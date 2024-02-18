#!/usr/bin/env python3
"""Run a task from a yaml config file."""
import logging
import os
from os import PathLike
from pathlib import Path
from typing import Union

import fire

from bitfount import config
from bitfount.runners.modeller_runner import (
    DEFAULT_MODEL_OUT,
    run_modeller,
    setup_modeller_from_config_file,
)
from bitfount.runners.utils import setup_loggers
from bitfount.utils.logging_utils import log_pytorch_env_info_if_available

log_level = os.getenv("BITFOUNT_LOG_LEVEL", logging.INFO)

config._BITFOUNT_CLI_MODE = True


def run(
    path_to_config_yaml: Union[str, PathLike],
    require_all_pods: bool = False,
    model_out: Path = DEFAULT_MODEL_OUT,
) -> None:
    """Runs a modeller from a config file.

    Args:
        path_to_config_yaml: Path to the config YAML file.
        require_all_pods: Whether to require all pods to accept the task before
            continuing.
        model_out: Path to save the model to (if applicable).
    """
    setup_loggers([logging.getLogger("bitfount")], log_level=log_level)
    log_pytorch_env_info_if_available()

    (
        modeller,
        pod_identifiers,
        project_id,
        run_on_new_datapoints,
        batched_execution,
    ) = setup_modeller_from_config_file(path_to_config_yaml)

    run_modeller(
        modeller,
        pod_identifiers,
        require_all_pods,
        model_out,
        project_id,
        run_on_new_datapoints,
        batched_execution,
    )


if __name__ == "__main__":
    fire.Fire(run)
