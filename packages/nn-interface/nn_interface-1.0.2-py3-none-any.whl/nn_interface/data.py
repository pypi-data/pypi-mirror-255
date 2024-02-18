# pylint: disable=unnecessary-ellipsis
from typing import Protocol

from nn_interface.type import Tensors


class DataManager(Protocol):
    """Interface for data-managers classes, like dataloader."""

    def load(self, idx: int) -> Tensors:
        """Return item by index."""
        ...

    def save(self, idx: int, result: Tensors) -> None:
        """Save item by index."""
        ...

    def __len__(self) -> int:
        ...
