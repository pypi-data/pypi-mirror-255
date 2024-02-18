from typing import Callable
from typing import Optional

from nn_interface.data import DataManager
from nn_interface.pipeline import Pipeline


class DataProcessor:
    """Applies pipeline to data from DataManager."""

    def __init__(self, pipeline: Pipeline):
        self._pipeline = pipeline

    def process(
        self,
        data_manager: DataManager,
        progress_callback: Optional[Callable[..., None]] = None,
    ) -> None:
        """
        Process data from DataManager.

        Parameters
        ----------
        data_manager : DataManager
            DataManager.
        progress_callback : Optional[Callable[..., None]]
            Called after every pipeline call, first argument is current item index in DataManager.

        """
        for idx in range(len(data_manager)):
            data_manager.save(idx, self._pipeline(data_manager.load(idx)))

            if progress_callback is not None:
                progress_callback(idx)
