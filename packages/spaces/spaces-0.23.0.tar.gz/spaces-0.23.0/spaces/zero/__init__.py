"""
"""

from ..config import Config
from . import torch

if Config.zero_gpu:
    if torch.is_in_bad_fork():
        raise RuntimeError(
            "CUDA has been initialized before importing the `spaces` package"
        )
    torch.patch() # pragma: no cover
