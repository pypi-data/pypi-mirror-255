#!/usr/bin/env python3
"""Run a Pod from a yaml config file."""
import logging
import os
from os import PathLike
from typing import Union

import fire

from bitfount import config
from bitfount.runners.pod_runner import setup_pod_from_config_file
from bitfount.runners.utils import setup_loggers
from bitfount.utils.logging_utils import log_pytorch_env_info_if_available

log_level = os.getenv("BITFOUNT_LOG_LEVEL", logging.INFO)

config._BITFOUNT_CLI_MODE = True


def run(path_to_config_yaml: Union[str, PathLike]) -> None:
    """Runs a pod from a config file.

    Args:
        path_to_config_yaml: Path to the config YAML file.
    """
    setup_loggers([logging.getLogger("bitfount")], log_level=log_level)
    log_pytorch_env_info_if_available()

    pod = setup_pod_from_config_file(path_to_config_yaml)
    pod.start()


if __name__ == "__main__":
    fire.Fire(run)
