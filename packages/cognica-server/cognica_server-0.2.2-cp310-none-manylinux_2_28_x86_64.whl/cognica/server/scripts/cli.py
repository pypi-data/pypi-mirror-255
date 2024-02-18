#
# Cognica
#
# Copyright (c) 2023 Cognica, Inc.
#

# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

import os
import subprocess
import sys
import sysconfig

from cognica.server import bootstrap

from cognica import server


def main():
    app_root = str(server.__path__[0]) + "/usr"
    version = sysconfig.get_python_version()

    cognica_path = app_root + "/bin/cognica"
    env = os.environ.copy()
    env["PYTHONHOME"] = sysconfig.get_config_vars("base")[0]
    env["PYTHONPATH"] = (
        f"{app_root}/lib/python{version}:"
        f"{app_root}/lib/python{version}/lib-dynload"
    )
    env["COGNICA_MECAB_RC_PATH"] = f"{app_root}/etc/mecabrc"
    env["COGNICA_MECAB_DICT_PATH"] = f"{app_root}/lib/mecab/dic/mecab-ko-dic"
    env["COGNICA_PYTHON_BOOTSTRAP_PATH"] = bootstrap.__file__

    try:
        subprocess.call([cognica_path] + sys.argv[1:], env=env)
    except KeyboardInterrupt:
        pass
