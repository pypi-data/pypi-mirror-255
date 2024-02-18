#
# Cognica
#
# Copyright (c) 2023 Cognica, Inc.
#

# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

import argparse
import yaml
import shutil
from pathlib import Path

from cognica import server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--data",
        type=str,
        help="Where to store the data.",
        required=False,
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Where the settings file will be saved.",
        default="./conf",
        required=False,
    )
    args = parser.parse_args()
    app_root = str(server.__path__[0]) / Path("usr")

    default_config = app_root / "conf/default.yaml"
    config_path = Path(args.config)
    config_path.mkdir(exist_ok=True, parents=True)
    config_file = config_path / default_config.name
    if not args.data:
        shutil.copy(default_config, config_file)
        data_path = Path("./data")
    else:
        data_path = Path(args.data)
        with default_config.open() as f:
            config = yaml.load(f, Loader=yaml.Loader)
        config["db"]["storage"]["db_path"] = str(data_path.absolute())
        with config_file.open("w") as f:
            output = yaml.dump(config, Dumper=yaml.Dumper)
            f.write(output)
    data_path.mkdir(exist_ok=True, parents=True)

    print("The initial setup of Cognica is now complete.")
    print(f"Default Config File: {config_file}")
    print(f"Data Path: {data_path}")
