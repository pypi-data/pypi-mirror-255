"""
"""
from __future__ import annotations

from contextlib import contextmanager
from types import ModuleType

from ..config import Config


def maybe_import_torch():
    if not Config.zero_gpu:
        return None
    try:
        import torch
    except ImportError:
        return None
    return torch


@contextmanager
def cuda_unavailable(torch: ModuleType):
    _is_available = torch.cuda.is_available
    torch.cuda.is_available = lambda: False
    yield
    torch.cuda.is_available = _is_available


def maybe_import_bitsandbytes():
    if (torch := maybe_import_torch()) is None:
        return None # pragma: no cover
    with cuda_unavailable(torch):
        try:
            import bitsandbytes
        except ImportError:
            bitsandbytes = None
        else:
            print("↑ Those bitsandbytes warnings are expected on ZeroGPU ↑")
    return bitsandbytes
