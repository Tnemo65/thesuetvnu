# Repo-Doc Sync Audit

Date: `2026-04-01`

This audit records whether the machine-readable repo surface matches the locked benchmark contract in [documentation.md](documentation.md).

## Scope

Audited surfaces:

- benchmark constants and release-gate configs
- artifact requirement manifests
- acquisition configs and setup entry points
- dataset configs
- detector configs and baseline source surface
- orchestration, evaluation, and stats source surface
- contract, orchestration, evaluation, injection, and acquisition tests
- packaging/setup metadata

## Status Summary

- `Synced now`
  - [configs/benchmark/constants.yaml](../configs/benchmark/constants.yaml)
  - [src/dqbench/contracts/benchmark.py](../src/dqbench/contracts/benchmark.py)
  - [configs/benchmark/release_gate.yaml](../configs/benchmark/release_gate.yaml)
  - [configs/benchmark/artifact_requirements.yaml](../configs/benchmark/artifact_requirements.yaml)
  - [tests/contracts/test_benchmark_constants.py](../tests/contracts/test_benchmark_constants.py)
  - [tests/contracts/test_release_gate_manifests.py](../tests/contracts/test_release_gate_manifests.py)
- `Audited and still stale relative to spec`
  - acquisition configs
  - dataset configs
  - detector configs
  - orchestration/runtime code
  - transfer-analysis code
  - orchestration and acquisition tests
- `Environment blocker discovered during audit`
  - the default shell interpreter is still `Python 3.8`, but contract verification now runs cleanly in a `uv`-managed `Python 3.11` environment that satisfies [pyproject.toml](../pyproject.toml)

## Findings By Surface

### 1. Benchmark Constants and Release Gate

Classification: `code/config wrong before audit`, `fixed in this sync pass`

Resolved:

- official scope is now machine-readable as `6` core domains, `2` external validation tracks, `1` supplementary appendix, `5` locked baselines, and `6` public-code reference detectors
- run matrix is now machine-readable as `786` benchmark runs, `3930` locked-baseline executions, `4716` reference-detector executions, and `8646` full empirical executions
- release gate now requires:
  - audited clean-track publication
  - public-code reference-detector execution
  - transfer-analysis outputs
  - operator-evidence and robustness outputs
  - separate `NYC 311` and `Austin 311` validation publication
- artifact requirements now require:
  - realized-severity manifests
  - operator-evidence maps
  - audited clean-track outputs
  - transfer-analysis outputs
  - domain-scale disclosure outputs
  - native multi-alert appendix outputs

### 2. Acquisition and Dataset Surface

Classification: `code/config stale`

Audited files:

- [configs/acquisition/tlc.yaml](../configs/acquisition/tlc.yaml)
- [configs/acquisition/bts.yaml](../configs/acquisition/bts.yaml)
- [configs/acquisition/chicago_food.yaml](../configs/acquisition/chicago_food.yaml)
- [configs/acquisition/nyc311.yaml](../configs/acquisition/nyc311.yaml)
- [configs/acquisition/faa_opsnet.yaml](../configs/acquisition/faa_opsnet.yaml)
- [configs/datasets/tlc.yaml](../configs/datasets/tlc.yaml)
- [configs/datasets/bts.yaml](../configs/datasets/bts.yaml)
- [configs/datasets/chicago_food.yaml](../configs/datasets/chicago_food.yaml)
- [configs/datasets/nyc311.yaml](../configs/datasets/nyc311.yaml)
- [scripts/download_snapshots.py](../scripts/download_snapshots.py)
- [src/dqbench/data/acquisition.py](../src/dqbench/data/acquisition.py)

Current drift from spec:

- acquisition workflow configs now exist for all locked Phase 1 public sources:
  - `tlc`
  - `bts`
  - `chicago_food`
  - `nyc_parking_violations`
  - `nyc_hpd_housing_complaints_violations`
  - `chicago_building_permits`
  - `nyc311`
  - `austin311`
  - `faa_opsnet`
- missing dataset configs for:
  - `NYC Parking Violations`
  - `NYC HPD Housing Complaints and Violations`
  - `Chicago Building Permits`
  - `Austin 311`
- [configs/datasets/tlc.yaml](../configs/datasets/tlc.yaml) still describes a `synthetic_sample` pilot and fixed `calibration_batches: 5`, which conflicts with the locked `snapshot-first` and `30% / min 24` calibration policy
- existing dataset configs still hardcode legacy fields such as `calibration_batches`, which are no longer the source of truth for split generation

### 3. Detector Config and Baseline Surface

Classification: `code/config stale`

Audited files:

- [configs/detectors/](../configs/detectors)
- [src/dqbench/baselines/](../src/dqbench/baselines)
- [pyproject.toml](../pyproject.toml)

Current drift from spec:

- missing detector configs for shipped appendix detectors:
  - `kNN`
  - `LOF`
  - `One-Class SVM`
- existing detector configs still hardcode `table_ref: tlc_trips`, which is pilot-specific and not suitable as the project-wide detector-config surface
- appendix detector source code currently exists only for:
  - `ECOD`
  - `COPOD`
  - `Extended Isolation Forest`
- `pyproject.toml` is directionally aligned because `scikit-learn`, `pyod`, and `eif` are declared, so there is no packaging blocker for the chosen detector families

### 4. Orchestration, Evaluation, and Stats Surface

Classification: `code stale`

Audited files:

- [src/dqbench/orchestration/run_experiment.py](../src/dqbench/orchestration/run_experiment.py)
- [src/dqbench/evaluation/matching.py](../src/dqbench/evaluation/matching.py)
- [src/dqbench/evaluation/metrics.py](../src/dqbench/evaluation/metrics.py)
- [src/dqbench/stats/inference.py](../src/dqbench/stats/inference.py)

Current drift from spec:

- [run_experiment.py](../src/dqbench/orchestration/run_experiment.py) still only prepares live data for `tlc synthetic_sample` and fails loudly for real frozen snapshots
- detector registry in [run_experiment.py](../src/dqbench/orchestration/run_experiment.py) still lacks:
  - `kNN`
  - `LOF`
  - `One-Class SVM`
- split generation still depends on dataset-config `calibration_batches` instead of the locked chronological `30% / min 24` rule plus untouched clean holdout
- evaluation metrics still do not materialize:
  - `weak_label_hit_rate`
  - `weak_label_lead_lag_median`
  - fixed runtime-boundary metadata outputs
- stats surface still lacks the required transfer-analysis machinery:
  - `Spearman`
  - `Kendall`
  - injected-to-clean rank correlation
  - injected-to-BTS weak-label rank correlation
  - threshold-portability summaries

### 5. Tests

Classification: `tests stale`

Audited files:

- [tests/contracts/test_acquisition_contracts.py](../tests/contracts/test_acquisition_contracts.py)
- [tests/contracts/test_output_artifacts.py](../tests/contracts/test_output_artifacts.py)
- [tests/contracts/test_manifest_models.py](../tests/contracts/test_manifest_models.py)
- [tests/contracts/test_models.py](../tests/contracts/test_models.py)
- [tests/orchestration/test_tlc_pilot.py](../tests/orchestration/test_tlc_pilot.py)
- [tests/orchestration/test_reference_detectors.py](../tests/orchestration/test_reference_detectors.py)
- [tests/evaluation/test_matching_metrics.py](../tests/evaluation/test_matching_metrics.py)
- [tests/evaluation/test_stats_reporting.py](../tests/evaluation/test_stats_reporting.py)
- [tests/injection/test_injectors.py](../tests/injection/test_injectors.py)
- [tests/data/test_acquisition.py](../tests/data/test_acquisition.py)

Current drift from spec:

- acquisition contract tests still only expect the old five workflows:
  - `tlc`
  - `bts`
  - `chicago_food`
  - `nyc311`
  - `faa_opsnet`
- orchestration tests are still pilot-only:
  - `test_tlc_pilot.py` assumes the synthetic TLC pilot path
  - reference-detector tests only cover `ECOD`, `COPOD`, and `EIF`
- evaluation and injection tests are still TLC-shaped examples, which is acceptable for local unit semantics, but they do not cover the expanded official scope

### 6. Environment and Setup

Classification: `environment mismatch resolved for Phase 0 verification`

Observed during audit:

- targeted contract tests passed:
  - `tests/contracts/test_benchmark_constants.py`
  - `tests/contracts/test_release_gate_manifests.py`
- full `tests/contracts` verification now passes in a spec-compliant runtime:
  - command: `uv run --python 3.11 --extra dev pytest tests/contracts`
  - result: `23 passed`
- the default shell interpreter on this workstation is still `Python 3.8`, so future verification should continue to use `uv` or another `Python >= 3.10` environment instead of assuming `/usr/bin/python3` is sufficient

## What This Audit Changed

This audit pass already synchronized the machine-readable contract layer that would otherwise create parallel truths:

- benchmark constants
- release gate
- artifact requirements
- contract tests for those manifests
- acquisition workflow coverage for all locked Phase 1 public sources

## What Remains For Coding

The next implementation work should start from the stale surfaces identified above, in this order:

1. acquisition configs and dataset configs for the expanded official scope
2. split generation and clean-track orchestration
3. detector adapters and configs for `kNN`, `LOF`, and `One-Class SVM`
4. transfer-analysis and weak-label metrics
5. orchestration and acquisition tests for the expanded scope
