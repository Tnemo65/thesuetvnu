"""Benchmark metrics for incident-aware evaluation."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from dqbench.evaluation.matching import MatchResult


def _batch_position_map(batch_index: pd.DataFrame) -> Dict[str, int]:
    return {str(row["batch_id"]): int(row["batch_order"]) for _, row in batch_index.iterrows()}


def _hierarchical_localization_score(alert_scope_level: str, alert_scope_ref: str, incident_target: Dict[str, object]) -> float:
    if alert_scope_level == incident_target.get("level") and alert_scope_ref == incident_target.get("ref"):
        return 1.0
    if alert_scope_level == "table" and alert_scope_ref == incident_target.get("table_ref"):
        return 0.5
    return 0.0


def compute_metrics(
    match_result: MatchResult,
    batch_index: pd.DataFrame,
    runtime_seconds: float,
    clean_batch_count: int | None = None,
    row_count: int | None = None,
) -> Dict[str, float | None]:
    total_incidents = len(match_result.incidents)
    total_alerts = len(match_result.alerts)
    matched_count = len(match_result.matched_pairs)
    precision = (matched_count / total_alerts) if total_alerts else None
    recall = (matched_count / total_incidents) if total_incidents else None
    f1 = None
    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = 2 * precision * recall / (precision + recall)

    batch_positions = _batch_position_map(batch_index)
    delay_raw_values = []
    delay_norm_values = []
    localization_scores_strict = []
    localization_scores_hier = []
    for alert, incident in match_result.matched_pairs:
        start_pos = batch_positions.get(incident.start_batch, 0)
        alert_pos = batch_positions.get(alert.batch_id, start_pos)
        delay_raw = alert_pos - start_pos
        window_size = max(1, batch_positions.get(incident.end_batch, start_pos) - start_pos + 1)
        delay_raw_values.append(float(delay_raw))
        delay_norm_values.append(float(delay_raw / window_size))
        localization_scores_strict.append(
            1.0 if alert.scope_level == incident.target_scope.get("level") and alert.scope_ref == incident.target_scope.get("ref") else 0.0
        )
        localization_scores_hier.append(
            _hierarchical_localization_score(alert.scope_level, alert.scope_ref, incident.target_scope)
        )

    duplicate_burden = None
    if total_incidents:
        duplicate_burden = sum(max(0, len(v)) for v in match_result.duplicates_by_incident.values()) / total_incidents

    clean_run_fp_batch = None
    clean_run_fp_alert = None
    if clean_batch_count:
        alert_batches = {alert.batch_id for alert in match_result.alerts}
        clean_run_fp_batch = len(alert_batches) / clean_batch_count
        clean_run_fp_alert = len(match_result.alerts) / clean_batch_count

    runtime_per_1m_rows = None
    if row_count:
        runtime_per_1m_rows = runtime_seconds / max(row_count / 1_000_000.0, 1e-9)

    return {
        "incident_recall": recall,
        "incident_precision": precision,
        "incident_f1": f1,
        "detection_delay_raw_mean": sum(delay_raw_values) / len(delay_raw_values) if delay_raw_values else None,
        "detection_delay_norm_mean": sum(delay_norm_values) / len(delay_norm_values) if delay_norm_values else None,
        "localization_accuracy_strict": sum(localization_scores_strict) / len(localization_scores_strict)
        if localization_scores_strict
        else None,
        "localization_accuracy_hierarchical": sum(localization_scores_hier) / len(localization_scores_hier)
        if localization_scores_hier
        else None,
        "duplicate_burden": duplicate_burden,
        "clean_run_fp_batch": clean_run_fp_batch,
        "clean_run_fp_alert": clean_run_fp_alert,
        "runtime_overhead_seconds": runtime_seconds,
        "runtime_per_1m_rows": runtime_per_1m_rows,
    }
