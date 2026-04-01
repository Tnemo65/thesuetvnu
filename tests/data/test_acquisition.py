from pathlib import Path

import yaml

from dqbench.data.acquisition import (
    freeze_snapshot_assets,
    load_acquisition_workflow,
    resolve_acquisition_assets,
)


def _write_workflow(path: Path, payload: dict) -> Path:
    path.write_text(yaml.safe_dump({"acquisition_workflow": payload}, sort_keys=False), encoding="utf-8")
    return path


def test_resolve_direct_and_manual_assets_with_repeat_parameters(tmp_path):
    workflow_path = _write_workflow(
        tmp_path / "workflow.yaml",
        {
            "dataset_id": "tlc",
            "dataset_label": "NYC TLC",
            "portal_page": "https://example.com/tlc",
            "schema_version_reference": "https://example.com/schema",
            "schema_references": ["https://example.com/schema"],
            "primary_event_timestamp_column": "event_ts",
            "update_cadence_documentation": "monthly",
            "batch_unit": "daily",
            "portal_workflow": ["stage manual support files if needed"],
            "raw_assets": [
                {
                    "asset_id": "yellow_tripdata",
                    "file_role": "raw_file",
                    "acquisition_mode": "direct_url",
                    "source_reference": "https://example.com/yellow_tripdata_{year_month}.parquet",
                    "local_name_template": "yellow_tripdata_{year_month}.parquet",
                    "url_template": "https://example.com/yellow_tripdata_{year_month}.parquet",
                    "repeat_parameter": "year_month",
                }
            ],
            "support_assets": [
                {
                    "asset_id": "taxi_zone_lookup",
                    "file_role": "support_table",
                    "acquisition_mode": "manual_portal",
                    "source_reference": "https://example.com/taxi-zone",
                    "local_name_template": "taxi_zone_lookup.csv",
                    "manual_source_name_template": "taxi_zone_lookup.csv",
                }
            ],
        },
    )
    workflow = load_acquisition_workflow(workflow_path)

    resolved = resolve_acquisition_assets(
        workflow,
        snapshot_id="2025q1",
        snapshot_date="2025-03-31",
        output_root=tmp_path / "data",
        variables={"year_month": ["2025-01", "2025-02"]},
        manual_input_dir=tmp_path / "manual",
    )

    assert len(resolved) == 3
    assert sum(asset.file_role == "raw_file" for asset in resolved) == 2
    assert resolved[0].url.endswith("2025-01.parquet")
    assert resolved[-1].manual_source_path.endswith("taxi_zone_lookup.csv")


def test_freeze_snapshot_assets_writes_raw_and_support_manifests(tmp_path):
    direct_source = tmp_path / "yellow_tripdata_2025-01.parquet"
    direct_source.write_text("fake parquet bytes", encoding="utf-8")
    manual_dir = tmp_path / "manual"
    manual_dir.mkdir()
    manual_source = manual_dir / "taxi_zone_lookup.csv"
    manual_source.write_text("LocationID,Zone\n1,A\n", encoding="utf-8")

    workflow_path = _write_workflow(
        tmp_path / "workflow.yaml",
        {
            "dataset_id": "tlc",
            "dataset_label": "NYC TLC",
            "portal_page": "https://example.com/tlc",
            "schema_version_reference": "https://example.com/schema",
            "schema_references": ["https://example.com/schema"],
            "primary_event_timestamp_column": "event_ts",
            "update_cadence_documentation": "monthly",
            "batch_unit": "daily",
            "portal_workflow": ["save taxi zone export as taxi_zone_lookup.csv"],
            "raw_assets": [
                {
                    "asset_id": "yellow_tripdata",
                    "file_role": "raw_file",
                    "acquisition_mode": "direct_url",
                    "source_reference": direct_source.as_uri(),
                    "local_name_template": "yellow_tripdata_2025-01.parquet",
                    "url_template": direct_source.as_uri(),
                }
            ],
            "support_assets": [
                {
                    "asset_id": "taxi_zone_lookup",
                    "file_role": "support_table",
                    "acquisition_mode": "manual_portal",
                    "source_reference": "https://example.com/taxi-zone",
                    "local_name_template": "taxi_zone_lookup.csv",
                    "manual_source_name_template": "taxi_zone_lookup.csv",
                }
            ],
        },
    )
    workflow = load_acquisition_workflow(workflow_path)
    resolved = resolve_acquisition_assets(
        workflow,
        snapshot_id="2025q1",
        snapshot_date="2025-03-31",
        output_root=tmp_path / "data",
        manual_input_dir=manual_dir,
    )

    manifest_paths = freeze_snapshot_assets(resolved)

    raw_manifest = Path(manifest_paths["raw_manifest_path"])
    support_manifest = Path(manifest_paths["support_manifest_path"])
    assert raw_manifest.exists()
    assert support_manifest.exists()

    raw_data = yaml.safe_load(raw_manifest.read_text(encoding="utf-8"))
    support_data = yaml.safe_load(support_manifest.read_text(encoding="utf-8"))
    assert raw_data["entries"][0]["dataset_id"] == "tlc"
    assert support_data["entries"][0]["file_role"] == "support_table"
