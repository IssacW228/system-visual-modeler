#!/usr/bin/env python3
"""Scan all structure, then sample authoritative evidence with adaptive detail."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
from collections import Counter
from pathlib import Path

IGNORED = {".git", ".next", ".visual-model", ".venv", "node_modules", "dist", "build", "coverage", "vendor", "__pycache__"}
TEXT_EXTENSIONS = {".c", ".cc", ".cpp", ".css", ".go", ".h", ".html", ".java", ".js", ".jsx", ".json", ".md", ".mjs", ".py", ".rb", ".rs", ".sh", ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"}
RICH_EXTENSIONS = {".csv", ".doc", ".docx", ".jpeg", ".jpg", ".mp3", ".mp4", ".pdf", ".png", ".ppt", ".pptx", ".tsv", ".wav", ".webp", ".xls", ".xlsx"}
AUTHORITY_NAMES = {
    "readme.md": 120, "readme.txt": 115, "architecture.md": 112, "overview.md": 108,
    "agents.md": 104, "skill.md": 104, "claude.md": 102, "product_requirements.md": 98,
    "requirements.md": 96, "spec.md": 96, "contributing.md": 92, "getting-started.md": 90,
    "quickstart.md": 90, "package.json": 84, "pyproject.toml": 84, "cargo.toml": 84,
    "go.mod": 84, "pom.xml": 84, "dockerfile": 78, "docker-compose.yml": 78,
}
MODE_DETAIL = {"lite": 1, "normal": 2, "deep": 4}
COMMON_TERMS = {
    "about", "after", "also", "before", "being", "class", "const", "export",
    "from", "function", "have", "import", "into", "return", "that", "their",
    "then", "this", "type", "using", "when", "where", "which", "with",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".md", ".txt"}: return "document"
    if ext in {".json", ".toml", ".yaml", ".yml", ".xml"} or path.name.lower() == "dockerfile": return "config"
    if ext in TEXT_EXTENSIONS: return "source"
    if ext in RICH_EXTENSIONS: return "rich-document"
    return "unknown"


def iter_files(target: Path):
    if target.is_file():
        yield target
        return
    for root, dirs, names in os.walk(target):
        dirs[:] = sorted(name for name in dirs if name not in IGNORED and not name.startswith("."))
        for name in sorted(names):
            if not name.startswith("."):
                yield Path(root) / name


def adaptive_take(values: list[str], source_size: int) -> list[str]:
    unique = list(dict.fromkeys(value.strip() for value in values if value.strip()))
    if not unique: return []
    detail = max(1, math.ceil(math.log2(max(source_size, 2))))
    if len(unique) <= detail: return unique
    step = len(unique) / detail
    return [unique[min(int(index * step), len(unique) - 1)] for index in range(detail)]


def extract_keywords(text: str, source_size: int) -> list[str]:
    english = [value.lower() for value in re.findall(r"[A-Za-z_$][\w$.-]{2,}", text)]
    english = [value for value in english if value not in COMMON_TERMS and not value.startswith(("http://", "https://"))]
    chinese = []
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        chinese.extend(chunk[index:index + 2] for index in range(len(chunk) - 1))
    budget = max(4, math.ceil(math.log2(max(source_size, 2))) * 2)
    ranked_english = [value for value, _ in sorted(Counter(english).items(), key=lambda pair: (-pair[1], pair[0]))[:budget]]
    ranked_chinese = [value for value, _ in sorted(Counter(chinese).items(), key=lambda pair: (-pair[1], pair[0]))[:budget]]
    return ranked_english + ranked_chinese


def extract_text_facts(text: str) -> dict:
    size = len(text.splitlines())
    return {
        "headings": adaptive_take(re.findall(r"(?m)^#{1,6}\s+(.{1,160})$", text), size),
        "symbols": adaptive_take(re.findall(r"(?m)^(?:export\s+)?(?:async\s+)?(?:def|class|function|interface|type|enum|const)\s+([A-Za-z_$][\w$]*)", text), size),
        "imports": adaptive_take(re.findall(r"(?m)^(?:import\s+.+?from\s+|from\s+|require\s*\()['\"]?([^'\"\s;)]+)", text), size),
        "links": adaptive_take(re.findall(r"\[[^\]]+\]\(([^)]+)\)", text), size),
        "keywords": extract_keywords(text, size),
    }


def representative_bytes(path: Path, size: int) -> bytes:
    window = max(8192, math.ceil(math.sqrt(max(size, 1))) * 2)
    if size <= window * 3:
        return path.read_bytes()
    with path.open("rb") as handle:
        first = handle.read(window)
        handle.seek(max(0, size // 2 - window // 2)); middle = handle.read(window)
        handle.seek(max(0, size - window)); last = handle.read(window)
    return first + b"\n\n[...middle sample...]\n\n" + middle + b"\n\n[...end sample...]\n\n" + last


def path_terms(text: str) -> set[str]:
    values = {term.lower() for term in re.findall(r"[A-Za-z0-9_$-]{2,}|[\u4e00-\u9fff]{2,}", text)}
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        values.update(chunk[index:index + 2] for index in range(len(chunk) - 1))
    return values


def authority(record: dict, question_terms: set[str]) -> float:
    path = record["path"]
    name = Path(path).name.lower()
    score = AUTHORITY_NAMES.get(name, 0) + 24 / (record["depth"] + 1)
    lowered = path.lower()
    if any(word in lowered for word in ("architecture", "overview", "design", "docs", "guide", "requirements", "spec", "rfc")): score += 28
    if Path(path).stem.lower() in {"main", "index", "page", "app", "server", "cli"}: score += 24
    if record["kind"] == "document": score += 18
    if question_terms & path_terms(path): score += 72
    return score


def choose_samples(records: list[dict], mode: str, question: str) -> list[dict]:
    if len(records) <= 1: return records
    budget = max(1, math.ceil(math.log2(len(records) + 1)) * MODE_DETAIL[mode])
    question_terms = path_terms(question)
    candidates = []
    for record in records:
        suffix = Path(record["path"]).suffix.lower()
        question_match = bool(question_terms & path_terms(record["path"]))
        if record["kind"] in {"source", "document", "config"} or (record["kind"] == "rich-document" and suffix in {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx"} and (record["depth"] <= 1 or question_match)) or question_match:
            candidates.append(record)
    ranked = sorted(candidates, key=lambda record: (-authority(record, question_terms), record["depth"], record["path"]))
    selected, seen_areas = [], set()
    mandatory = [record for record in ranked if record["depth"] <= 1 and AUTHORITY_NAMES.get(Path(record["path"]).name.lower(), 0) >= 90]
    for record in mandatory:
        if record not in selected: selected.append(record)
    for record in ranked:
        if len(selected) >= budget: break
        if record not in selected and record["area"] not in seen_areas:
            selected.append(record); seen_areas.add(record["area"])
    for record in ranked:
        if len(selected) >= budget: break
        if record not in selected: selected.append(record)
    return selected


def compress_areas(records: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for record in records: grouped.setdefault(record["area"], []).append(record)
    summaries = [{"path":area, "files":len(items), "bytes":sum(item["bytes"] for item in items), "kinds":dict(Counter(item["kind"] for item in items))} for area, items in grouped.items()]
    summaries.sort(key=lambda item: (-item["files"], item["path"]))
    detail = max(1, math.ceil(math.log2(len(records) + 1)))
    if len(summaries) <= detail: return summaries
    shown, rest = summaries[:detail], summaries[detail:]
    shown.append({"path":"…other areas", "areas":len(rest), "files":sum(item["files"] for item in rest), "bytes":sum(item["bytes"] for item in rest)})
    return shown


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    parser.add_argument("--mode", choices=MODE_DETAIL, default="lite")
    parser.add_argument("--question", default="")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    target = args.target.resolve()
    if not target.exists(): parser.error(f"target does not exist: {target}")

    records = []
    for path in iter_files(target):
        rel = path.name if target.is_file() else str(path.relative_to(target))
        stat = path.stat(); parts = Path(rel).parts
        records.append({"path":rel, "kind":classify(path), "bytes":stat.st_size, "mtime_ns":stat.st_mtime_ns, "depth":len(parts) - 1, "area":parts[0] if len(parts) > 1 else "."})

    detailed = []
    for record in choose_samples(records, args.mode, args.question):
        path = target if target.is_file() else target / record["path"]
        item = dict(record)
        if record["kind"] in {"source", "document", "config"}:
            raw = representative_bytes(path, record["bytes"])
            item["sha256"] = digest(raw + f":{record['bytes']}:{record['mtime_ns']}".encode())
            item["fingerprint_kind"] = "representative-content+metadata"
            item.update(extract_text_facts(raw.decode("utf-8", errors="replace")))
        elif record["kind"] == "rich-document":
            item["requires_specialized_extractor"] = True
            item["fingerprint"] = digest(f"{record['path']}:{record['bytes']}:{record['mtime_ns']}".encode())
        detailed.append(item)

    inventory_fingerprint = digest("\n".join(f"{r['path']}:{r['bytes']}:{r['mtime_ns']}" for r in records).encode())
    primary_documents = [item["path"] for item in detailed if item["kind"] in {"document", "config"}]
    entrypoints = [item["path"] for item in detailed if Path(item["path"]).stem.lower() in {"main", "index", "page", "app", "server", "cli"}]
    result = {
        "version":"2.0", "target":str(target), "mode":args.mode, "question":args.question or None,
        "fingerprint":inventory_fingerprint,
        "coverage":{"structure_scanned":len(records), "content_sampled":len(detailed), "strategy":"complete metadata inventory → authority + structural diversity + question relevance"},
        "inventory":{"bytes":sum(record["bytes"] for record in records), "kinds":dict(Counter(record["kind"] for record in records)), "extensions":dict(Counter(Path(record["path"]).suffix.lower() or "[none]" for record in records))},
        "areas":compress_areas(records), "orientation":{"primary_documents":primary_documents, "likely_entrypoints":entrypoints}, "files":detailed,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(rendered, encoding="utf-8")
    else: print(rendered, end="")
    return 0


if __name__ == "__main__": raise SystemExit(main())
