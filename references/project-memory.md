# Lightweight Project Memory

The purpose of memory is fast, precise follow-up answers—not conversational autobiography.

## Structure

`.visual-model/memory.json` stores small evidence-backed items and four orthogonal edge sets inspired by MAGMA:

- **semantic:** items share meaningful normalized terms or categories;
- **temporal:** source revisions order items or mark newer evidence;
- **causal:** manifest flow connects producers, transformations, state changes, and consumers;
- **entity:** components, files, symbols, ports, and modes refer to the same named entity.

Every item includes an ID, compact text, kind, source references, confidence, and source fingerprint. The implementation is deliberately local, deterministic, and dependency-free; it is not a vector database and does not claim semantic equivalence to the MAGMA research system.

Build and query without loading the files into model context:

```bash
python3 scripts/project_memory.py build --evidence .visual-model/evidence-index.json --manifest .visual-model/model.json --output .visual-model/memory.json
python3 scripts/project_memory.py update .visual-model/memory.json --evidence .visual-model/evidence-index.json --manifest .visual-model/model.json
python3 scripts/project_memory.py query .visual-model/memory.json "<question>" --evidence .visual-model/evidence-index.json
```

`stale: true` means relevant evidence must be refreshed before answering.

## Write policy

Store validated component responsibilities and interfaces, source-backed relationships and modes, deliberate simplifications, resolved uncertainties, important decisions, and fingerprints required to detect staleness.

Do not store secrets, credentials, personal data, unrelated content, raw chats, long source passages, generated/vendor/cache files, or unsupported hypotheses.

## Retrieval policy

- “why/how/impact/flow” favors causal edges.
- “when/latest/changed” favors temporal edges.
- Exact file, symbol, component, or mode names favor entity edges.
- Conceptual questions favor semantic edges.

Return a small evidence bundle with confidence and source references. Expand one hop only when the first bundle cannot answer the question. Open raw sources only for verification or unresolved details.

When `matched` is false, do not substitute unrelated graph neighbors. Use `needs_source_lookup` as the signal to inspect a narrowly selected source slice, then refresh the evidence and memory if the missing fact is worth retaining.

## Lifecycle

Run `update` after refreshing evidence. It reuses byte-identical memory items, recomputes semantic edges only for added or changed items, removes retired items from active retrieval, and refreshes causal, temporal, and entity edges from current evidence. A no-op update does not rewrite the memory file. The command returns added, updated, removed, unchanged, graph-change, and revision information.

Stable IDs survive unchanged content. Retain old facts only when explicitly stored as historical evidence; never mix superseded facts into the active answer bundle.
