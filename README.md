# dq-alert-benchmark

`dq-alert-benchmark` la repo benchmark cho `tabular data-quality alerting`, theo huong:

- `DuckDB + Parquet + Python`
- `3 core domains`: `NYC TLC`, `BTS On-Time`, `Chicago Food`
- `1 validation domain`: `NYC 311`
- `5 fault families`
- `4 baselines`
- `8 metrics`
- `incident-aware evaluation`

Trang thai hien tai:

- Da co `contracts` cho `RunSpec`, `IncidentRecord`, `AlertRecord`
- Da co `dataset adapters`, `manifest helpers`, `profiling`, `injectors`
- Da co `naive threshold`, `constraint-style`, `Redyuk-style history`, `IsolationForest`
- Da co `matching`, `calibration`, `metrics`, `TLC pilot runner`
- Da co `pytest` smoke suite tren du lieu synthetic

Khoi dong nhanh:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev,ml]
pytest
python -m dqbench.orchestration.run_experiment --config configs/experiments/tlc_pilot.yaml
```

Thu muc chinh:

- `src/dqbench`: package benchmark
- `configs`: dataset, detector, fault, experiment, calibration configs
- `scripts`: wrappers va acquisition helpers
- `tests`: unit + integration smoke tests
- `docs`: ghi chu protocol, claims, reproducibility, va architecture overview

Phan acquisition cho cac data portal song duoc thiet ke theo mo hinh `snapshot-first`: luu `manifest`, `checksum`, `snapshot_date`, va `schema_version`.
