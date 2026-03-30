# Reproducibility Notes

- Repo uu tien `snapshot-first`, khong `API-live-first`.
- `configs/experiments/tlc_pilot.yaml` la duong chay smoke E2E cho TLC.
- Neu may khong co `python3-venv`, co the dung:

```bash
python3 -m pip install --user -e .[dev]
./scripts/check.sh
```

- Khi co snapshot that, moi domain nen co:
  - `snapshot_id`
  - `snapshot_date`
  - `schema_version`
  - `checksum_sha256`
  - `source_url`
