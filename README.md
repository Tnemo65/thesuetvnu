# dq-alert-benchmark scaffold

This directory is the implementation scaffold for `dq-alert-benchmark`.

The authoritative benchmark specification is maintained in one final document:

- [`documentation.md`](docs/documentation.md)

## Benchmark Contract Summary

The locked benchmark design in [`documentation.md`](docs/documentation.md) defines:

- `3 core domains`: `NYC TLC`, `BTS On-Time`, `Chicago Food`
- `1 external validation case study`: `NYC 311`
- `5 fault families` overall, with a `4-family` shared-core leaderboard and one `fk_break` extension
- `5 locked baseline families`
- `8 primary metrics`
- `1` `BTS` audit-backed supplementary appendix
- a transparent synthetic-injection protocol with published manifests and operator-bank metadata
- an audited clean track per core domain for false-positive and threshold-portability interpretation
- supplementary transfer analysis linking the injected benchmark to the external-validation tracks
- `snapshot-first` reproducibility with frozen splits, seeds, manifests, and checksums

This scaffold also ships optional `reference detector adapters` for `ECOD`, `COPOD`, and `Extended Isolation Forest`. They use public third-party code under the same batch-profile contract, but they are supplementary and do not change the locked five-baseline benchmark.

Baseline quality in this project is intentionally interpreted through multiple evidence layers:

- contract-valid execution on the canonical batch-profile interface
- performance on the transparent injected benchmark matrix
- false-positive behavior on the audited clean track
- descriptive transfer behavior on `NYC 311` and the `BTS` audit-backed appendix

## Role Of This Directory

This scaffold is the implementation workspace for the benchmark artifact. It is not the canonical source of benchmark scope decisions. Scope, protocol, baseline, metric, and artifact requirements are defined only by [`documentation.md`](docs/documentation.md).

## Acquisition Workflows

Phase 1 acquisition workflows live under [`configs/acquisition`](configs/acquisition) and are executed through the `dqbench-download-snapshots` CLI.

- Use `plan` to resolve the expected raw/support files for a frozen snapshot without downloading anything.
- Use `freeze` to download direct-url assets or stage portal-exported files into the snapshot-first workspace under `data/raw` and `data/external`, then materialize snapshot manifests.
- Portal/manual workflows fail loudly unless you first stage the exact exported files with the expected names.

## Optional Reference Detectors

Install the supplementary reference detectors with:

```bash
python3 -m pip install -e '.[ml,reference_detectors]'
```

`Extended Isolation Forest` currently depends on the public `eif` package, which in local validation on `April 1, 2026` required `Cython<3` to build cleanly.

Example runs:

```bash
python3 -m dqbench.orchestration.run_experiment --config configs/experiments/tlc_pilot_ecod.yaml
python3 -m dqbench.orchestration.run_experiment --config configs/experiments/tlc_pilot_copod.yaml
python3 -m dqbench.orchestration.run_experiment --config configs/experiments/tlc_pilot_eif.yaml
```

Reference notes for these detectors live in [`docs/external_reference_detectors.md`](docs/external_reference_detectors.md).
