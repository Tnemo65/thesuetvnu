"""Config loading helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from dqbench.contracts.runs import RunSpec


def load_yaml(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML config at {path} must decode to a mapping")
    return data


def dump_yaml(path: str | Path, data: Dict[str, Any]) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


def load_run_spec(path: str | Path) -> RunSpec:
    data = load_yaml(path)
    run_spec_data = data.get("run_spec", data)
    return RunSpec.from_dict(run_spec_data)
