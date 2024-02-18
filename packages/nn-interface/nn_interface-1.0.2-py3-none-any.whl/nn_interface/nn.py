from abc import ABC
from abc import abstractmethod

from nn_interface import LOGGER
from nn_interface.type import Tensors
from nn_interface.utils import timer


class NeuralNetwork(ABC):
    """
    Neural network interface.

    To create your own neural network, implement the following methods:
    - ``_preprocess``
    - ``_process``
    - ``_postprocess``
    """

    @timer(LOGGER)
    def infer(self, x: Tensors) -> Tensors:
        """Neural network inference (alias: ``__call__``)."""
        return self._postprocess(self._process(self._preprocess(x)))

    def __call__(self, x: Tensors) -> Tensors:
        return self.infer(x)

    @timer(LOGGER)
    def preprocess(self, x: Tensors) -> Tensors:
        """Preprocessing: prepare data for inference (process)."""
        return self._preprocess(x)

    @timer(LOGGER)
    def process(self, x: Tensors) -> Tensors:
        """Inference."""
        return self._process(x)

    @timer(LOGGER)
    def postprocess(self, x: Tensors) -> Tensors:
        """Postprocessing: handle data after inference."""
        return self._postprocess(x)

    @abstractmethod
    def _preprocess(self, x: Tensors) -> Tensors:
        """Preprocessing implementation."""

    @abstractmethod
    def _process(self, x: Tensors) -> Tensors:
        """Processing implementation."""

    @abstractmethod
    def _postprocess(self, x: Tensors) -> Tensors:
        """Postprocessing implementation"""
