"""Injector registry."""

from __future__ import annotations

from dqbench.injection.duplicate_burst import DuplicateBurstInjector
from dqbench.injection.fk_break import FKBreakInjector
from dqbench.injection.freshness_lag import FreshnessLagInjector
from dqbench.injection.null_spike import NullSpikeInjector
from dqbench.injection.range_violation import RangeViolationInjector

INJECTOR_REGISTRY = {
    "null_spike": NullSpikeInjector,
    "duplicate_burst": DuplicateBurstInjector,
    "range_violation": RangeViolationInjector,
    "freshness_lag": FreshnessLagInjector,
    "fk_break": FKBreakInjector,
}


def build_injector(name: str):
    if name not in INJECTOR_REGISTRY:
        raise KeyError(f"Unknown injector {name!r}")
    return INJECTOR_REGISTRY[name]()
