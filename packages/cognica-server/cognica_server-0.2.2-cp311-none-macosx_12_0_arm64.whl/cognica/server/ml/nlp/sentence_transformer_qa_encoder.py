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
import typing as t

import torch
from transformers import pipeline

from cognica.server.permission.user import impersonate


class SentenceTransformerQAOutput(t.NamedTuple):
    score: float
    begin: int
    end: int
    answer: str


class SentenceTransformerQAEncoder:
    def __init__(self, filename: str):
        self._model = pipeline(
            task="question-answering",
            model=filename,
            tokenizer=filename,
            model_kwargs={"cache_dir": "data/models/.cache"},
        )
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

    def predict(
        self,
        questions: str | list[str],
        contexts: str | list[str],
        top_k: int = 1,
    ) -> list[list[SentenceTransformerQAOutput]] | None:
        if not isinstance(questions, list):
            questions = [questions]
        if not isinstance(contexts, list):
            contexts = [contexts]

        if len(questions) != len(contexts):
            return None

        inputs = {
            "question": questions,
            "context": contexts,
        }
        output_answers: t.Any = self._model(inputs, top_k=top_k)
        if len(questions) == 1 and top_k == 1:
            output_answers = [output_answers]
        elif top_k == 1:
            output_answers = [[output] for output in output_answers]

        outputs: list[list[SentenceTransformerQAOutput]] = []
        for answers in output_answers:
            converted_answers: list[SentenceTransformerQAOutput] = []
            for answer in answers:
                output = SentenceTransformerQAOutput(
                    score=answer.get("score"),
                    begin=answer.get("start"),
                    end=answer.get("end"),
                    answer=answer.get("answer"),
                )
                converted_answers.append(output)
            outputs.append(converted_answers)

        return outputs
