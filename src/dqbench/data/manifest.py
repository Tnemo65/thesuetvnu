"""Snapshot manifest helpers and lightweight acquisition CLI."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from dqbench.config import dump_yaml
from dqbench.contracts.manifests import SnapshotManifest, SnapshotManifestEntry


@dataclass
class SnapshotEntry:
    dataset_id: str
    snapshot_id: str
    source_reference: str
    local_path: str
    snapshot_date: str
    schema_version_reference: str
    checksum_sha256: str
    file_role: str = "raw_file"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(path: str | Path, entries: Iterable[SnapshotEntry]) -> None:
    manifest = SnapshotManifest(
        entries=[SnapshotManifestEntry(**entry.__dict__) for entry in entries],
    )
    dump_yaml(path, json.loads(manifest.json()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a snapshot manifest from local files")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--snapshot-id", required=True)
    parser.add_argument("--schema-version", default="v1")
    parser.add_argument("--snapshot-date", required=True)
    parser.add_argument("--manifest-path", required=True)
    parser.add_argument("--files-csv", required=True, help="CSV with columns: source_url,local_path")
    args = parser.parse_args()

    entries: List[SnapshotEntry] = []
    with Path(args.files_csv).open("r", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            entries.append(
                SnapshotEntry(
                    dataset_id=args.domain,
                    snapshot_id=args.snapshot_id,
                    source_reference=row.get("source_reference") or row["source_url"],
                    local_path=row["local_path"],
                    snapshot_date=args.snapshot_date,
                    schema_version_reference=args.schema_version,
                    checksum_sha256=sha256_file(row["local_path"]),
                    file_role=row.get("file_role", "raw_file"),
                )
            )

    write_manifest(args.manifest_path, entries)
    print(json.dumps({"manifest_path": args.manifest_path, "entries": len(entries)}, indent=2))
