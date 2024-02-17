""" Helper classes and functions for the SSL model """

import torch
import torch.nn as nn
import numpy as np
import random
from pathlib import Path
from transforms3d.axangles import axangle2mat
from tqdm import tqdm
from torchvision import transforms
from torch.utils.data.dataset import Dataset

SAMPLE_RATE = 30  # Sample rate for SSL Resnet18 model fixed to 30Hz
verbose = True
torch_cache_path = Path(__file__).parent / "torch_hub_cache"

torch.multiprocessing.set_sharing_strategy("file_system")


class RandomSwitchAxis:
    """
    Randomly switch the three axises for the raw files
    Input size: 3 * FEATURE_SIZE
    """

    def __call__(self, sample):
        # 3 * FEATURE
        x = sample[0, :]
        y = sample[1, :]
        z = sample[2, :]

        choice = random.randint(1, 6)

        if choice == 1:
            sample = torch.stack([x, y, z], dim=0)
        elif choice == 2:
            sample = torch.stack([x, z, y], dim=0)
        elif choice == 3:
            sample = torch.stack([y, x, z], dim=0)
        elif choice == 4:
            sample = torch.stack([y, z, x], dim=0)
        elif choice == 5:
            sample = torch.stack([z, x, y], dim=0)
        elif choice == 6:
            sample = torch.stack([z, y, x], dim=0)

        return sample


class RotationAxis:
    """
    Rotation along an axis
    """

    def __call__(self, sample):
        # 3 * FEATURE_SIZE
        sample = np.swapaxes(sample, 0, 1)
        angle = np.random.uniform(low=-np.pi, high=np.pi)
        axis = np.random.uniform(low=-1, high=1, size=sample.shape[1])
        sample = np.matmul(sample, axangle2mat(axis, angle))
        sample = np.swapaxes(sample, 0, 1)
        return sample


class NormalDataset(Dataset):
    def __init__(
        self, X, y=None, pid=None, augmentation=False, transpose_channels_first=True
    ):

        X = X.astype("f4")  # PyTorch defaults to float32

        if transpose_channels_first:
            X = np.transpose(X, (0, 2, 1))
        self.X = torch.from_numpy(X)

        if y is not None:
            self.y = torch.tensor(y)
        else:
            self.y = None

        self.pid = pid

        if augmentation:
            self.transform = transforms.Compose([RandomSwitchAxis(), RotationAxis()])
        else:
            self.transform = None

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        sample = self.X[idx, :]

        if self.y is not None:
            y = self.y[idx]
        else:
            y = np.NaN

        if self.pid is not None:
            pid = self.pid[idx]
        else:
            pid = np.NaN

        if self.transform is not None:
            sample = self.transform(sample)

        return sample, y, pid


class EarlyStopping:
    """Early stops the training if validation loss
    doesn't improve after a given patience."""

    def __init__(
        self,
        patience=5,
        verbose=False,
        delta=0,
        path="checkpoint.pt",
        trace_func=print,
    ):
        """
        Args:
            patience (int): How long to wait after last time v
                            alidation loss improved.
                            Default: 7
            verbose (bool): If True, prints a message for each
                            validation loss improvement.
                            Default: False
            delta (float): Minimum change in the monitored quantity
                            to qualify as an improvement.
                            Default: 0
            path (str): Path for the checkpoint to be saved to.
                            Default: 'checkpoint.pt'
            trace_func (function): trace print function.
                            Default: print
        """
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.delta = delta
        self.trace_func = trace_func

        self.path = path

    def __call__(self, val_loss, model):

        score = -val_loss

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        elif score < self.best_score + self.delta:
            self.counter += 1
            if self.verbose:
                self.trace_func(
                    f"EarlyStopping counter: {self.counter}/{self.patience}"
                )
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        """Saves model when validation loss decrease."""
        if self.verbose:
            msg = "Validation loss decreased"
            msg = msg + f" ({self.val_loss_min:.6f} --> {val_loss:.6f}). "
            msg = msg + "Saving model ..."
            self.trace_func(msg)
        if hasattr(model, "module"):
            torch.save(model.module.state_dict(), self.path)
        else:
            torch.save(model.state_dict(), self.path)
        self.val_loss_min = val_loss


def get_sslnet(
    device,
    tag="v1.0.0",
    local_repo_path=None,
    pretrained=False,
    window_sec: int = 30,
    num_labels: int = 4,
):
    """
    Load and return the Self Supervised Learning (SSL) model from pytorch hub or local storage.

    :param str device: PyTorch device to use
    :param str tag: Tag on the ssl-wearables repo to check out
    :param str local_repo_path: Path to local version of the SSL repo for offline usage
    :param bool/str pretrained: Initialise the model with UKB self-supervised pretrained weights
    :param int window_sec: The length of the window of data in seconds (limited to 5, 10 or 30)
    :param int num_labels: The number of labels to predict
    :return: pytorch SSL model
    :rtype: nn.Module
    """

    if window_sec not in [5, 10, 30]:
        raise ValueError(
            "Length of window in seconds must be either 5, 10 or 30 seconds"
        )

    if num_labels < 1:
        raise ValueError("Numer of class labels should be > 0")

    if local_repo_path is not None:
        sslnet: nn.Module = torch.hub.load(
            local_repo_path,
            f"harnet{window_sec}",
            source="local",
            class_num=num_labels,
            pretrained=pretrained == True,
        )

    else:
        repo_name = "ssl-wearables"
        repo = f"OxWearables/{repo_name}:{tag}"

        if not torch_cache_path.exists():
            Path.mkdir(torch_cache_path, parents=True, exist_ok=True)

        torch.hub.set_dir(str(torch_cache_path))

        # find repo cache dir that matches repo name and tag
        cache_dirs = [f for f in torch_cache_path.iterdir() if f.is_dir()]
        repo_path = next(
            (f for f in cache_dirs if repo_name in f.name and tag in f.name), None
        )

        if repo_path is None:
            repo_path = repo
            source = "github"
        else:
            repo_path = str(repo_path)
            source = "local"
            if verbose:
                print(f"Using local {repo_path}")

        sslnet: nn.Module = torch.hub.load(
            repo_path,
            f"harnet{window_sec}",
            trust_repo=True,
            source=source,
            class_num=num_labels,
            pretrained=pretrained == True,
            verbose=verbose,
        )

    model_dict = torch.load(pretrained, map_location=device)
    sslnet.load_state_dict(model_dict)

    return sslnet


def predict(model, dataloader, device, output_logits=False):
    """
    Iterate over the dataloader and do prediction with a pytorch model.

    :param nn.Module model: pytorch Module
    :param DataLoader data_loader: pytorch dataloader
    :param str device: pytorch map device
    :param bool output_logits: When True, output the raw outputs (logits) from the last layer (before classification).
                                When False, argmax the logits and output a classification scalar.
    :return: true labels, model predictions, pids
    :rtype: (np.ndarray, np.ndarray, np.ndarray)
    """

    if verbose:
        print("Classifying windows...")

    predictions_list = []
    true_list = []
    pid_list = []
    model.eval()

    if len(dataloader) == 0:
        return np.array([]), np.array([]), np.array([])

    with torch.inference_mode():
        for x, y, pid in tqdm(dataloader, mininterval=5, disable=not verbose):
            x = x.to(device, dtype=torch.float)
            logits = model(x)
            true_list.append(y)
            if output_logits:
                predictions_list.append(logits.cpu())
            else:
                pred_y = torch.argmax(logits, dim=1)
                predictions_list.append(pred_y.cpu())
            pid_list.extend(pid)

    true_list = torch.cat(true_list)
    predictions_list = torch.cat(predictions_list)

    if output_logits:
        return (
            torch.flatten(true_list).numpy(),
            predictions_list.numpy(),
            np.array(pid_list),
        )
    else:
        return (
            torch.flatten(true_list).numpy(),
            torch.flatten(predictions_list).numpy(),
            np.array(pid_list),
        )
