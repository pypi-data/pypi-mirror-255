from typing import List

import os

from dataclasses import dataclass


@dataclass
class Config:
    name: str
    description: str


def require_config(config: Config) -> str:
    env_name = config.name
    if env_name not in os.environ:
        raise Exception(
            f"Config '{env_name}' is not defined as an environment variable."
        )
    return os.environ[env_name]
