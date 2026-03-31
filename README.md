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
- `snapshot-first` reproducibility with frozen splits, seeds, manifests, and checksums

## Role Of This Directory

This scaffold is the implementation workspace for the benchmark artifact. It is not the canonical source of benchmark scope decisions. Scope, protocol, baseline, metric, and artifact requirements are defined only by [`documentation.md`](docs/documentation.md).
