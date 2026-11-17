"""Regression checks for the packaging boundary; no model or network needed."""

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import write_archive
from validate import DISTRIBUTION_FILES, contained_path, validate

ROOT = Path(__file__).resolve().parents[2]


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        for name in DISTRIBUTION_FILES:
            source = ROOT / name
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    def test_clean_repository_is_valid(self):
        self.assertEqual(validate(self.root), [])

    def test_mismatched_versions_fail(self):
        path = self.root / ".claude-plugin/plugin.json"
        manifest = json.loads(path.read_text())
        manifest["version"] = "9.9.9"
        path.write_text(json.dumps(manifest))
        self.assertTrue(any("disagree on version" in error for error in validate(self.root)))

    def test_broken_local_reference_fails(self):
        path = self.root / "skills/academic-writing/SKILL.md"
        path.write_text(path.read_text() + "\n[Missing](references/missing.md)\n")
        self.assertTrue(any("broken local link" in error for error in validate(self.root)))

    def test_traversal_and_symlinks_are_rejected(self):
        with self.assertRaises(ValueError):
            contained_path(self.root, "./../secret")
        (self.root / "linked").symlink_to(self.root / "LICENSE")
        with self.assertRaises(ValueError):
            contained_path(self.root, "./linked")

    def test_archives_are_deterministic_and_exclude_unlisted_files(self):
        (self.root / ".env").write_text("DO_NOT_PUBLISH=private\n")
        (self.root / "private-draft.md").write_text("Unpublished manuscript")
        first = self.root.parent / "first.zip"
        second = self.root.parent / "second.zip"
        write_archive(self.root, first, "academic-writing/")
        write_archive(self.root, second, "academic-writing/")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as archive:
            self.assertEqual(archive.namelist(), ["academic-writing/" + name for name in sorted(DISTRIBUTION_FILES)])
            self.assertIsNone(archive.testzip())


if __name__ == "__main__":
    unittest.main()
