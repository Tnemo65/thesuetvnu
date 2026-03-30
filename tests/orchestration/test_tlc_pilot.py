from pathlib import Path

from dqbench.orchestration.run_experiment import run_experiment


def test_tlc_pilot_runs_end_to_end(tmp_path):
    config_path = Path("configs/experiments/tlc_pilot.yaml")
    result = run_experiment(config_path)
    assert result["metrics"]["incident_recall"] in {0.0, 1.0, None}
    assert len(result["incidents"]) == 1
    assert len(result["scores_df"]) > 0
