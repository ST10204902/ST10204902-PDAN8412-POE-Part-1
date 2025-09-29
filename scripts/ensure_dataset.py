"""Utilities to make sure the Victorian author attribution dataset is present locally.

This module checks whether the expected files exist under the project `data/` directory.
If they are missing it downloads the official UCI archive, extracts the nested archive,
places the contents into `data/`, and leaves a cached copy of the zip in `artifacts/`.
"""

from __future__ import annotations

import argparse

import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Iterable, Optional, Sequence

DATASET_URL = "https://archive.ics.uci.edu/static/public/454/victorian+era+authorship+attribution.zip"
ARCHIVE_FILENAME = "victorian_era_authorship_attribution.zip"
EXPECTED_FILES = (
    "Data Description.pdf",
    "Gungor_2018_VictorianAuthorAttribution_data.csv",
    "Gungor_2018_VictorianAuthorAttribution_data-train.csv",
)


def project_root() -> Path:
    """Return the repository root based on the script location."""

    return Path(__file__).resolve().parents[1]


def data_dir() -> Path:
    """Return the canonical data directory path."""

    return project_root() / "data"


def artifacts_dir() -> Path:
    """Return the directory used for cached artifacts."""

    return project_root() / "artifacts"


def existing_dataset_files(data_path: Path) -> Iterable[Path]:
    """Yield paths to expected dataset files that are currently present."""

    for name in EXPECTED_FILES:
        path = data_path / name
        if path.exists():
            yield path


def missing_dataset_files(data_path: Path) -> Sequence[str]:
    """Return the list of expected dataset files that are currently missing."""

    return [name for name in EXPECTED_FILES if not (data_path / name).exists()]


def download_archive(url: str, destination: Path) -> None:
    """Download the dataset archive to the destination path."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading archive from {url}\n  -> {destination}")
    try:
        with urllib.request.urlopen(url) as response, open(destination, "wb") as output:
            shutil.copyfileobj(response, output)
    except Exception as exc:  # pragma: no cover
        if destination.exists():
            destination.unlink()
        raise RuntimeError(f"Failed to download dataset archive: {exc}") from exc


def extract_outer_archive(archive_path: Path, target_dir: Path) -> None:
    """Extract root-level items from the main archive into the target directory."""

    with zipfile.ZipFile(archive_path) as zf:
        members = zf.namelist()
        print(f"Extracting {archive_path.name} to {target_dir} ({len(members)} members)")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            zf.extractall(tmp_path)
            for item in tmp_path.iterdir():
                destination = target_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, destination, dirs_exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, destination)


def extract_nested_dataset(data_path: Path) -> None:
    """Extract dataset.zip (if present) into the data directory."""

    nested_zip = data_path / "dataset.zip"
    if not nested_zip.exists():
        return

    with zipfile.ZipFile(nested_zip) as nested:
        members = nested.namelist()
        print(f"Extracting nested archive {nested_zip.name} ({len(members)} members)")
        nested.extractall(data_path)

    dataset_folder = data_path / "dataset"
    if dataset_folder.exists():
        for item in dataset_folder.iterdir():
            destination = data_path / item.name
            if item.is_dir():
                shutil.copytree(item, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(item, destination)


def ensure_dataset(force_download: bool = False, archive_source: Optional[str] = None, dry_run: bool = False) -> None:
    """Ensure the Victorian author attribution dataset is available locally."""

    data_path = data_dir()
    artifacts_path = artifacts_dir()
    data_path.mkdir(parents=True, exist_ok=True)
    artifacts_path.mkdir(parents=True, exist_ok=True)

    missing = missing_dataset_files(data_path)
    if not missing and not force_download:
        print("All expected dataset files are already present. Nothing to do.")
        return

    if dry_run:
        print("Missing files detected:" if missing else "Force download requested.")
        for name in missing:
            print(f"  - {name}")
        return

    if archive_source:
        archive_path = Path(archive_source).expanduser().resolve()
        if not archive_path.exists():
            raise FileNotFoundError(f"The specified archive does not exist: {archive_path}")
        print(f"Using provided archive at {archive_path}")
    else:
        archive_path = artifacts_path / ARCHIVE_FILENAME
        if force_download or not archive_path.exists():
            download_archive(DATASET_URL, archive_path)
        else:
            print(f"Using cached archive at {archive_path}")

    extract_outer_archive(archive_path, data_path)
    extract_nested_dataset(data_path)

    remaining = missing_dataset_files(data_path)
    if remaining:
        raise RuntimeError(
            "Dataset download or extraction finished but some files are still missing: "
            + ", ".join(remaining)
        )

    print("Dataset is ready.")


def parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for the script."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Download the archive even if expected files are present or a cached zip exists.",
    )
    parser.add_argument(
        "--archive-path",
        type=str,
        help="Use an already-downloaded archive at the given path instead of fetching from the internet.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report missing files without downloading or extracting anything.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point for the CLI."""

    args = parse_arguments(argv)
    try:
        ensure_dataset(
            force_download=args.force_download,
            archive_source=args.archive_path,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # pragma: no cover - CLI surface
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
