import pandas as pd

from dqbench.reporting.aggregate import summarize_metrics
from dqbench.stats.inference import cliffs_delta, friedman_test, pairwise_wilcoxon_holm, vargha_delaney_a12


def test_friedman_and_pairwise_wilcoxon_work():
    df = pd.DataFrame(
        {
            "condition_id": ["c1", "c1", "c1", "c2", "c2", "c2", "c3", "c3", "c3"],
            "detector": ["a", "b", "c", "a", "b", "c", "a", "b", "c"],
            "score": [0.8, 0.6, 0.7, 0.9, 0.7, 0.75, 0.85, 0.65, 0.7],
        }
    )
    friedman = friedman_test(df, condition_col="condition_id", detector_col="detector", value_col="score")
    pairwise = pairwise_wilcoxon_holm(df, condition_col="condition_id", detector_col="detector", value_col="score")
    assert friedman["num_conditions"] == 3
    assert len(pairwise) == 3


def test_effect_sizes_and_summary():
    assert cliffs_delta([3, 4, 5], [1, 2, 3]) > 0
    assert vargha_delaney_a12([3, 4, 5], [1, 2, 3]) > 0.5
    summary = summarize_metrics(
        pd.DataFrame({"incident_recall": [0.2, 0.4], "incident_precision": [0.5, 0.7]}),
        metric_columns=["incident_recall", "incident_precision"],
    )
    assert set(summary["metric"]) == {"incident_recall", "incident_precision"}
