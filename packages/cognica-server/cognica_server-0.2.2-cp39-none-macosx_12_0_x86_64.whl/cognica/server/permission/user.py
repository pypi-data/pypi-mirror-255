#
# Cognica
#
# Copyright (c) 2023-2024 Cognica, Inc.
#

# pylint: disable=missing-module-docstring,missing-function-docstring

from __future__ import annotations

import contextlib


__user_stack: list[str] = []


@contextlib.contextmanager
def impersonate(user: str):
    __user_stack.append(user)

    yield user

    __user_stack.pop()


def get_user() -> str | None:
    if not __user_stack:
        return None

    return __user_stack[-1]
