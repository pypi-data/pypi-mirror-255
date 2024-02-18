"""
"""
from __future__ import annotations

import time
import warnings
from datetime import timedelta

import gradio as gr
import httpx

from .. import utils
from ..config import Config
from .api import APIClient
from .api import QuotaInfos
from .api import ScheduleResponse
from .gradio import get_event


TOKEN_HEADER = 'X-IP-Token'
DEFAULT_SCHEDULE_DURATION = 60

QUOTA_MESSAGE = "You have exceeded your GPU quota"
UNUSED_MESSAGE = "GPU device not used"
NO_GPU_MESSAGE_REGULAR = "No GPU is currently available"
NO_GPU_MESSAGE_INQUEUE = "No GPU is currently available for you after 60s"


def api_client():
    assert Config.zero_device_api_url is not None
    httpx_client = httpx.Client(base_url=Config.zero_device_api_url, timeout=60, verify=False)
    return APIClient(httpx_client)


def startup_report():
    retries, max_retries = 0, 2
    client = api_client()
    while (status := client.startup_report()) is httpx.codes.NOT_FOUND: # pragma: no cover
        time.sleep(1)
        if (retries := retries + 1) > max_retries:
            raise RuntimeError("Error while initializing ZeroGPU: NotFound")
    if status is not httpx.codes.OK: # pragma: no cover
        raise RuntimeError("Error while initializing ZeroGPU: Unknown")


def schedule(
    task_id: int,
    request: gr.Request | None = None,
    duration: timedelta | None = None,
    _first_attempt: bool = True,
) -> ScheduleResponse:

    if not gr.__version__.startswith('4.'): # pragma: no cover
        raise RuntimeError("ZeroGPU is only compatible with Gradio 4+")

    res = api_client().schedule(
        cgroup_path=utils.self_cgroup_device_path(),
        task_id=task_id,
        token=_get_token(request),
        duration_seconds=duration.seconds if duration is not None else None,
    )

    if isinstance(res, ScheduleResponse):
        return res

    if isinstance(res, QuotaInfos): # pragma: no cover
        requested = duration.seconds if duration is not None else DEFAULT_SCHEDULE_DURATION
        if res.wait < timedelta(0):
            message = (
                f"The requested GPU duration ({requested}s) "
                f"is larger than the maximum allowed"
            )
        else:
            message = (
                f"You have exceeded your GPU quota "
                f"({res.left}s left vs. {requested}s requested). "
                f"Please retry in {res.wait}"
            )
        raise gr.Error(message)

    if not isinstance(res, httpx.codes): # pragma: no cover
        gr.Info("Waiting for a GPU to become available")
        connection_event = get_event()
        if connection_event is None and request is not None:
            warnings.warn("ZeroGPU: Cannot get Gradio app Queue instance")
        while True:
            try:
                event = next(res)
            except StopIteration:
                raise RuntimeError("Unexpected end of stream")
            except httpx.RemoteProtocolError:
                if not _first_attempt:
                    raise RuntimeError("Error while re-trying after queue disconnect")
                return schedule(task_id, request, duration, _first_attempt=False)
            if event.event == 'ping':
                if connection_event is not None and not connection_event.alive:
                    res.close()
                    raise RuntimeError("Connection closed by visitor while queueing")
                continue
            if event.event == 'failed':
                raise gr.Error(NO_GPU_MESSAGE_INQUEUE)
            if event.event == 'succeeded':
                assert event.data is not None
                if connection_event is not None and not connection_event.alive:
                    release(task_id, event.data.nvidiaIndex)
                    raise RuntimeError("Connection closed by visitor on queue success")
                gr.Info("Successfully acquired a GPU")
                return event.data

    if res is httpx.codes.SERVICE_UNAVAILABLE:
        raise gr.Error(NO_GPU_MESSAGE_REGULAR)

    # TODO: Find a way to log 'detail' response field
    raise RuntimeError(f"ZeroGPU API /schedule error: {res} ({httpx.codes.get_reason_phrase(res)})") # pragma: no cover


def release(
    task_id: int,
    nvidia_index: int,
    fail: bool = False,
    allow_404: bool = False,
) -> None:

    res = api_client().release(
        cgroup_path=utils.self_cgroup_device_path(),
        task_id=task_id,
        nvidia_index=nvidia_index,
        fail=fail,
    )

    if res is httpx.codes.NO_CONTENT: # pragma: no cover
        try:
            gr.Warning(UNUSED_MESSAGE)
        except AttributeError:
            pass
        warnings.warn(UNUSED_MESSAGE, RuntimeWarning)
        return None

    if allow_404 and res is httpx.codes.NOT_FOUND:
        return None

    if httpx.codes.is_success(res):
        return None

    # TODO: Find a way to log 'detail' response field
    # TODO: Only raise in dev environment. Simply warn in production ?
    raise RuntimeError(f"ZeroGPU API /release error: {res} ({httpx.codes.get_reason_phrase(res)})")


def _get_token(request: gr.Request | None) -> str | None:

    if request is None:
        return None

    headers = getattr(request, 'headers', None)
    if headers is None or not hasattr(headers, '__dict__'):
        raise gr.Error("Internal Gradio error")

    # Compatibility trick
    if not hasattr(headers, 'get'):
        headers = headers.__dict__ # pragma: no cover

    if not (token := headers.get(TOKEN_HEADER.lower())):
        raise gr.Error("Internal infra error")

    return token
