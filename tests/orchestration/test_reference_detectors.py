import importlib.util
import json
from pathlib import Path

import pytest

from dqbench.config import dump_yaml, load_yaml
from dqbench.orchestration.run_experiment import run_experiment


REFERENCE_CASES = (
    ("configs/experiments/tlc_pilot_ecod.yaml", "pyod"),
    ("configs/experiments/tlc_pilot_copod.yaml", "pyod"),
    ("configs/experiments/tlc_pilot_eif.yaml", "eif"),
)


def _write_temp_config(source_path: str, tmp_path: Path) -> Path:
    config = load_yaml(source_path)
    output_dir = tmp_path / Path(source_path).stem
    config["output_dir"] = str(output_dir)
    target_path = tmp_path / Path(source_path).name
    dump_yaml(target_path, config)
    return target_path


def test_reference_detectors_run_end_to_end(tmp_path):
    executed = 0
    for source_path, required_package in REFERENCE_CASES:
        if importlib.util.find_spec(required_package) is None:
            continue
        executed += 1
        config_path = _write_temp_config(source_path, tmp_path)
        result = run_experiment(config_path)
        assert result["metrics"]["incident_recall"] in {0.0, 1.0, None}
        assert len(result["scores_df"]) > 0

        schema_validation_path = Path(load_yaml(config_path)["output_dir"]) / "schema_validation.json"
        artifact = json.loads(schema_validation_path.read_text(encoding="utf-8"))
        assert artifact["reports"]
        assert all(report["passed"] for report in artifact["reports"])
    if executed == 0:
        pytest.skip("reference detector dependencies are not installed")
