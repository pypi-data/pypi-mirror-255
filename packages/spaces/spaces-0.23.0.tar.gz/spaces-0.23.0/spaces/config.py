"""
"""
from __future__ import annotations

import os

from .utils import boolean


class Settings:
    def __init__(self):
        self.zero_gpu = boolean(
            os.getenv('SPACES_ZERO_GPU'))
        self.zero_device_api_url = (
            os.getenv('SPACES_ZERO_DEVICE_API_URL'))
        self.gradio_auto_wrap = boolean(
            os.getenv('SPACES_GRADIO_AUTO_WRAP'))
        self.zero_patch_torch_device = boolean(
            os.getenv('ZERO_GPU_PATCH_TORCH_DEVICE'))


Config = Settings()


if Config.zero_gpu:
    assert Config.zero_device_api_url is not None, (
        'SPACES_ZERO_DEVICE_API_URL env must be set '
        'on ZeroGPU Spaces (identified by SPACES_ZERO_GPU=true)'
    )
