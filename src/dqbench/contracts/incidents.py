"""Ground-truth incident contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from dqbench.contracts.runs import VALID_DOMAINS, VALID_DURATIONS, VALID_FAULTS, VALID_SEVERITIES
from dqbench.utils.validation import (
    require_choice,
    require_mapping,
    require_non_empty,
    require_ordered_bounds,
)

VALID_SCOPE_LEVELS = ("relation", "table", "column")


@dataclass(frozen=True)
class IncidentRecord:
    incident_id: str
    run_id: str
    domain: str
    family: str
    severity: str
    duration: str
    target_scope: Dict[str, Any]
    start_batch: str
    end_batch: str
    window_start: str
    window_end: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        require_non_empty("incident_id", self.incident_id)
        require_non_empty("run_id", self.run_id)
        require_choice("domain", self.domain, VALID_DOMAINS)
        require_choice("family", self.family, VALID_FAULTS[:-1])
        require_choice("severity", self.severity, VALID_SEVERITIES[:-1])
        require_choice("duration", self.duration, VALID_DURATIONS[:-1])
        require_mapping("target_scope", self.target_scope)
        require_choice("target_scope.level", self.target_scope.get("level"), VALID_SCOPE_LEVELS)
        require_non_empty("target_scope.ref", self.target_scope.get("ref"))
        require_ordered_bounds("start_batch", self.start_batch, "end_batch", self.end_batch)
        require_ordered_bounds("window_start", self.window_start, "window_end", self.window_end)
        if self.start_batch < self.window_start or self.end_batch > self.window_end:
            raise ValueError("incident interval must lie inside the detection window")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IncidentRecord":
        obj = cls(
            incident_id=str(data["incident_id"]),
            run_id=str(data["run_id"]),
            domain=str(data["domain"]),
            family=str(data["family"]),
            severity=str(data["severity"]),
            duration=str(data["duration"]),
            target_scope=dict(data["target_scope"]),
            start_batch=str(data["start_batch"]),
            end_batch=str(data["end_batch"]),
            window_start=str(data["window_start"]),
            window_end=str(data["window_end"]),
            metadata=dict(data.get("metadata", {})),
        )
        obj.validate()
        return obj
