# dq-alert-benchmark scaffold

This directory is the implementation scaffold for `dq-alert-benchmark`.

The authoritative benchmark specification is maintained in one final document:

- [`documentation.md`](docs/documentation.md)

## Benchmark Contract Summary

The locked benchmark design in [`documentation.md`](docs/documentation.md) defines:

- `6 core domains`: `NYC TLC`, `BTS On-Time`, `Chicago Food`, `NYC Parking Violations`, `NYC HPD Housing Complaints and Violations`, `Chicago Building Permits`
- `2 external validation case studies`: `NYC 311`, `Austin 311`
- `5 fault families` overall, with a `4-family` shared-core leaderboard and one `fk_break` extension
- `5 locked baseline families`
- `6` public-code reference detectors: `ECOD`, `COPOD`, `Extended Isolation Forest`, `kNN`, `LOF`, `One-Class SVM`
- `8 primary metrics`
- `1` `BTS` audit-backed supplementary appendix
- a transparent synthetic-injection protocol with published manifests and operator-bank metadata
- an audited clean track per core domain for false-positive and threshold-portability interpretation
- supplementary transfer analysis linking the injected benchmark to the external-validation tracks
- a mandatory public-code reference-detector appendix for every paper-scale empirical release
- domain-scale disclosure tables for each admitted core-domain snapshot
- predeclared detector and injector definitions, plus a native multi-alert appendix when a detector emits more than one alert per batch
- `snapshot-first` reproducibility with frozen splits, seeds, manifests, and checksums

The benchmark requires public-code reference detector adapters for `ECOD`, `COPOD`, `Extended Isolation Forest`, `kNN`, `LOF`, and `One-Class SVM`. They use public third-party code under the same batch-profile contract, stay supplementary to the `5` locked baselines, and are required in every paper-scale empirical release appendix.

Baseline quality in this project is intentionally interpreted through multiple evidence layers:

- contract-valid execution on the canonical batch-profile interface
- performance on the transparent injected benchmark matrix
- false-positive behavior on the audited clean track
- descriptive transfer behavior on `NYC 311`, `Austin 311`, and the `BTS` audit-backed appendix

## Role Of This Directory

This scaffold is the implementation workspace for the benchmark artifact. It is not the canonical source of benchmark scope decisions. Scope, protocol, baseline, metric, and artifact requirements are defined only by [`documentation.md`](docs/documentation.md).

## Acquisition Workflows

Phase 1 acquisition workflows live under [`configs/acquisition`](configs/acquisition) and are executed through the `dqbench-download-snapshots` CLI.

- Use `plan` to resolve the expected raw/support files for a frozen snapshot without downloading anything.
- Use `freeze` to download direct-url assets or stage portal-exported files into the snapshot-first workspace under `data/raw` and `data/external`, then materialize snapshot manifests.
- Portal/manual workflows fail loudly unless you first stage the exact exported files with the expected names.

## Public-Code Reference Detectors

Install the reference-detector dependency set with:

```bash
python3 -m pip install -e '.[ml,reference_detectors]'
```

`Extended Isolation Forest` currently depends on the public `eif` package, which in local validation on `April 1, 2026` required `Cython<3` to build cleanly.

The official appendix scope also includes `kNN`, `LOF`, and `One-Class SVM`; their pinned upstream integrations are part of the benchmark contract and are tracked in the implementation plan and reference-detector notes.

Existing scaffolded example runs:

```bash
python3 -m dqbench.orchestration.run_experiment --config configs/experiments/tlc_pilot_ecod.yaml
python3 -m dqbench.orchestration.run_experiment --config configs/experiments/tlc_pilot_copod.yaml
python3 -m dqbench.orchestration.run_experiment --config configs/experiments/tlc_pilot_eif.yaml
```

Reference notes for these detectors live in [`docs/external_reference_detectors.md`](docs/external_reference_detectors.md).
