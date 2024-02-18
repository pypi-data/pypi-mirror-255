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

import pathlib
import sys

import numpy as np
import torch

from sentence_transformers import SentenceTransformer

from cognica.server.permission.user import impersonate


class SentenceTransformerEncoder:
    def __init__(self, filename: str):
        self._model = SentenceTransformer(filename, cache_folder="data/models/.cache")
        if sys.version_info < (3, 12):
            try:
                self._model = torch.compile(self._model)
            except Exception:
                with impersonate("root"):
                    model_name = pathlib.Path(filename).stem
                    print(
                        "Warning: Failed to compile model for TorchScript."
                        f" Model: {model_name}"
                    )

    def encode(
        self, input: str | list[str]
    ) -> list[torch.Tensor] | np.ndarray | torch.Tensor:
        return self._model.encode(input)
