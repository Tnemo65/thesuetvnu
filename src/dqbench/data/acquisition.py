"""Acquisition workflows for public snapshot freeze."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from string import Formatter
from typing import Dict, Iterable, List
from urllib.parse import urlparse
from urllib.request import Request, url2pathname, urlopen

from dqbench.config import load_yaml
from dqbench.contracts.acquisition import AcquisitionAssetSpec, AcquisitionWorkflowSpec
from dqbench.data.manifest import SnapshotEntry, write_manifest

USER_AGENT = "dqbench-phase1-acquisition/0.1"


@dataclass(frozen=True)
class ResolvedAcquisitionAsset:
    dataset_id: str
    snapshot_id: str
    snapshot_date: str
    file_role: str
    asset_id: str
    acquisition_mode: str
    source_reference: str
    schema_version_reference: str
    target_path: str
    url: str | None = None
    manual_source_path: str | None = None


def _template_fields(template: str) -> set[str]:
    return {
        field_name
        for _, field_name, _, _ in Formatter().parse(template)
        if field_name is not None
    }


def _build_context(
    *,
    workflow: AcquisitionWorkflowSpec,
    snapshot_id: str,
    snapshot_date: str,
    values: Dict[str, str],
) -> Dict[str, str]:
    return {
        "dataset_id": workflow.dataset_id,
        "snapshot_id": snapshot_id,
        "snapshot_date": snapshot_date,
        **values,
    }


def _repeat_values(asset: AcquisitionAssetSpec, variables: Dict[str, List[str]]) -> Iterable[Dict[str, str]]:
    if asset.repeat_parameter is None:
        return [{}]
    values = variables.get(asset.repeat_parameter) or []
    if not values:
        raise ValueError(
            f"Asset {asset.asset_id!r} requires repeated values for {asset.repeat_parameter!r}; "
            f"pass --var {asset.repeat_parameter}=..."
        )
    return [{asset.repeat_parameter: value} for value in values]


def _render_template(template: str, context: Dict[str, str], *, asset_id: str) -> str:
    required = _template_fields(template)
    missing = sorted(required - set(context))
    if missing:
        raise ValueError(f"Asset {asset_id!r} template is missing values for {missing}")
    return template.format(**context)


def load_acquisition_workflow(path: str | Path) -> AcquisitionWorkflowSpec:
    data = load_yaml(path)
    workflow_data = data.get("acquisition_workflow", data)
    return AcquisitionWorkflowSpec(**workflow_data)


def resolve_acquisition_assets(
    workflow: AcquisitionWorkflowSpec,
    *,
    snapshot_id: str,
    snapshot_date: str,
    output_root: str | Path,
    variables: Dict[str, List[str]] | None = None,
    manual_input_dir: str | Path | None = None,
) -> List[ResolvedAcquisitionAsset]:
    variables = variables or {}
    output_root = Path(output_root)
    raw_root = output_root / "raw" / workflow.dataset_id / snapshot_id
    support_root = output_root / "external" / workflow.dataset_id / snapshot_id
    resolved: List[ResolvedAcquisitionAsset] = []

    for asset in [*workflow.raw_assets, *workflow.support_assets]:
        for value_set in _repeat_values(asset, variables):
            context = _build_context(
                workflow=workflow,
                snapshot_id=snapshot_id,
                snapshot_date=snapshot_date,
                values=value_set,
            )
            local_name = _render_template(asset.local_name_template, context, asset_id=asset.asset_id)
            target_dir = raw_root if asset.file_role == "raw_file" else support_root
            target_path = target_dir / local_name
            source_reference = _render_template(asset.source_reference, context, asset_id=asset.asset_id)
            url = None
            manual_source_path = None
            if asset.acquisition_mode == "direct_url":
                assert asset.url_template is not None
                url = _render_template(asset.url_template, context, asset_id=asset.asset_id)
            else:
                assert asset.manual_source_name_template is not None
                if manual_input_dir is None:
                    manual_source_name = _render_template(
                        asset.manual_source_name_template,
                        context,
                        asset_id=asset.asset_id,
                    )
                    manual_source_path = str(Path("<manual_input_dir>") / manual_source_name)
                else:
                    manual_source_name = _render_template(
                        asset.manual_source_name_template,
                        context,
                        asset_id=asset.asset_id,
                    )
                    manual_source_path = str(Path(manual_input_dir) / manual_source_name)

            resolved.append(
                ResolvedAcquisitionAsset(
                    dataset_id=workflow.dataset_id,
                    snapshot_id=snapshot_id,
                    snapshot_date=snapshot_date,
                    file_role=asset.file_role,
                    asset_id=asset.asset_id,
                    acquisition_mode=asset.acquisition_mode,
                    source_reference=source_reference,
                    schema_version_reference=workflow.schema_version_reference,
                    target_path=str(target_path),
                    url=url,
                    manual_source_path=manual_source_path,
                )
            )

    return resolved


def _download_to_path(url: str, target_path: str | Path) -> None:
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(url)
    if parsed.scheme == "file":
        source_path = Path(url2pathname(parsed.path))
        if not source_path.exists():
            raise FileNotFoundError(f"Direct acquisition source does not exist: {source_path}")
        shutil.copy2(source_path, target_path)
        return

    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request) as response, target_path.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def _stage_manual_file(source_path: str | Path, target_path: str | Path) -> None:
    source_path = Path(source_path)
    target_path = Path(target_path)
    if not source_path.exists():
        raise FileNotFoundError(
            f"Manual acquisition file not found: {source_path}. "
            "Portal/manual workflows require you to stage the exact exported files first."
        )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)


def freeze_snapshot_assets(resolved_assets: Iterable[ResolvedAcquisitionAsset]) -> Dict[str, str]:
    raw_entries: List[SnapshotEntry] = []
    support_entries: List[SnapshotEntry] = []

    resolved_list = list(resolved_assets)
    if not resolved_list:
        raise ValueError("No acquisition assets were resolved for the requested snapshot.")

    for asset in resolved_list:
        target_path = Path(asset.target_path)
        if asset.acquisition_mode == "direct_url":
            assert asset.url is not None
            _download_to_path(asset.url, target_path)
        else:
            assert asset.manual_source_path is not None
            _stage_manual_file(asset.manual_source_path, target_path)

        entry = SnapshotEntry(
            dataset_id=asset.dataset_id,
            snapshot_id=asset.snapshot_id,
            source_reference=asset.source_reference,
            local_path=str(target_path),
            snapshot_date=asset.snapshot_date,
            schema_version_reference=asset.schema_version_reference,
            checksum_sha256="",
            file_role=asset.file_role,
        )
        if asset.file_role == "raw_file":
            raw_entries.append(entry)
        else:
            support_entries.append(entry)

    # Defer checksum calculation to the manifest helper so each copied/downloaded file is hashed exactly once.
    raw_manifest_path = None
    support_manifest_path = None
    if raw_entries:
        raw_manifest_path = str(Path(raw_entries[0].local_path).parent / "snapshot_manifest.yaml")
        write_manifest_with_fresh_checksums(raw_manifest_path, raw_entries)
    if support_entries:
        support_manifest_path = str(Path(support_entries[0].local_path).parent / "support_table_manifest.yaml")
        write_manifest_with_fresh_checksums(support_manifest_path, support_entries)

    return {
        "raw_manifest_path": raw_manifest_path,
        "support_manifest_path": support_manifest_path,
    }


def write_manifest_with_fresh_checksums(path: str | Path, entries: Iterable[SnapshotEntry]) -> None:
    refreshed = []
    for entry in entries:
        refreshed.append(
            SnapshotEntry(
                dataset_id=entry.dataset_id,
                snapshot_id=entry.snapshot_id,
                source_reference=entry.source_reference,
                local_path=entry.local_path,
                snapshot_date=entry.snapshot_date,
                schema_version_reference=entry.schema_version_reference,
                checksum_sha256="",  # placeholder replaced by helper
                file_role=entry.file_role,
            )
        )

    final_entries = []
    from dqbench.data.manifest import sha256_file

    for entry in refreshed:
        final_entries.append(
            SnapshotEntry(
                dataset_id=entry.dataset_id,
                snapshot_id=entry.snapshot_id,
                source_reference=entry.source_reference,
                local_path=entry.local_path,
                snapshot_date=entry.snapshot_date,
                schema_version_reference=entry.schema_version_reference,
                checksum_sha256=sha256_file(entry.local_path),
                file_role=entry.file_role,
            )
        )
    write_manifest(path, final_entries)


def _parse_vars(items: List[str]) -> Dict[str, List[str]]:
    variables: Dict[str, List[str]] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --var {item!r}; expected key=value")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise ValueError(f"Invalid --var {item!r}; expected non-empty key and value")
        variables.setdefault(key, []).append(value)
    return variables


def _plan_payload(
    workflow: AcquisitionWorkflowSpec,
    resolved_assets: Iterable[ResolvedAcquisitionAsset],
) -> Dict[str, object]:
    return {
        "dataset_id": workflow.dataset_id,
        "dataset_label": workflow.dataset_label,
        "portal_page": workflow.portal_page,
        "schema_version_reference": workflow.schema_version_reference,
        "schema_references": workflow.schema_references,
        "primary_event_timestamp_column": workflow.primary_event_timestamp_column,
        "update_cadence_documentation": workflow.update_cadence_documentation,
        "batch_unit": workflow.batch_unit,
        "portal_workflow": workflow.portal_workflow,
        "resolved_assets": [asdict(asset) for asset in resolved_assets],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze public dataset snapshots and manifests")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", required=True, help="Path to acquisition workflow YAML")
    common.add_argument("--snapshot-id", required=True)
    common.add_argument("--snapshot-date", required=True, help="YYYY-MM-DD")
    common.add_argument("--output-root", default="data")
    common.add_argument("--manual-input-dir")
    common.add_argument(
        "--var",
        action="append",
        default=[],
        help="Repeatable key=value snapshot variable. Use multiple times for repeated assets, e.g. --var year_month=2025-01",
    )

    plan_parser = subparsers.add_parser("plan", parents=[common], help="Resolve the acquisition plan without downloading/staging files")
    freeze_parser = subparsers.add_parser("freeze", parents=[common], help="Freeze a snapshot by downloading or staging files and writing manifests")

    args = parser.parse_args()
    try:
        date.fromisoformat(args.snapshot_date)
    except ValueError as exc:
        raise SystemExit(f"--snapshot-date must be YYYY-MM-DD: {exc}") from exc

    workflow = load_acquisition_workflow(args.config)
    variables = _parse_vars(args.var)
    resolved_assets = resolve_acquisition_assets(
        workflow,
        snapshot_id=args.snapshot_id,
        snapshot_date=args.snapshot_date,
        output_root=args.output_root,
        variables=variables,
        manual_input_dir=args.manual_input_dir,
    )

    if args.command == "plan":
        print(json.dumps(_plan_payload(workflow, resolved_assets), indent=2))
        return

    manifest_paths = freeze_snapshot_assets(resolved_assets)
    payload = _plan_payload(workflow, resolved_assets)
    payload["manifest_paths"] = manifest_paths
    print(json.dumps(payload, indent=2))
