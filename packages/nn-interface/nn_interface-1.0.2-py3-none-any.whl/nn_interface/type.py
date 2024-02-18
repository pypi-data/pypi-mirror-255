from typing import Tuple
from typing import Union

import numpy as np
import torch

Tensors = Union[torch.Tensor, np.ndarray, Tuple[Union[torch.Tensor, np.ndarray], ...]]
