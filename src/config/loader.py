from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ProjectConfig:
    """Top-level project configuration."""

    name: str
    version: str
    environment: str


@dataclass(frozen=True)
class LoggingConfig:
    """Logging-related configuration."""

    level: str
    log_to_file: bool
    log_dir: str
    log_filename: str


@dataclass(frozen=True)
class AMMConfig:
    """Default AMM configuration used for initialization and examples."""

    default_fee_rate: float
    default_token_x: str
    default_token_y: str
    default_reserve_x: float
    default_reserve_y: float


@dataclass(frozen=True)
class AppConfig:
    """Aggregate application configuration object."""

    project: ProjectConfig
    logging: LoggingConfig
    amm: AMMConfig


def _read_yaml(path: Path) -> dict[str, Any]:
    """Read and parse a YAML file into a dictionary.

    Args:
        path: Filesystem path to the YAML file.

    Returns:
        Parsed YAML content as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML content is empty or invalid.
    """
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML structure in config file: {path}")

    return data


def load_config(config_path: str | Path = "configs/base.yaml") -> AppConfig:
    """Load application configuration from YAML.

    Args:
        config_path: Relative or absolute path to the YAML config file.

    Returns:
        AppConfig object containing typed configuration sections.
    """
    path = Path(config_path)
    raw = _read_yaml(path)

    project_raw = raw["project"]
    logging_raw = raw["logging"]
    amm_raw = raw["amm"]

    return AppConfig(
        project=ProjectConfig(
            name=project_raw["name"],
            version=project_raw["version"],
            environment=project_raw["environment"],
        ),
        logging=LoggingConfig(
            level=logging_raw["level"],
            log_to_file=logging_raw["log_to_file"],
            log_dir=logging_raw["log_dir"],
            log_filename=logging_raw["log_filename"],
        ),
        amm=AMMConfig(
            default_fee_rate=float(amm_raw["default_fee_rate"]),
            default_token_x=amm_raw["default_token_x"],
            default_token_y=amm_raw["default_token_y"],
            default_reserve_x=float(amm_raw["default_reserve_x"]),
            default_reserve_y=float(amm_raw["default_reserve_y"]),
        ),
    )