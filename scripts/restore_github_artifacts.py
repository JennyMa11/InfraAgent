"""Verify or restore lossless copies of frozen evaluation files from GitHub."""

import argparse
import gzip
import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "artifacts/github-large-evals/manifest.json"


def safe_path(relative):
    path = ROOT / relative
    if Path(relative).is_absolute() or not path.resolve().is_relative_to(ROOT):
        raise ValueError(f"Path outside repository: {relative}")
    return path


def digest(stream, output=None):
    sha = hashlib.sha256()
    size = 0
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        sha.update(block)
        size += len(block)
        if output is not None:
            output.write(block)
    return sha.hexdigest(), size


def verify_file(path, sha, size):
    with path.open("rb") as stream:
        actual = digest(stream)
    if actual != (sha, size):
        raise ValueError(f"Hash or size mismatch: {path.relative_to(ROOT)}")


def restore(entry, verify_only):
    archive = safe_path(entry["archive"])
    original = safe_path(entry["path"])
    verify_file(archive, entry["archive_sha256"], entry["archive_bytes"])
    if original.exists():
        verify_file(original, entry["sha256"], entry["bytes"])
    temporary = None
    try:
        if verify_only or original.exists():
            with gzip.open(archive, "rb") as stream:
                actual = digest(stream)
        else:
            original.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=original.parent, delete=False) as output:
                temporary = Path(output.name)
                with gzip.open(archive, "rb") as stream:
                    actual = digest(stream, output)
        if actual != (entry["sha256"], entry["bytes"]):
            raise ValueError(f"Decompressed hash or size mismatch: {entry['path']}")
        if temporary is not None:
            # Refuse to replace a file created while decompression was running.
            os.link(temporary, original)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true", help="Check without restoring files")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    if manifest["schema_version"] != 1 or manifest["compression"] != "gzip":
        raise ValueError("Unsupported archive manifest")
    for entry in manifest["files"]:
        restore(entry, args.verify_only)
    action = "Verified" if args.verify_only else "Restored or verified"
    print(f"{action} {len(manifest['files'])} frozen evaluation files")


if __name__ == "__main__":
    main()
