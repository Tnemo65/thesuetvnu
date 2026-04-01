from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from dqbench.contracts.acquisition import AcquisitionWorkflowSpec
from dqbench.data.acquisition import load_acquisition_workflow


def test_repository_acquisition_workflows_load_for_all_phase1_sources():
    config_dir = Path(__file__).resolve().parents[2] / "configs" / "acquisition"
    expected = {
        "tlc": "direct_url",
        "bts": "manual_portal",
        "chicago_food": "manual_portal",
        "nyc_parking_violations": "manual_portal",
        "nyc_hpd_housing_complaints_violations": "manual_portal",
        "chicago_building_permits": "manual_portal",
        "nyc311": "manual_portal",
        "austin311": "manual_portal",
        "faa_opsnet": "manual_portal",
    }

    for dataset_id, expected_mode in expected.items():
        workflow = load_acquisition_workflow(config_dir / f"{dataset_id}.yaml")
        assert workflow.dataset_id == dataset_id
        assert workflow.raw_assets[0].acquisition_mode == expected_mode


def test_acquisition_contract_rejects_invalid_mode_specific_asset_fields():
    with pytest.raises(ValidationError, match="direct_url assets must define url_template"):
        AcquisitionWorkflowSpec(
            dataset_id="tlc",
            dataset_label="NYC TLC",
            portal_page="https://example.com",
            schema_version_reference="https://example.com/schema",
            schema_references=["https://example.com/schema"],
            primary_event_timestamp_column="event_ts",
            update_cadence_documentation="monthly",
            batch_unit="daily",
            raw_assets=[
                {
                    "asset_id": "raw",
                    "file_role": "raw_file",
                    "acquisition_mode": "direct_url",
                    "source_reference": "https://example.com/raw.csv",
                    "local_name_template": "raw.csv",
                }
            ],
        )

    with pytest.raises(ValidationError, match="manual_portal workflows must document portal_workflow steps"):
        AcquisitionWorkflowSpec(
            dataset_id="nyc311",
            dataset_label="NYC 311",
            portal_page="https://example.com",
            schema_version_reference="https://example.com/schema",
            schema_references=["https://example.com/schema"],
            primary_event_timestamp_column="Created Date",
            update_cadence_documentation="daily",
            batch_unit="daily",
            raw_assets=[
                {
                    "asset_id": "snapshot",
                    "file_role": "raw_file",
                    "acquisition_mode": "manual_portal",
                    "source_reference": "https://example.com/portal",
                    "local_name_template": "nyc311.csv",
                    "manual_source_name_template": "nyc311.csv",
                }
            ],
        )


def test_load_acquisition_workflow_accepts_root_or_nested_yaml_shape(tmp_path):
    path = tmp_path / "workflow.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "acquisition_workflow": {
                    "dataset_id": "tlc",
                    "dataset_label": "NYC TLC",
                    "portal_page": "https://example.com",
                    "schema_version_reference": "https://example.com/schema",
                    "schema_references": ["https://example.com/schema"],
                    "primary_event_timestamp_column": "event_ts",
                    "update_cadence_documentation": "monthly",
                    "batch_unit": "daily",
                    "raw_assets": [
                        {
                            "asset_id": "raw",
                            "file_role": "raw_file",
                            "acquisition_mode": "direct_url",
                            "source_reference": "file:///tmp/raw.csv",
                            "local_name_template": "raw.csv",
                            "url_template": "file:///tmp/raw.csv",
                        }
                    ],
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    workflow = load_acquisition_workflow(path)
    assert workflow.dataset_id == "tlc"
