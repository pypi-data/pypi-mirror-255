"""Utility functions for the explore module."""
import pathlib
from typing import Optional

import yaml
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from explore.constants import DVC_OUTS_KEY


def get_path_last_part(list_of_full_path: list[pathlib.Path]) -> list[str]:
    """Returns a list with the last part of the path for each path in the list."""
    list_of_last_part = [path.parts[-1] for path in list_of_full_path]
    return list_of_last_part


class DVCStep(BaseModel):
    """Data model representing a DVC step."""

    name: str
    output_path: Optional[pathlib.Path]


def parse_dvc_steps_from_dvc_yaml() -> list[DVCStep]:
    """Parse the DVC steps from the dvc.yaml file."""
    with open("dvc.yaml", "r", encoding="utf-8") as f:
        dvc_yaml = yaml.safe_load(f)

    stages_dict = dvc_yaml["stages"]
    steps = []
    for stage_name, stage_content in stages_dict.items():
        if DVC_OUTS_KEY in stage_content:
            output_path = stage_content[DVC_OUTS_KEY][0]
        else:
            output_path = None

        steps.append(DVCStep(name=stage_name, output_path=output_path))
    return steps
