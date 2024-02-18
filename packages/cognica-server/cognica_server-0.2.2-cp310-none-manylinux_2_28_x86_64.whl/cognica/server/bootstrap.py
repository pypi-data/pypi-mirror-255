#
# Cognica
#
# Copyright (c) 2023-2024 Cognica, Inc.
#

# pylint: disable=missing-module-docstring,missing-function-docstring
# pylint: disable=unused-argument,import-outside-toplevel

from __future__ import annotations

import os
import pathlib
import sys


# Add Cognica root path to package search paths.
paths = [
    # Convert `$COGNICA_HOME/module/python/cognica/server/bootstrap.py` to
    # `$COGNICA_HOME/module/python`, which is the root directory of the Python
    # module.
    pathlib.Path(__file__).parent.parent.parent.absolute(),
]
for path in reversed(paths):
    if path in sys.path:
        continue
    sys.path.insert(0, path.as_posix())


# Set start method to `spawn` on macOS and Linux as the mode `fork` is not safe
# and can be expensive with embedded Python in the multithreaded environment,
# especially with OpenMP. Some packages in Cognica uses OpenMP internally. Also,
# packages like `transformers` use the `multiprocessing` module to accelerate
# their computation speed. This combination potentially causes unexpected issues
# such as random crashes and deadlock without this setting.
if __name__ == "__main__" and sys.platform in {"darwin", "linux"}:
    import multiprocessing as mp

    mp.set_start_method("spawn")
    mp.freeze_support()
    del mp


# Explicitly disable parallelism for the `transformers` package to suppress
# verbose log messages.
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# Replace some built-in functions to mitigate the security vulnerabilities.
def __safe_input(prompt: object = "") -> str | None:
    from cognica.server.permission.user import get_user

    user = get_user()
    if user is None or user != "root":
        raise RuntimeError("'input()' is not allowed in the computational environment.")

    hooks = (
        __builtins__.get("__hooks__")
        if isinstance(__builtins__, dict)
        else getattr(__builtins__, "__hooks__")
    )
    return hooks["input"](prompt)  # type: ignore


def __safe_print(*args: object, **kwargs: object) -> None:
    from cognica.server.permission.user import get_user

    user = get_user()
    if user is None or user != "root":
        raise RuntimeError("'print()' is not allowed in the computational environment.")

    hooks = (
        __builtins__.get("__hooks__")
        if isinstance(__builtins__, dict)
        else getattr(__builtins__, "__hooks__")
    )
    hooks["print"](*args, **kwargs)  # type: ignore


if isinstance(__builtins__, dict):
    __builtins__["__hooks__"] = {  # type: ignore
        "input": __builtins__["input"],
        "print": __builtins__["print"],
    }
    __builtins__["input"] = __safe_input  # type: ignore
    __builtins__["print"] = __safe_print  # type: ignore
else:
    __builtins__.__hooks__ = {  # type: ignore
        "input": __builtins__.input,
        "print": __builtins__.print,
    }
    __builtins__.input = __safe_input  # type: ignore
    __builtins__.print = __safe_print  # type: ignore

del sys
del pathlib
del os
