"""Detector alert contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from dqbench.contracts.benchmark import (
    VALID_CALIBRATIONS,
    VALID_DETECTORS,
    VALID_DOMAINS,
    VALID_SCOPE_LEVELS,
)
from dqbench.utils.validation import require_choice, require_mapping, require_non_empty


@dataclass(frozen=True)
class AlertRecord:
    alert_id: str
    run_id: str
    detector: str
    domain: str
    batch_id: str
    scope_level: str
    scope_ref: str
    score: float
    calibration_policy: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        require_non_empty("alert_id", self.alert_id)
        require_non_empty("run_id", self.run_id)
        require_choice("detector", self.detector, VALID_DETECTORS)
        require_choice("domain", self.domain, VALID_DOMAINS)
        require_non_empty("batch_id", self.batch_id)
        require_choice("scope_level", self.scope_level, VALID_SCOPE_LEVELS)
        require_non_empty("scope_ref", self.scope_ref)
        require_choice("calibration_policy", self.calibration_policy, VALID_CALIBRATIONS)
        if not isinstance(self.score, (int, float)):
            raise ValueError("score must be numeric")
        require_mapping("payload", self.payload)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertRecord":
        obj = cls(
            alert_id=str(data["alert_id"]),
            run_id=str(data["run_id"]),
            detector=str(data["detector"]),
            domain=str(data["domain"]),
            batch_id=str(data["batch_id"]),
            scope_level=str(data["scope_level"]),
            scope_ref=str(data["scope_ref"]),
            score=float(data["score"]),
            calibration_policy=str(data["calibration_policy"]),
            payload=dict(data.get("payload", {})),
        )
        obj.validate()
        return obj
