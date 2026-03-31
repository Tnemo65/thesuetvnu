"""Experiment runner for scaffolded benchmark runs."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

from dqbench.baselines.base import build_run_id
from dqbench.baselines.calibration_threshold_lower_bound import CalibrationThresholdLowerBoundBaseline
from dqbench.baselines.constraint_rule_baseline import ConstraintRuleBaseline
from dqbench.baselines.ewma_cusum_sequential import EWMACUSUMSequentialBaseline
from dqbench.baselines.history_based_robust_profile import HistoryBasedRobustProfileBaseline
from dqbench.baselines.isolation_forest import IsolationForestBaseline
from dqbench.config import load_run_spec, load_yaml
from dqbench.contracts.incidents import IncidentRecord
from dqbench.data.base import PreparedDataset
from dqbench.data.bts import BTSDatasetAdapter
from dqbench.data.chicago import ChicagoFoodDatasetAdapter
from dqbench.data.nyc311 import NYC311DatasetAdapter
from dqbench.data.profiling import build_batch_profiles, numeric_feature_columns
from dqbench.data.samples import generate_tlc_sample
from dqbench.data.tlc import TLCDatasetAdapter
from dqbench.evaluation.matching import match_alerts
from dqbench.evaluation.metrics import compute_metrics
from dqbench.injection.registry import build_injector

ADAPTERS = {
    "tlc": TLCDatasetAdapter,
    "bts": BTSDatasetAdapter,
    "chicago_food": ChicagoFoodDatasetAdapter,
    "nyc311": NYC311DatasetAdapter,
}

DETECTORS = {
    "calibration_threshold_lower_bound": CalibrationThresholdLowerBoundBaseline,
    "constraint_rule_baseline": ConstraintRuleBaseline,
    "history_based_robust_profile": HistoryBasedRobustProfileBaseline,
    "ewma_cusum_sequential": EWMACUSUMSequentialBaseline,
    "isolation_forest": IsolationForestBaseline,
}


def prepare_domain_data(domain: str, dataset_config: Dict[str, object]) -> PreparedDataset:
    if domain == "tlc" and dataset_config.get("synthetic_sample", False):
        raw_df, support_tables = generate_tlc_sample(
            days=int(dataset_config.get("sample_days", 14)),
            rows_per_day=int(dataset_config.get("sample_rows_per_day", 50)),
            seed=int(dataset_config.get("sample_seed", 42)),
        )
        return TLCDatasetAdapter().prepare(raw_df, support_tables=support_tables)
    raise NotImplementedError("Live data preparation is scaffolded via manifests; use synthetic_sample for now.")


def split_calibration_eval(df: pd.DataFrame, batch_index: pd.DataFrame, calibration_batches: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    ordered_batches = batch_index.sort_values("batch_order")["batch_id"].tolist()
    calibration_batch_ids = set(ordered_batches[:calibration_batches])
    calibration_df = df.loc[df["batch_id"].isin(calibration_batch_ids)].copy()
    eval_df = df.copy()
    return calibration_df, eval_df


def write_json(path: str | Path, data: object) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, default=str)


def run_experiment(config_path: str | Path) -> Dict[str, object]:
    config = load_yaml(config_path)
    run_spec = load_run_spec(config_path)
    dataset_config = load_yaml(config["dataset_config_path"])
    detector_config = load_yaml(config["detector_config_path"])
    calibration_config = load_yaml(config["calibration_config_path"])

    prepared = prepare_domain_data(run_spec.domain, dataset_config)
    clean_df = prepared.canonical_df
    batch_index = prepared.batch_index
    calibration_batches = int(dataset_config.get("calibration_batches", 5))
    calibration_df, _ = split_calibration_eval(clean_df, batch_index, calibration_batches)

    incidents: list[IncidentRecord] = []
    dirty_df = clean_df
    dirty_batch_index = batch_index
    if run_spec.fault_family != "clean":
        fault_config = load_yaml(config["fault_config_path"])
        fault_config["severity"] = run_spec.severity
        fault_config["duration"] = run_spec.duration
        injector = build_injector(run_spec.fault_family)
        injection_result = injector.inject(
            clean_df=clean_df,
            batch_index=batch_index,
            run_id=build_run_id(run_spec),
            domain=run_spec.domain,
            config=fault_config,
            seed=run_spec.seed,
        )
        dirty_df = injection_result.dirty_df
        dirty_batch_index = injection_result.dirty_batch_index
        incidents = injection_result.incidents

    calibration_profiles = build_batch_profiles(calibration_df, dataset_config)
    eval_profiles = build_batch_profiles(dirty_df, dataset_config)
    detector = DETECTORS[run_spec.detector]()
    detector_config.setdefault("feature_columns", numeric_feature_columns(calibration_profiles))
    start = time.perf_counter()
    detector.fit(calibration_profiles, detector_config)
    calibration_scores_df = detector.score(calibration_profiles)
    eval_scores_df = detector.score(eval_profiles)
    alerts = detector.emit_alerts(
        scores_df=eval_scores_df,
        calibration_scores=calibration_scores_df["score"],
        run_spec=run_spec,
        config={**calibration_config, **detector_config},
    )
    runtime_seconds = time.perf_counter() - start
    match_result = match_alerts(alerts, incidents)
    clean_batch_count = len(dirty_batch_index) if run_spec.fault_family == "clean" else None
    metrics = compute_metrics(
        match_result=match_result,
        batch_index=dirty_batch_index,
        runtime_seconds=runtime_seconds,
        clean_batch_count=clean_batch_count,
        row_count=len(dirty_df),
    )

    output_dir = config.get("output_dir")
    if output_dir:
        write_json(Path(output_dir) / "alerts.json", [asdict(alert) for alert in alerts])
        write_json(Path(output_dir) / "incidents.json", [asdict(incident) for incident in incidents])
        write_json(
            Path(output_dir) / "matches.json",
            {
                "matched_pairs": [
                    {"alert_id": alert.alert_id, "incident_id": incident.incident_id}
                    for alert, incident in match_result.matched_pairs
                ],
                "duplicate_alert_ids": [alert.alert_id for alert in match_result.duplicate_alerts],
                "unmatched_alert_ids": [alert.alert_id for alert in match_result.unmatched_alerts],
                "missed_incident_ids": [incident.incident_id for incident in match_result.missed_incidents],
            },
        )
        write_json(Path(output_dir) / "metrics.json", metrics)

    return {
        "run_id": build_run_id(run_spec),
        "alerts": alerts,
        "incidents": incidents,
        "match_result": match_result,
        "metrics": metrics,
        "batch_index": dirty_batch_index,
        "scores_df": eval_scores_df,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a dqbench experiment")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    result = run_experiment(args.config)
    print(json.dumps({"run_id": result["run_id"], "metrics": result["metrics"]}, indent=2, default=str))
