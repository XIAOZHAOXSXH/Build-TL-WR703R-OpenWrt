#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
from collections import deque
from pathlib import Path


DEP_VERSION_RE = re.compile(r"\s*\([^)]*\)")


def parse_packages_file(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    current_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw_line.strip():
            if current.get("Package") and current.get("Filename"):
                entries.append(current)
            current = {}
            current_key = None
            continue

        if raw_line[0].isspace() and current_key:
            current[current_key] += raw_line.strip()
            continue

        key, value = raw_line.split(":", 1)
        current_key = key
        current[key] = value.strip()

    if current.get("Package") and current.get("Filename"):
        entries.append(current)

    return entries


def dep_candidates(raw_dep: str) -> list[str]:
    names: list[str] = []
    for option in raw_dep.split("|"):
        dep = DEP_VERSION_RE.sub("", option).strip()
        dep = dep.lstrip("+")
        if not dep or dep.startswith("@") or dep.startswith("!"):
            continue
        names.append(dep)
    return names


def resolve_package_file(bin_packages: Path, filename: str) -> Path | None:
    candidate = bin_packages / filename
    if candidate.exists():
        return candidate

    basename = Path(filename).name
    matches = list(bin_packages.rglob(basename))
    if matches:
        return matches[0]

    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin-packages", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", action="append", default=[])
    args = parser.parse_args()

    bin_packages = Path(args.bin_packages).resolve()
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    packages: dict[str, dict[str, str]] = {}
    for packages_file in sorted(bin_packages.rglob("Packages")):
        for entry in parse_packages_file(packages_file):
            packages.setdefault(entry["Package"], entry)

    selected: list[str] = []
    seen: set[str] = set()
    queue = deque(args.seed)

    while queue:
        package_name = queue.popleft()
        if package_name in seen:
            continue
        seen.add(package_name)

        entry = packages.get(package_name)
        if not entry:
            continue

        selected.append(package_name)

        for raw_dep in entry.get("Depends", "").split(","):
            candidates = dep_candidates(raw_dep)
            chosen = next((dep for dep in candidates if dep in packages), None)
            if chosen and chosen not in seen:
                queue.append(chosen)

    manifest_lines: list[str] = []
    for package_name in selected:
        entry = packages[package_name]
        package_file = resolve_package_file(bin_packages, entry["Filename"])
        if not package_file:
            continue

        shutil.copy2(package_file, output_dir / package_file.name)
        manifest_lines.append(f"{package_name}\t{package_file.name}")

    manifest = output_dir / "package-manifest.txt"
    manifest.write_text("\n".join(manifest_lines) + ("\n" if manifest_lines else ""), encoding="utf-8")

    print(f"Collected {len(manifest_lines)} packages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
