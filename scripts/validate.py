#!/usr/bin/env python3
"""Validate this repository's small, deliberately fixed plugin layout.

This is a project validator, not an implementation of every host's JSON schema.
It performs no network requests, host installation, or model-based evaluation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

PLUGIN_NAME = "academic-writing"
MARKETPLACE_NAME = "academic-writing-marketplace"
VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?")

# Explicit names prevent a new draft, secret, or local cache from entering a ZIP.
DISTRIBUTION_FILES = (
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".github/workflows/validate.yml",
    ".gitignore",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "NOTICE.md",
    "PRIVACY.md",
    "README.md",
    "docs/design.md",
    "docs/installation.md",
    "licenses/anti-defensive-writing-MIT.txt",
    "licenses/humanizer-MIT.txt",
    "prompts/academic-writing.txt",
    "scripts/build.py",
    "scripts/validate.py",
    "scripts/tests/test_packaging.py",
    "skills/academic-writing/SKILL.md",
    "skills/academic-writing/references/examples.md",
    "skills/academic-writing/references/review-checklist.md",
)


def contained_path(root: Path, value: str) -> Path:
    """Resolve a ./ plugin path and reject traversal, symlinks, and missing paths."""
    if not isinstance(value, str) or not value.startswith("./"):
        raise ValueError(f"expected a ./ relative path, got {value!r}")
    relative = Path(value)
    if ".." in relative.parts:
        raise ValueError(f"parent traversal is not allowed: {value}")
    path = root / relative
    for item in (path, *path.parents):
        if item == root.parent:
            break
        if item.is_symlink():
            raise ValueError(f"symbolic links are not packaged: {value}")
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"path leaves plugin root: {value}")
    if not path.exists():
        raise ValueError(f"missing path: {value}")
    return path


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path.name}")
    return value


def check_local_links(root: Path, source: Path, text: str) -> list[str]:
    """Check ordinary inline Markdown links, ignoring fenced code and remote URLs."""
    errors = []
    prose = re.sub(r"```.*?```|~~~.*?~~~", "", text, flags=re.S)
    for target in re.findall(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", prose):
        target = target.strip()
        if target.startswith("<") and ">" in target:
            target = target[1:target.index(">")]
        else:
            target = target.split(' "', 1)[0].split(" '", 1)[0]
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        linked = (source.parent / unquote(parsed.path)).resolve()
        if not linked.is_relative_to(root.resolve()) or not linked.exists():
            errors.append(f"{source.relative_to(root)}: broken local link {target}")
    return errors


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors = []
    for name in DISTRIBUTION_FILES:
        try:
            path = contained_path(root, "./" + name)
            if not path.is_file():
                raise ValueError(f"not a regular file: {name}")
            text = path.read_text(encoding="utf-8")
            if name.endswith(".md"):
                errors.extend(check_local_links(root, path, text))
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(str(exc))

    manifests = []
    for name in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        try:
            manifest = read_json(root / name)
            manifests.append(manifest)
            if manifest.get("name") != PLUGIN_NAME:
                errors.append(f"{name}: name must be {PLUGIN_NAME}")
            if not VERSION_PATTERN.fullmatch(str(manifest.get("version", ""))):
                errors.append(f"{name}: version must be a semantic version")
            if manifest.get("license") != "MIT":
                errors.append(f"{name}: license must be MIT")
            for key in ("description",):
                if not isinstance(manifest.get(key), str) or not manifest[key].strip():
                    errors.append(f"{name}: nonempty {key} is required")
            if not isinstance(manifest.get("author"), dict) or not manifest["author"].get("name"):
                errors.append(f"{name}: author.name is required")
            skills = manifest.get("skills", "./skills/")
            for skill_path in [skills] if isinstance(skills, str) else skills:
                if not contained_path(root, skill_path).is_dir():
                    errors.append(f"{name}: skills must point to a directory")
            for key in ("hooks", "mcpServers", "apps", "userConfig"):
                if key in manifest:
                    errors.append(f"{name}: unexpected runtime component {key}")
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"{name}: {exc}")
    if len(manifests) == 2:
        for field in ("name", "version", "description", "author", "license"):
            if manifests[0].get(field) != manifests[1].get(field):
                errors.append(f"plugin manifests disagree on {field}")

    for host, name in (("codex", ".agents/plugins/marketplace.json"),
                       ("claude", ".claude-plugin/marketplace.json")):
        try:
            marketplace = read_json(root / name)
            if marketplace.get("name") != MARKETPLACE_NAME:
                errors.append(f"{name}: unexpected marketplace name")
            plugins = marketplace.get("plugins")
            if not isinstance(plugins, list) or len(plugins) != 1:
                raise ValueError("expected exactly one plugin entry")
            entry = plugins[0]
            if entry.get("name") != PLUGIN_NAME:
                errors.append(f"{name}: plugin name mismatch")
            if host == "codex":
                source = entry.get("source", {})
                if source.get("source") != "local":
                    errors.append(f"{name}: expected local source")
                resolved = contained_path(root, source.get("path"))
                policy = entry.get("policy", {})
                if policy.get("installation") != "AVAILABLE" or policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
                    errors.append(f"{name}: invalid installation policy")
                if entry.get("category") != "Productivity":
                    errors.append(f"{name}: missing Productivity category")
            else:
                resolved = contained_path(root, entry.get("source"))
                if not marketplace.get("owner", {}).get("name"):
                    errors.append(f"{name}: owner.name is required")
            if resolved.resolve() != root:
                errors.append(f"{name}: source must point to the repository root")
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            errors.append(f"{name}: {exc}")

    skill_path = root / "skills/academic-writing/SKILL.md"
    try:
        skill_text = skill_path.read_text(encoding="utf-8")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", skill_text, re.S)
        if not match:
            raise ValueError("SKILL.md must begin with YAML front matter")
        metadata = match.group(1)
        name = re.search(r"^name:\s*([^\n]+)$", metadata, re.M)
        if not name or name.group(1).strip(" '\"") != PLUGIN_NAME:
            errors.append("SKILL.md: name does not match the directory")
        description = re.search(r"^description:\s*(\S.*)$", metadata, re.M)
        if not description:
            errors.append("SKILL.md: description is required")
        skill_version = re.search(r"^\s*version:\s*['\"]?([0-9]+\.[0-9]+\.[0-9]+)", metadata, re.M)
        if skill_version and manifests and skill_version.group(1) != manifests[0].get("version"):
            errors.append("SKILL.md: metadata version differs from plugin version")
    except (OSError, ValueError) as exc:
        errors.append(str(exc))

    try:
        prompt = (root / "prompts/academic-writing.txt").read_text(encoding="utf-8")
        invalid = sorted({char for char in prompt
                          if unicodedata.category(char).startswith(("P", "S"))
                          and char not in "，。"})
        if invalid:
            errors.append(f"short prompt contains punctuation other than ，。: {''.join(invalid)}")
    except OSError as exc:
        errors.append(str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Validated {len(DISTRIBUTION_FILES)} distribution files, two plugin manifests, two marketplaces, skill metadata, local links, and prompt punctuation.")
    print("Host installation and writing quality are not covered by this static check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
