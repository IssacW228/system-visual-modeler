# Modes and Evidence Budgets

Use budgets as stopping rules for evidence collection, not as guarantees about provider billing.

| Mode | Structural scan | Content reading | Model detail | Visual QA | Memory |
|---|---|---|---|---|---|
| lite | complete metadata inventory | adaptive project docs, entry points, and question-relevant samples | only the major structure needed for orientation | static sanity check | none |
| normal | complete inventory plus relationship candidates | evidence selected by manifest needs | inspectable components and one representative trace | overview + hardest focus | required |
| deep | complete inventory plus domain-specific extraction | evidence selected by unresolved semantics | fidelity-driven; no preset size | full audit | required |

Do not use a fixed file or node count as a stopping rule. Adapt detail to project scale, structural diversity, document authority, entry-point proximity, and direct relevance to the user's question. Separate “structure scanned” from “content sampled” so broad coverage never implies that every file was semantically read.

## Progressive delivery

For normal or deep work on a large input:

1. Produce the evidence index and a topology sketch first.
2. Resolve the highest-impact uncertainties.
3. Make the first usable model available.
4. Add deeper inspection, modes, memory, and audit without replacing stable IDs.

Prefer deterministic extraction and compact JSON over copying raw content into context. Run scripts without reading their implementations unless they fail or require modification.
