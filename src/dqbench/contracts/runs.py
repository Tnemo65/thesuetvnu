"""Run configuration contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from dqbench.contracts.benchmark import (
    VALID_BATCH_UNITS,
    VALID_CALIBRATIONS,
    VALID_DETECTORS,
    VALID_DOMAINS,
    VALID_FAULTS,
    VALID_RUN_DURATIONS as VALID_DURATIONS,
    VALID_RUN_SEVERITIES as VALID_SEVERITIES,
)
from dqbench.utils.validation import (
    ValidationError,
    require_choice,
    require_keys,
    require_non_empty,
    require_non_negative_int,
)


@dataclass(frozen=True)
class RunSpec:
    domain: str
    snapshot_id: str
    batch_unit: str
    fault_family: str
    severity: str
    duration: str
    seed: int
    detector: str
    calibration_policy: str

    def validate(self) -> None:
        require_choice("domain", self.domain, VALID_DOMAINS)
        require_non_empty("snapshot_id", self.snapshot_id)
        require_choice("batch_unit", self.batch_unit, VALID_BATCH_UNITS)
        require_choice("fault_family", self.fault_family, VALID_FAULTS)
        require_choice("severity", self.severity, VALID_SEVERITIES)
        require_choice("duration", self.duration, VALID_DURATIONS)
        require_non_negative_int("seed", self.seed)
        require_choice("detector", self.detector, VALID_DETECTORS)
        require_choice("calibration_policy", self.calibration_policy, VALID_CALIBRATIONS)

        is_clean = self.fault_family == "clean"
        if is_clean and (self.severity != "none" or self.duration != "none"):
            raise ValidationError("clean runs must use severity='none' and duration='none'")
        if not is_clean and (self.severity == "none" or self.duration == "none"):
            raise ValidationError("dirty runs must use concrete severity and duration")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunSpec":
        require_keys(
            data,
            [
                "domain",
                "snapshot_id",
                "batch_unit",
                "fault_family",
                "severity",
                "duration",
                "seed",
                "detector",
                "calibration_policy",
            ],
            "RunSpec",
        )
        obj = cls(
            domain=str(data["domain"]),
            snapshot_id=str(data["snapshot_id"]),
            batch_unit=str(data["batch_unit"]),
            fault_family=str(data["fault_family"]),
            severity=str(data["severity"]),
            duration=str(data["duration"]),
            seed=int(data["seed"]),
            detector=str(data["detector"]),
            calibration_policy=str(data["calibration_policy"]),
        )
        obj.validate()
        return obj
