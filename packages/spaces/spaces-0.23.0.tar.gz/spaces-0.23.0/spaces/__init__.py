"""
"""

import sys

if sys.version_info.minor < 8: # pragma: no cover
    raise RuntimeError("Importing PySpaces requires Python 3.8+")


from .zero.decorator import GPU
from .zero.torch import disable_cuda_intercept
from .gradio import gradio_auto_wrap
from .gradio import disable_gradio_auto_wrap
from .gradio import enable_gradio_auto_wrap


__all__ = [
    'GPU',
    'disable_cuda_intercept',
    'gradio_auto_wrap',
    'disable_gradio_auto_wrap',
    'enable_gradio_auto_wrap',
]
