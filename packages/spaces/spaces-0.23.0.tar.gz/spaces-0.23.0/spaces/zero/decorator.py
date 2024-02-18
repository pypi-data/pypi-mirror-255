"""
"""
from __future__ import annotations

import inspect
import sys
import warnings
from datetime import timedelta
from functools import partial
from typing import Callable
from typing import TypeVar
from typing import overload
from typing_extensions import ParamSpec

import gradio as gr

from ..config import Config
from . import client
from .wrappers import regular_function_wrapper
from .wrappers import generator_function_wrapper


P = ParamSpec('P')
R = TypeVar('R')


decorated_cache: dict[Callable, Callable] = {}


@overload
def GPU(
    task: None = None, *,
    duration: int | timedelta | None = None,
    enable_queue: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...
@overload
def GPU(
    task: Callable[P, R], *,
    duration: int | timedelta | None = None,
    enable_queue: bool = True,
) -> Callable[P, R]:
    ...
def GPU(
    task: Callable[P, R] | None = None, *,
    duration: int | timedelta | None = None,
    enable_queue: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]] | Callable[P, R]:
    """
    ZeroGPU decorator

    Basic usage:
        ```
        @spaces.GPU
        def fn(...):
            # CUDA is available here
            pass
        ```

    With custom duration:
        ```
        @spaces.GPU(duration=45) # Expressed in seconds
        def fn(...):
            # CUDA is available here
            pass
        ```

    Args:
        task (`Callable | None`): Python function that requires CUDA
        duration (`int | datetime.timedelta`): Estimated duration in seconds or `datetime.timedelta`

    Returns:
        `Callable`: GPU-ready function
    """
    if task is None:
        return partial(_GPU, duration=duration, enable_queue=enable_queue)
    return _GPU(task, duration, enable_queue)


def _GPU(
    task: Callable[P, R],
    duration: int | timedelta | None,
    enable_queue: bool,
) -> Callable[P, R]:

    if not enable_queue:
        warnings.warn("`enable_queue` parameter is now ignored and always defaults to `True`")

    if not Config.zero_gpu:
        # TODO: still prepend gr.Request for type consistency ?
        return task # type: ignore

    if sys.version_info.minor < 9: # pragma: no cover
        raise RuntimeError("Actually using @spaces.GPU on a ZeroGPU Space requires Python 3.9+")

    if task in decorated_cache:
        # TODO: Assert same duration ?
        return decorated_cache[task] # type: ignore

    if inspect.iscoroutinefunction(task):
        raise NotImplementedError

    if duration is None or isinstance(duration, timedelta):
        timedelta_duration = duration
    else:
        timedelta_duration = timedelta(seconds=duration)

    if inspect.isgeneratorfunction(task):
        decorated = generator_function_wrapper(task, timedelta_duration)
    else:
        decorated = regular_function_wrapper(task, timedelta_duration)

    client.startup_report()
    decorated_cache.update({
        task:      decorated,
        decorated: decorated,
    })

    return decorated # type: ignore
