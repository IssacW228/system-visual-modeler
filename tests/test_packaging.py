#!/usr/bin/env python3

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, "SKILL.md must start with YAML frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return fields


class PackagingTest(unittest.TestCase):
    def setUp(self):
        self.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))

    def test_names_agree_across_codex_and_claude_manifests(self):
        name = frontmatter(self.skill)["name"]
        self.assertEqual(self.plugin["name"], name)
        self.assertEqual([entry["name"] for entry in self.marketplace["plugins"]], [name])
        self.assertEqual(self.marketplace["plugins"][0]["source"], "./")

    def test_description_fits_skill_limits(self):
        description = frontmatter(self.skill)["description"]
        self.assertTrue(0 < len(description) <= 1024)

    def test_plugin_root_loads_as_single_skill(self):
        self.assertFalse((ROOT / "skills").exists(), "a skills/ directory would replace the root SKILL.md")
        self.assertNotIn("skills", self.plugin)

    def test_referenced_bundle_paths_exist(self):
        paths = set(re.findall(r"(?:scripts|references|assets)/[\w./-]+", self.skill))
        self.assertTrue(paths)
        for path in sorted(paths):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path.rstrip("/.")).exists(), path)


if __name__ == "__main__":
    unittest.main()
