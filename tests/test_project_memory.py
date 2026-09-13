#!/usr/bin/env python3

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "project_memory.py"
SPEC = importlib.util.spec_from_file_location("project_memory", SCRIPT)
project_memory = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(project_memory)


def evidence(source_hash="aaa", project_hash="inventory-a"):
    return {
        "target": "/example",
        "fingerprint": project_hash,
        "files": [
            {
                "path": "README.md",
                "sha256": source_hash,
                "mtime_ns": 10,
                "headings": ["Overview"],
                "symbols": [],
            }
        ],
    }


def manifest(role="Turns evidence into a model", include_renderer=True):
    components = [
        {
            "id": "modeler",
            "title": "Modeler",
            "role": role,
            "source_refs": ["README.md:1"],
            "ports": [],
        }
    ]
    if include_renderer:
        components.append(
            {
                "id": "renderer",
                "title": "Renderer",
                "role": "Renders the model",
                "source_refs": ["README.md:1"],
                "ports": [],
            }
        )
    return {
        "title": "Example",
        "components": components,
        "edges": [{"id": "flow", "from": "modeler", "to": "renderer", "kind": "data"}] if include_renderer else [],
    }


class IncrementalMemoryTests(unittest.TestCase):
    def test_noop_update_reuses_items_and_does_not_rewrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence_path = root / "evidence.json"
            manifest_path = root / "model.json"
            memory_path = root / "memory.json"
            evidence_path.write_text(json.dumps(evidence()), encoding="utf-8")
            manifest_path.write_text(json.dumps(manifest()), encoding="utf-8")

            project_memory.build(evidence_path, manifest_path, memory_path)
            before = memory_path.read_bytes()
            before_mtime = memory_path.stat().st_mtime_ns
            report = project_memory.update(memory_path, evidence_path, manifest_path, None)

            self.assertFalse(report["changed"])
            self.assertEqual(report["revision"], 1)
            self.assertEqual(report["unchanged"], 3)
            self.assertEqual(memory_path.read_bytes(), before)
            self.assertEqual(memory_path.stat().st_mtime_ns, before_mtime)

    def test_changed_source_updates_only_dependent_items(self):
        initial, _ = project_memory.assemble(evidence(), manifest())
        revised, report = project_memory.assemble(evidence("bbb", "inventory-b"), manifest(), initial)

        self.assertTrue(report["changed"])
        self.assertEqual(report["revision"], 2)
        self.assertEqual(report["added"], [])
        self.assertEqual(report["removed"], [])
        self.assertEqual(
            report["updated"],
            ["component:modeler", "component:renderer", "source:README.md"],
        )
        self.assertEqual(revised["project"]["source_fingerprint"], "inventory-b")

    def test_component_change_and_removal_are_reported(self):
        initial, _ = project_memory.assemble(evidence(), manifest())
        _, report = project_memory.assemble(
            evidence(), manifest(role="Builds a compact model", include_renderer=False), initial
        )

        self.assertEqual(report["revision"], 2)
        self.assertEqual(report["updated"], ["component:modeler"])
        self.assertEqual(report["removed"], ["component:renderer"])
        self.assertEqual(report["unchanged"], 1)

    def test_query_returns_compact_grounded_evidence(self):
        memory, _ = project_memory.assemble(evidence(), manifest())
        with tempfile.TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memory.json"
            memory_path.write_text(json.dumps(memory), encoding="utf-8")
            result = project_memory.query(memory_path, "How does the modeler flow work?", None, None)

        self.assertEqual(result["retrieval_graph"], "causal")
        self.assertTrue(result["matched"])
        self.assertGreaterEqual(len(result["evidence"]), 1)
        self.assertNotIn("terms", result["evidence"][0])
        self.assertIn("source_refs", result["evidence"][0])

    def test_query_does_not_return_unrelated_causal_fallback(self):
        memory, _ = project_memory.assemble(evidence(), manifest())
        with tempfile.TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memory.json"
            memory_path.write_text(json.dumps(memory), encoding="utf-8")
            result = project_memory.query(memory_path, "为什么量子咖啡机会发光？", None, None)

        self.assertFalse(result["matched"])
        self.assertTrue(result["needs_source_lookup"])
        self.assertEqual(result["evidence"], [])


if __name__ == "__main__":
    unittest.main()
