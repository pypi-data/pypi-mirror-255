from abc import ABC
from abc import abstractmethod
from typing import Any

from nn_interface import LOGGER
from nn_interface.type import Tensors
from nn_interface.utils import timer


class IOProcessor(ABC):
    """
    Input/Output processor.

    To create your own neural network, implement the following methods:
    - ``_process_input``
    - ``_process_output``
    """

    @timer(LOGGER)
    def process_input(self, x: Any) -> Tensors:
        """
        Input processor: accepts anything, returns a tensor.

        Parameters
        ----------
        x : Any
            Anything, for example image path.

        Returns
        -------
        Tensors
            Tensors for neural network processing.

        """
        return self._process_input(x)

    @timer(LOGGER)
    def process_output(self, x: Tensors) -> Any:
        """
        Output processor: accepts tensors, returns anything.

        Parameters
        ----------
        x : Tensors
            Output of a neural network.

        Returns
        -------
        Any
            Anything, for example image.

        """
        return self._process_output(x)

    @abstractmethod
    def _process_input(self, x: Any) -> Tensors:
        """Input processing implementation."""

    @abstractmethod
    def _process_output(self, x: Tensors) -> Any:
        """Output processing implementation."""
