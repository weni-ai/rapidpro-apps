#!/usr/bin/env python3
"""Pin weni-rp-apps in Flows pyproject.toml and poetry.lock from PyPI JSON."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path


PACKAGE = "weni-rp-apps"


def pypi_json(version: str) -> dict:
    url = f"https://pypi.org/pypi/{PACKAGE}/{version}/json"
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def format_spec(spec: str) -> str:
    if not spec:
        return "*"
    parts = [part.strip() for part in spec.split(",") if part.strip()]

    def sort_key(part: str) -> tuple[int, str]:
        if part.startswith(">="):
            return (0, part)
        if part.startswith(">"):
            return (1, part)
        if part.startswith("=="):
            return (2, part)
        if part.startswith("<="):
            return (3, part)
        if part.startswith("<"):
            return (4, part)
        return (5, part)

    return ",".join(sorted(parts, key=sort_key))


def lock_dependencies(requires_dist: list[str] | None) -> str:
    if not requires_dist:
        return ""
    lines = ["", "[package.dependencies]"]
    for requirement in requires_dist:
        requirement = requirement.split(";", 1)[0].strip()
        match = re.match(r"^([A-Za-z0-9_.-]+)\s*(.*)$", requirement)
        if not match:
            continue
        name, spec = match.group(1), match.group(2).strip()
        lines.append(f'{name} = "{format_spec(spec)}"')
    return "\n".join(lines) + "\n"


def lock_package_block(version: str, payload: dict) -> str:
    info = payload["info"]
    files = []
    for item in payload["urls"]:
        sha = item["digests"]["sha256"]
        files.append(f'    {{file = "{item["filename"]}", hash = "sha256:{sha}"}}')
    files_toml = "files = [\n" + ",\n".join(files) + ",\n]"
    python_versions = info.get("requires_python") or "*"
    description = info.get("summary") or ""
    return (
        f"[[package]]\n"
        f'name = "{PACKAGE}"\n'
        f'version = "{version}"\n'
        f'description = {json.dumps(description)}\n'
        f"optional = false\n"
        f'python-versions = "{python_versions}"\n'
        f'groups = ["main"]\n'
        f"{files_toml}\n"
        f"{lock_dependencies(info.get('requires_dist'))}"
    )


def update_pyproject(path: Path, version: str) -> None:
    text = path.read_text()
    if re.search(r"a|b|rc", version):
        replacement = (
            f'{PACKAGE} = {{version = "{version}", allow-prereleases = true}}'
        )
    else:
        replacement = f'{PACKAGE} = "{version}"'
    updated, count = re.subn(rf"^{PACKAGE} = .*$", replacement, text, flags=re.M)
    if count != 1:
        raise SystemExit(f"expected 1 {PACKAGE} entry in {path}, found {count}")
    path.write_text(updated)


def update_lock(path: Path, version: str, payload: dict) -> None:
    text = path.read_text()
    block = lock_package_block(version, payload)
    updated, count = re.subn(
        rf'\[\[package\]\]\nname = "{PACKAGE}"\n.*?(?=\n\[\[package\]\]\n)',
        block + "\n",
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit(f"expected 1 {PACKAGE} package in {path}, found {count}")
    path.write_text(updated)


def refresh_content_hash() -> None:
    from poetry.core.pyproject.toml import PyProjectTOML
    from poetry.packages.locker import Locker

    pyproject_path = Path("pyproject.toml").resolve()
    pyproject = PyProjectTOML(pyproject_path)
    locker = Locker(pyproject_path.parent / "poetry.lock", pyproject.data)
    content_hash = locker._get_content_hash()
    lock = Path("poetry.lock")
    text = lock.read_text()
    updated, count = re.subn(
        r"^content-hash = \".*\"$",
        f'content-hash = "{content_hash}"',
        text,
        flags=re.M,
    )
    if count != 1:
        raise SystemExit(f"expected 1 content-hash in poetry.lock, found {count}")
    lock.write_text(updated)
    print(f"Loaded {pyproject_path}")
    print(f"Updated poetry.lock content-hash to {content_hash}")


def main() -> None:
    version = os.environ.get("VERSION")
    if not version:
        raise SystemExit("VERSION env var is required")

    payload = pypi_json(version)
    update_pyproject(Path("pyproject.toml"), version)
    update_lock(Path("poetry.lock"), version, payload)
    refresh_content_hash()
    print(f"Pinned {PACKAGE} to {version}")


if __name__ == "__main__":
    sys.exit(main())
