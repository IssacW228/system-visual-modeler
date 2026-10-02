#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "scan_evidence.py"
MODES = ("lite", "normal", "deep")


def write(root: Path, rel: str, text: str = "x\n") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def scan(target: Path, mode: str = "lite", question: str = "") -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(target), "--mode", mode, "--question", question],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def sampled(index: dict) -> list:
    return [item["path"] for item in index["files"]]


class ScanEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)

    def build_project(self):
        write(self.root, "README.md", "# Demo\n\nService overview.\n")
        write(self.root, ".github/workflows/ci.yml", "on: push\njobs: {}\n")
        write(self.root, ".env", "API_TOKEN=secret\n")
        write(self.root, "node_modules/dep/index.js", "module.exports = 1\n")
        write(self.root, "target/debug/app", "binary\n")
        for area in ("api", "core", "store", "web", "jobs", "auth"):
            for index in range(6):
                write(self.root, f"src/{area}/mod_{index}.py", f"def {area}_{index}():\n    return {index}\n")

    def test_broken_symlink_is_reported_not_fatal(self):
        write(self.root, "README.md", "# Demo\n")
        try:
            os.symlink(self.root / "missing-target", self.root / "dangling")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        index = scan(self.root)
        self.assertEqual(index["unresolved"], [{"path": "dangling", "reason": "broken-symlink"}])
        self.assertEqual(sampled(index), ["README.md"])

    def test_all_modes_share_one_inventory_and_differ_only_in_sampling(self):
        self.build_project()
        indexes = {mode: scan(self.root, mode) for mode in MODES}
        inventories = {mode: index["coverage"]["structure_scanned"] for mode, index in indexes.items()}
        self.assertEqual(len(set(inventories.values())), 1, inventories)
        counts = [indexes[mode]["coverage"]["content_sampled"] for mode in MODES]
        self.assertEqual(counts, sorted(counts))
        self.assertLess(counts[0], counts[-1])

    def test_hidden_config_is_inventoried_but_lite_skips_it_unless_asked(self):
        self.build_project()
        lite = scan(self.root, "lite")
        self.assertIn(".yml", lite["inventory"]["extensions"])
        self.assertNotIn(".github/workflows/ci.yml", sampled(lite))
        asked = scan(self.root, "lite", "how does the ci workflow run?")
        self.assertIn(".github/workflows/ci.yml", sampled(asked))

    def test_secrets_and_build_output_are_excluded_in_every_mode(self):
        self.build_project()
        for mode in MODES:
            with self.subTest(mode=mode):
                index = scan(self.root, mode)
                paths = sampled(index)
                self.assertFalse(any(path.startswith(("node_modules/", "target/")) or path == ".env" for path in paths))
                self.assertEqual(index["coverage"]["structure_scanned"], 2 + 36)

    def test_gitignore_is_honored(self):
        if shutil.which("git") is None:
            self.skipTest("git unavailable")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        write(self.root, ".gitignore", "generated/\n*.log\n")
        write(self.root, "README.md", "# Demo\n")
        write(self.root, "app.py", "def main():\n    pass\n")
        write(self.root, "debug.log", "noise\n")
        write(self.root, "generated/schema.py", "class Generated:\n    pass\n")
        index = scan(self.root, "deep")
        self.assertEqual(index["coverage"]["structure_scanned"], 3)
        self.assertNotIn("generated/schema.py", sampled(index))

    def test_non_python_languages_are_sampled_with_symbols(self):
        write(self.root, "README.md", "# Swift app\n")
        write(self.root, "Sources/App/main.swift", "import Foundation\n\n@main\nstruct App {\n    static func main() {}\n}\n")
        write(self.root, "Sources/App/Store.swift", "public final class Store {}\n")
        write(self.root, "android/src/Main.kt", "data class User(val id: Int)\nfun main() {}\n")
        write(self.root, "core/lib.rs", "pub(crate) fn run() {}\npub struct Engine;\nimpl Engine {}\n")
        index = scan(self.root, "deep")
        self.assertNotIn("unknown", index["inventory"]["kinds"])
        symbols = {item["path"]: item.get("symbols", []) for item in index["files"]}
        self.assertIn("Sources/App/main.swift", index["orientation"]["likely_entrypoints"])
        self.assertIn("Store", symbols["Sources/App/Store.swift"])
        self.assertIn("User", symbols["android/src/Main.kt"])
        self.assertTrue({"run", "Engine"} <= set(symbols["core/lib.rs"]))


if __name__ == "__main__":
    unittest.main()
