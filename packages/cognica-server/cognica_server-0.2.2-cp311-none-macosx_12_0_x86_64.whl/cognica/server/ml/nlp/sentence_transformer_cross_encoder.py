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

from sentence_transformers import CrossEncoder

from cognica.server.permission.user import impersonate


class SentenceTransformerCrossEncoder:
    def __init__(self, filename: str):
        tokenizer_args = {
            "cache_dir": "data/models/.cache",
        }
        automodel_args = {
            "cache_dir": "data/models/.cache",
        }
        self._model = CrossEncoder(
            filename,
            tokenizer_args=tokenizer_args,
            automodel_args=automodel_args,
        )
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

    def predict(
        self, inputs: list[list[str]]
    ) -> list[torch.Tensor] | np.ndarray | torch.Tensor:
        return self._model.predict(inputs)
