#!/usr/bin/env python3
"""Build, incrementally update, and query lightweight multi-graph project memory."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path


QUERY_STOP_TERMS = {
    "about", "does", "explain", "how", "please", "what", "when", "why", "work",
    "为什", "什么", "如何", "怎么", "原因", "请问", "介绍", "解释",
}


def digest(value: object) -> str:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode()).hexdigest()


def terms(text: str) -> set[str]:
    values = {value.lower() for value in re.findall(r"[A-Za-z_$][\w$.-]{1,}|[\u4e00-\u9fff]{2,}", text)}
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        values.update(chunk[index:index + 2] for index in range(len(chunk) - 1))
    return values


def item(item_id: str, kind: str, text: str, refs: list[str], fingerprint: str, confidence: str = "high") -> dict:
    return {"id":item_id, "kind":kind, "text":text[:600], "terms":sorted(terms(text)), "source_refs":refs, "fingerprint":fingerprint, "confidence":confidence}


def source_fingerprint(source: dict) -> str:
    return source.get("sha256") or source.get("fingerprint") or digest({key:source.get(key) for key in ("path", "bytes", "mtime_ns")})


def component_fingerprint(component: dict, sources: dict[str, str]) -> str:
    referenced = {}
    for ref in component.get("source_refs", []):
        path = str(ref).split(":", 1)[0].split("#", 1)[0]
        if path in sources: referenced[path] = sources[path]
    return digest({"component":component, "sources":referenced})


def semantic_edge(left: dict, right: dict) -> dict | None:
    left_terms, right_terms = set(left["terms"]), set(right["terms"])
    union = left_terms | right_terms
    score = len(left_terms & right_terms) / len(union) if union else 0
    if score < 0.18: return None
    return {"from":left["id"], "to":right["id"], "relation":"term-overlap", "score":round(score, 3)}


def assemble(evidence: dict, manifest: dict, previous: dict | None = None) -> tuple[dict, dict]:
    source_hashes = {source["path"]:source_fingerprint(source) for source in evidence.get("files", [])}
    new_items = []
    for source in evidence.get("files", []):
        text = " ".join([source.get("path", ""), *source.get("headings", []), *source.get("symbols", []), *source.get("keywords", [])])
        new_items.append(item(f"source:{source['path']}", "source", text, [source["path"]], source_hashes[source["path"]]))
    for component in manifest.get("components", []):
        component_id = str(component.get("id", "unknown"))
        title = str(component.get("title", component_id))
        port_text = " ".join(f"{port.get('payload', '')} {port.get('shape', '')}" for port in component.get("ports", []))
        refs = list(component.get("source_refs", []))
        new_items.append(item(f"component:{component_id}", "component", f"{title}. {component.get('role', '')}. {port_text}", refs, component_fingerprint(component, source_hashes)))

    old_map = {entry["id"]:entry for entry in (previous or {}).get("items", [])}
    new_map = {entry["id"]:entry for entry in new_items}
    added = sorted(new_map.keys() - old_map.keys())
    removed = sorted(old_map.keys() - new_map.keys())
    updated = sorted(key for key in new_map.keys() & old_map.keys() if new_map[key] != old_map[key])
    unchanged = sorted((new_map.keys() & old_map.keys()) - set(updated))
    for key in unchanged: new_map[key] = old_map[key]
    active_items = [new_map[key] for key in sorted(new_map)]

    causal, entity, temporal = [], [], []
    for component in manifest.get("components", []):
        component_id = str(component.get("id", "unknown"))
        for ref in component.get("source_refs", []):
            path = str(ref).split(":", 1)[0].split("#", 1)[0]
            target = f"source:{path}"
            if target in new_map: entity.append({"from":f"component:{component_id}", "to":target, "relation":"grounded-in"})
    for edge in manifest.get("edges", []):
        source = edge.get("source", {}).get("component") or edge.get("from")
        target = edge.get("target", {}).get("component") or edge.get("to")
        if source and target: causal.append({"from":f"component:{source}", "to":f"component:{target}", "relation":edge.get("kind", "flow"), "edge_id":edge.get("id")})
    source_items = [entry for entry in active_items if entry["kind"] == "source"]
    mtimes = {f"source:{source['path']}":source.get("mtime_ns", 0) for source in evidence.get("files", [])}
    ordered = sorted(source_items, key=lambda entry:(mtimes.get(entry["id"], 0), entry["id"]))
    temporal.extend({"from":left["id"], "to":right["id"], "relation":"not-newer-than"} for left, right in zip(ordered, ordered[1:]))

    changed_ids = set(added + updated)
    semantic = []
    if previous:
        valid_ids = set(new_map)
        semantic.extend(edge for edge in previous.get("graphs", {}).get("semantic", []) if edge.get("from") in valid_ids and edge.get("to") in valid_ids and edge.get("from") not in changed_ids and edge.get("to") not in changed_ids)
    preserved_pairs = {tuple(sorted((edge["from"], edge["to"]))) for edge in semantic}
    for position, left in enumerate(active_items):
        for right in active_items[position + 1:]:
            pair = tuple(sorted((left["id"], right["id"])))
            if pair in preserved_pairs: continue
            if previous and left["id"] not in changed_ids and right["id"] not in changed_ids: continue
            edge = semantic_edge(left, right)
            if edge: semantic.append(edge)
    graphs = {"semantic":semantic, "temporal":temporal, "causal":causal, "entity":entity}
    old_graphs = (previous or {}).get("graphs", {})
    graph_changes = {name:old_graphs.get(name, []) != edges for name, edges in graphs.items()}
    inventory_changed = evidence.get("fingerprint") != (previous or {}).get("project", {}).get("source_fingerprint")
    changed = bool(added or removed or updated or inventory_changed or any(graph_changes.values()))
    previous_revision = int((previous or {}).get("revision", 0))
    change_set = {"added":added, "updated":updated, "removed":removed, "unchanged":len(unchanged), "inventory_changed":inventory_changed, "graphs_changed":[name for name, value in graph_changes.items() if value]}
    memory = {
        "version":"2.0", "revision":previous_revision + 1 if changed else previous_revision,
        "project":{"title":manifest.get("title", Path(evidence.get("target", "project")).name), "target":evidence.get("target"), "source_fingerprint":evidence.get("fingerprint", ""), "manifest_fingerprint":digest(manifest)},
        "last_update":change_set, "items":active_items, "graphs":graphs,
    }
    return memory, {"changed":changed, "revision":memory["revision"], **change_set}


def write_atomic(output: Path, memory: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)


def build(evidence_path: Path, manifest_path: Path, output: Path) -> dict:
    memory, report = assemble(json.loads(evidence_path.read_text(encoding="utf-8")), json.loads(manifest_path.read_text(encoding="utf-8")))
    write_atomic(output, memory)
    return report


def update(memory_path: Path, evidence_path: Path, manifest_path: Path, output: Path | None) -> dict:
    previous = json.loads(memory_path.read_text(encoding="utf-8"))
    memory, report = assemble(json.loads(evidence_path.read_text(encoding="utf-8")), json.loads(manifest_path.read_text(encoding="utf-8")), previous)
    destination = output or memory_path
    if report["changed"] or destination != memory_path: write_atomic(destination, memory)
    return report


def query(memory_path: Path, question: str, limit: int | None, evidence_path: Path | None) -> dict:
    memory = json.loads(memory_path.read_text(encoding="utf-8")); question_terms = terms(question) - QUERY_STOP_TERMS; lowered = question.lower()
    causal_cues = ("why", "how", "impact", "flow", "cause", "为什么", "如何", "影响", "流程", "原因")
    temporal_cues = ("when", "latest", "recent", "changed", "何时", "最新", "最近", "变化")
    entity_cue = bool(re.search(r"(?:[\w.-]+/)+[\w.-]+|[\w-]+\.(?:md|json|ya?ml|toml|tsx?|jsx?|py|go|rs|java|css)\b", lowered))
    preferred = "entity" if entity_cue else "causal" if any(cue in lowered for cue in causal_cues) else "temporal" if any(cue in lowered for cue in temporal_cues) else "semantic"
    items = memory.get("items", []); item_limit = limit or max(1, math.ceil(math.log2(len(items) + 1)))
    adjacency: dict[str, set[str]] = {}
    for edge in memory.get("graphs", {}).get(preferred, []):
        adjacency.setdefault(edge["from"], set()).add(edge["to"]); adjacency.setdefault(edge["to"], set()).add(edge["from"])
    scored = []
    for entry in items:
        overlap = len(question_terms & set(entry.get("terms", [])))
        exact = 2 if any(term in entry.get("text", "").lower() for term in question_terms) else 0
        scored.append((overlap * 4 + exact, entry))
    scored.sort(key=lambda pair:(-pair[0], pair[1]["id"]))
    selected = [entry for score, entry in scored if score > 0][:item_limit]
    selected_ids = {entry["id"] for entry in selected}
    neighbors = {neighbor for entry in selected for neighbor in adjacency.get(entry["id"], set())}
    for _, entry in scored:
        if len(selected) >= item_limit: break
        if entry["id"] in neighbors and entry["id"] not in selected_ids: selected.append(entry); selected_ids.add(entry["id"])
    stale = None
    if evidence_path:
        current = json.loads(evidence_path.read_text(encoding="utf-8")); stale = current.get("fingerprint") != memory.get("project", {}).get("source_fingerprint")
    compact = [{key:entry.get(key) for key in ("id", "kind", "text", "source_refs", "confidence")} for entry in selected]
    return {"query":question, "retrieval_graph":preferred, "matched":bool(compact), "needs_source_lookup":not bool(compact), "stale":stale, "revision":memory.get("revision"), "project":memory.get("project", {}), "evidence":compact}


def main() -> int:
    parser = argparse.ArgumentParser(); commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build"); build_parser.add_argument("--evidence", type=Path, required=True); build_parser.add_argument("--manifest", type=Path, required=True); build_parser.add_argument("--output", type=Path, default=Path(".visual-model/memory.json"))
    update_parser = commands.add_parser("update"); update_parser.add_argument("memory", type=Path); update_parser.add_argument("--evidence", type=Path, required=True); update_parser.add_argument("--manifest", type=Path, required=True); update_parser.add_argument("--output", type=Path)
    query_parser = commands.add_parser("query"); query_parser.add_argument("memory", type=Path); query_parser.add_argument("question"); query_parser.add_argument("--limit", type=int); query_parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    if args.command == "build": result = build(args.evidence, args.manifest, args.output)
    elif args.command == "update": result = update(args.memory, args.evidence, args.manifest, args.output)
    else: result = query(args.memory, args.question, args.limit, args.evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
