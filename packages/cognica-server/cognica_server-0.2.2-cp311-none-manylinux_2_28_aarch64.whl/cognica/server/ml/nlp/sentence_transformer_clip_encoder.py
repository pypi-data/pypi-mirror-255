#
# Cognica
#
# Copyright (c) 2023-2024 Cognica, Inc.
#

# pylint: disable=missing-module-docstring,missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-builtin,broad-exception-caught
# pylint: disable=too-few-public-methods

from __future__ import annotations

import io
import pathlib
import sys

import numpy as np

import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

from cognica.server.permission.user import impersonate


class SentenceTransformerCLIPEncoder:
    def __init__(self, filename: str):
        cache_dir = "data/models/.cache"
        self._model = CLIPModel.from_pretrained(filename, cache_dir=cache_dir)
        self._processor = CLIPProcessor.from_pretrained(filename, cache_dir=cache_dir)
        if sys.version_info < (3, 12):
            try:
                self._model = torch.compile(self._model)  # type: ignore
            except Exception:
                with impersonate("root"):
                    model_name = pathlib.Path(filename).stem
                    print(
                        "Warning: Failed to compile model for TorchScript."
                        f" Model: {model_name}"
                    )

    def encode(self, input: bytes | list[bytes]) -> np.ndarray:
        if not isinstance(input, list):
            input = [input]

        images: list[Image.Image] = []
        for buffer in input:
            image = Image.open(io.BytesIO(buffer))
            images.append(image)

        inputs = self._processor(images=images, return_tensors="pt")
        outputs = self._model.get_image_features(**inputs)  # type: ignore

        return outputs.detach().numpy()
