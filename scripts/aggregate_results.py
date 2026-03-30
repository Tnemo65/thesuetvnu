#!/usr/bin/env python3
"""Aggregate metrics.json files under an output directory."""

from __future__ import annotations

import argparse

from dqbench.reporting.aggregate import collect_metric_records, summarize_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate dqbench result files")
    parser.add_argument("--output-root", default="outputs/runs")
    args = parser.parse_args()
    df = collect_metric_records(args.output_root)
    summary = summarize_metrics(
        df,
        metric_columns=[
            "incident_recall",
            "incident_precision",
            "incident_f1",
            "detection_delay_raw_mean",
            "localization_accuracy_hierarchical",
            "duplicate_burden",
            "clean_run_fp_batch",
            "runtime_overhead_seconds",
        ],
    )
    print(summary.to_string(index=False) if not summary.empty else "No metrics found.")


if __name__ == "__main__":
    main()
