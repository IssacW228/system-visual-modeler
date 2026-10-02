# Modes and Evidence Budgets

Use budgets as stopping rules for evidence collection, not as guarantees about provider billing.

| Mode | Structural scan | Content reading | Model detail | Visual QA | Memory |
|---|---|---|---|---|---|
| lite | complete metadata inventory | adaptive project docs, entry points, and question-relevant samples | only the major structure needed for orientation | static sanity check | none |
| normal | complete inventory plus relationship candidates | evidence selected by manifest needs | inspectable components and one representative trace | overview + hardest focus | required |
| deep | complete inventory plus domain-specific extraction | evidence selected by unresolved semantics | fidelity-driven; no preset size | full audit | required |

All modes share one inventory and one exclusion policy: `.gitignore`, dependency/build/cache directories, and secret-like files (`.env*`, private keys) are excluded everywhere; hidden project configuration such as `.github/` is inventoried everywhere. Lite stays light only through its smaller content-sampling budget and by down-ranking hidden paths unless the question names them. Never add a lite-only exclusion: it would make lite blind to structure that normal and deep can see, and anything lite leaves unread must still be visible as "found, not read".

Do not use a fixed file or node count as a stopping rule. Adapt detail to project scale, structural diversity, document authority, entry-point proximity, and direct relevance to the user's question. Separate “structure scanned” from “content sampled” so broad coverage never implies that every file was semantically read.

## Progressive delivery

For normal or deep work on a large input:

1. Produce the evidence index and a topology sketch first.
2. Resolve the highest-impact uncertainties.
3. Make the first usable model available.
4. Add deeper inspection, modes, memory, and audit without replacing stable IDs.

Prefer deterministic extraction and compact JSON over copying raw content into context. Run scripts without reading their implementations unless they fail or require modification.
