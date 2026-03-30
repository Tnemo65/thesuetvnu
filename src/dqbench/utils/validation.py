"""Small validation helpers used across contracts and config loading."""

from __future__ import annotations

from typing import Any, Iterable, Mapping


class ValidationError(ValueError):
    """Raised when a config or record fails schema validation."""


def require_keys(data: Mapping[str, Any], keys: Iterable[str], schema_name: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValidationError(f"{schema_name} missing required keys: {missing}")


def require_choice(name: str, value: Any, choices: Iterable[Any]) -> None:
    choices = tuple(choices)
    if value not in choices:
        raise ValidationError(f"{name} must be one of {choices}, got {value!r}")


def require_non_empty(name: str, value: Any) -> None:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{name} must be non-empty")


def require_non_negative_int(name: str, value: Any) -> None:
    if not isinstance(value, int) or value < 0:
        raise ValidationError(f"{name} must be a non-negative integer, got {value!r}")


def require_mapping(name: str, value: Any) -> None:
    if not isinstance(value, dict):
        raise ValidationError(f"{name} must be a mapping")


def require_ordered_bounds(start_name: str, start_value: str, end_name: str, end_value: str) -> None:
    if start_value > end_value:
        raise ValidationError(f"{start_name} must be <= {end_name}")
