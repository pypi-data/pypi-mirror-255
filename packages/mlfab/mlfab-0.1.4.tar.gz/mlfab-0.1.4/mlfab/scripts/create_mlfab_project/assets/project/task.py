"""Trains a simple convolutional neural network on the MNIST dataset.

Run this example with `python -m [[PROJECT NAME]].task`.
"""

from dataclasses import dataclass

import torch.nn.functional as F
from dpshdl.impl.mnist import MNIST
from torch import Tensor, nn
from torch.optim.optimizer import Optimizer

import mlfab


@dataclass
class Config(mlfab.Config):
    in_dim: int = mlfab.field(1, help="Number of input dimensions")


class MnistClassification(mlfab.Task[Config]):
    def __init__(self, config: Config) -> None:
        super().__init__(config)

        self.model = nn.Sequential(
            nn.Conv2d(config.in_dim, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, 10),
        )

    def get_dataset(self, phase: mlfab.Phase) -> MNIST:
        root_dir = mlfab.get_data_dir() / "mnist"
        return MNIST(root_dir=root_dir, train=phase == "train")

    def build_optimizer(self) -> Optimizer:
        return mlfab.Adam.get(self, lr=1e-3)

    def forward(self, x: Tensor) -> Tensor:
        return self.model(x)

    def get_loss(self, batch: tuple[Tensor, Tensor], state: mlfab.State) -> Tensor:
        x, y = batch
        yhat = self(x)
        self.log_step(batch, yhat, state)
        return F.cross_entropy(yhat, y.squeeze(-1).long())

    def log_valid_step(self, batch: tuple[Tensor, Tensor], output: Tensor, state: mlfab.State) -> None:
        (x, y), yhat = batch, output

        def get_label_strings() -> list[str]:
            ytrue, ypred = y.squeeze(-1), yhat.argmax(-1)
            return [f"ytrue={ytrue[i]}, ypred={ypred[i]}" for i in range(len(ytrue))]

        self.log_labeled_images("images", lambda: (x, get_label_strings()))


if __name__ == "__main__":
    MnistClassification.launch(Config(batch_size=16))
