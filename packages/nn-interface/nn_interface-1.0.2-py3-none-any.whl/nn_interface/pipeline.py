from typing import Any
from typing import List

from nn_interface import LOGGER
from nn_interface.io import IOProcessor
from nn_interface.nn import NeuralNetwork
from nn_interface.type import Tensors
from nn_interface.utils import timer


class Pipeline:
    """
    Generic pipeline.

    Call sequence:
    - ``io_processor.process_input``
    - ``nn.infer`` (for all neural networks)
    - ``io_processor.process_output``
    """

    def __init__(
        self,
        io_processor: IOProcessor,
        networks: List[NeuralNetwork],
    ):
        """
        Parameters
        ----------
        io_processor : IOProcessor
            IOProcessor for handling input data and output of neural networks.
        networks : List[NeuralNetwork]
            Neural networks.

        """
        self._io_processor = io_processor
        self._networks = networks

    @timer(LOGGER)
    def process(self, x: Any) -> Any:
        """Process data with the pipeline (alias: ``__call__``)."""
        # unwrap, process, wrap
        return self._io_processor.process_output(self._nn_process(self._io_processor.process_input(x)))

    def __call__(self, x: Any) -> Any:
        return self.process(x)

    def _nn_process(self, x: Tensors) -> Tensors:
        for network in self._networks:
            x = network(x)
        return x
