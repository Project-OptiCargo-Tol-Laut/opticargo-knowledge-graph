"""Build and verify the opticargo-shared wheel used by this repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from email.parser import Parser
from pathlib import Path


def wheel_metadata(wheel: Path) -> tuple[str, str]:
    with zipfile.ZipFile(wheel) as archive:
        metadata_files = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_files) != 1:
            raise ValueError("wheel must contain exactly one METADATA file")
        metadata = Parser().parsestr(archive.read(metadata_files[0]).decode("utf-8"))
    return metadata["Name"], metadata["Version"]


def verify_wheel(wheel: Path, expected_version: str | None = None) -> dict[str, str]:
    name, version = wheel_metadata(wheel)
    if name.casefold().replace("_", "-") != "opticargo-shared":
        raise ValueError(f"unexpected wheel distribution: {name}")
    if expected_version and version != expected_version:
        raise ValueError(f"expected shared version {expected_version}, received {version}")
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
    return {"wheel": str(wheel.resolve()), "name": name, "version": version, "sha256": digest}


def parse_args() -> argparse.Namespace:
    repository = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=repository.parent / "opticargo-shared")
    parser.add_argument("--output", type=Path, default=repository / "vendor")
    parser.add_argument("--wheel", type=Path, help="verify an existing wheel without building")
    parser.add_argument("--expected-version")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.wheel:
        report = verify_wheel(args.wheel, args.expected_version)
    else:
        source = args.source.resolve()
        if not (source / "pyproject.toml").is_file():
            raise FileNotFoundError(f"opticargo-shared source is invalid: {source}")
        args.output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="opticargo-shared-wheel-") as temp_dir:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--wheel",
                    "--no-isolation",
                    "--outdir",
                    temp_dir,
                    str(source),
                ],
                check=True,
                timeout=300,
            )
            wheels = list(Path(temp_dir).glob("*.whl"))
            if len(wheels) != 1:
                raise RuntimeError(f"expected one shared wheel, produced {len(wheels)}")
            report = verify_wheel(wheels[0], args.expected_version)
            destination = args.output / wheels[0].name
            shutil.copy2(wheels[0], destination)
            report = verify_wheel(destination, args.expected_version)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
