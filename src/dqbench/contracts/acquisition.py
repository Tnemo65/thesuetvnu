"""Contracts for public acquisition workflows and frozen snapshot plans."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import Field, root_validator, validator

from dqbench.contracts.benchmark import VALID_DOMAINS
from dqbench.contracts.manifests import StrictModel, _ensure_non_empty_string

VALID_ACQUISITION_DATASETS = VALID_DOMAINS + ("faa_opsnet",)
VALID_ACQUISITION_MODES = ("direct_url", "manual_portal")
VALID_FILE_ROLES = ("raw_file", "support_table")


class AcquisitionAssetSpec(StrictModel):
    asset_id: str
    file_role: str
    acquisition_mode: str
    source_reference: str
    local_name_template: str
    url_template: Optional[str] = None
    manual_source_name_template: Optional[str] = None
    repeat_parameter: Optional[str] = None
    description: Optional[str] = None

    @validator("asset_id", "source_reference", "local_name_template")
    def _validate_required_text(cls, value: str, field: object) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("file_role")
    def _validate_file_role(cls, value: str) -> str:
        value = _ensure_non_empty_string("file_role", value)
        if value not in VALID_FILE_ROLES:
            raise ValueError(f"file_role must be one of {VALID_FILE_ROLES}")
        return value

    @validator("acquisition_mode")
    def _validate_mode(cls, value: str) -> str:
        value = _ensure_non_empty_string("acquisition_mode", value)
        if value not in VALID_ACQUISITION_MODES:
            raise ValueError(f"acquisition_mode must be one of {VALID_ACQUISITION_MODES}")
        return value

    @validator("url_template", "manual_source_name_template", "repeat_parameter", "description")
    def _validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _ensure_non_empty_string("optional_text", value)

    @root_validator
    def _validate_mode_specific_requirements(cls, values: Dict[str, object]) -> Dict[str, object]:
        mode = values.get("acquisition_mode")
        url_template = values.get("url_template")
        manual_source_name_template = values.get("manual_source_name_template")

        if mode == "direct_url" and not url_template:
            raise ValueError("direct_url assets must define url_template")
        if mode == "manual_portal" and not manual_source_name_template:
            raise ValueError("manual_portal assets must define manual_source_name_template")
        if mode == "direct_url" and manual_source_name_template is not None:
            raise ValueError("direct_url assets must not define manual_source_name_template")
        if mode == "manual_portal" and url_template is not None:
            raise ValueError("manual_portal assets must not define url_template")
        return values


class AcquisitionWorkflowSpec(StrictModel):
    dataset_id: str
    dataset_label: str
    portal_page: str
    schema_version_reference: str
    schema_references: List[str] = Field(..., min_items=1)
    primary_event_timestamp_column: str
    update_cadence_documentation: str
    batch_unit: str
    portal_workflow: List[str] = Field(default_factory=list)
    raw_assets: List[AcquisitionAssetSpec] = Field(..., min_items=1)
    support_assets: List[AcquisitionAssetSpec] = Field(default_factory=list)

    @validator(
        "dataset_id",
        "dataset_label",
        "portal_page",
        "schema_version_reference",
        "primary_event_timestamp_column",
        "update_cadence_documentation",
        "batch_unit",
        each_item=False,
    )
    def _validate_required_text(cls, value: str, field: object) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("dataset_id")
    def _validate_dataset_id(cls, value: str) -> str:
        if value not in VALID_ACQUISITION_DATASETS:
            raise ValueError(f"dataset_id must be one of {VALID_ACQUISITION_DATASETS}")
        return value

    @validator("schema_references", each_item=True)
    def _validate_schema_reference(cls, value: str) -> str:
        return _ensure_non_empty_string("schema_references", value)

    @validator("portal_workflow", each_item=True)
    def _validate_workflow_step(cls, value: str) -> str:
        return _ensure_non_empty_string("portal_workflow", value)

    @root_validator
    def _validate_asset_roles_and_workflow(cls, values: Dict[str, object]) -> Dict[str, object]:
        raw_assets = values.get("raw_assets") or []
        support_assets = values.get("support_assets") or []
        portal_workflow = values.get("portal_workflow") or []

        if any(asset.file_role != "raw_file" for asset in raw_assets):
            raise ValueError("raw_assets must use file_role='raw_file'")
        if any(asset.file_role != "support_table" for asset in support_assets):
            raise ValueError("support_assets must use file_role='support_table'")

        manual_assets = [asset for asset in [*raw_assets, *support_assets] if asset.acquisition_mode == "manual_portal"]
        if manual_assets and not portal_workflow:
            raise ValueError("manual_portal workflows must document portal_workflow steps")
        return values
