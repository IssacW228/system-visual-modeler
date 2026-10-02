---
name: system-visual-modeler
description: "Rapidly turn a folder, document, codebase, workflow, architecture, algorithm, or mathematical pipeline into a faithful 2D, 2.5D, or 3D interactive model. Use for quick structural decomposition, mechanism tracing, visual explanation, or a polished inspectable web model; not for decorative scenes or ordinary dashboards."
---

# System Visual Modeler

Build the smallest visual model that answers how the subject is structured or behaves. Start fast, preserve evidence, and deepen only when requested or necessary.

## Runtime paths and invocation

This skill runs in Claude Code and Codex. Bundled `scripts/`, `references/`, and `assets/` paths are relative to the skill directory, not to the user's project. In Claude Code the skill directory is `${CLAUDE_SKILL_DIR}`; elsewhere it is the directory containing this `SKILL.md`. Run scripts with that prefix and keep the user's project as the working directory, for example:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/scan_evidence.py" . --mode lite --question "<question>" --output .visual-model/evidence-index.json
```

Scripts need only Python 3.9+ and the standard library. Write outputs under the user's project in `.visual-model/`, never inside the skill directory.

Arguments from a slash invocation (`/system-visual-modeler <target> [lite|normal|deep] [question]`), if any: $ARGUMENTS. Treat a path as the target, a mode word as the explicit weight, and the remaining text as the question. With no arguments, model the current project or the subject named in the conversation.

## Choose weight before reading deeply

Use an explicit user choice. Otherwise infer the lightest sufficient mode:

| Mode | Use when | Default result |
|---|---|---|
| `lite` | quick orientation at any input scale, one question, or no polished artifact requested | adaptive evidence index + compact 2D overview of the major structure |
| `normal` | interactive model, teaching explanation, project/folder analysis, or follow-up questions expected | typed manifest + 2D/2.5D model + trace + project memory |
| `deep` | delivery-grade fidelity, multiple modes, complex state/tensors, or explicit audit/3D request | full manifest + justified 2D/2.5D/3D + complete audit + project memory |

Treat `standard` as an alias for `normal`. Do not ask which mode unless the choice materially changes cost or output; state the inferred mode briefly and proceed.

Read [references/modes-and-budgets.md](references/modes-and-budgets.md) only when scope is large, the mode is ambiguous, or a budget must be enforced.

## Intake: scan first, read second

For a local path, run `scripts/scan_evidence.py` before opening many files. Do not read the script source merely to use it. Exclude generated, vendored, cache, and binary content. In `lite`, scan the complete structural inventory, rank the project-level documentation and likely entry points, then read only those high-value samples. Do not stop at an arbitrary file count or return the first files encountered. Read only the compact index and the smallest cited source slices needed to resolve the user's question.

- For source trees, extract structure, symbols, imports, entry points, and candidate flows deterministically.
- For Markdown/text, extract hierarchy, links, repeated concepts, and procedural language.
- For PDF, Word, spreadsheet, slide, image, audio, or other rich formats, use the applicable format tool/skill for extraction; feed its concise output into the evidence index rather than teaching this skill every file format.
- If an input cannot be parsed, report it as unresolved instead of fabricating a relationship.

## Model truth

Resolve only the facts required by the selected mode: components, responsibility, ports or boundaries, payload/type/shape, directed relationships, state, operating differences, and visible invariants.

Every visible edge must correspond to evidence or be labeled as a hypothesis. Distinguish data, control, call, dependency, state, residual, feedback, and event flow. Preserve the physical differences between split, branch, broadcast, concatenate, reduce/add, dense projection, gate, cache, and loop.

For `normal` or `deep`, use a manifest as the single source of truth. Read [references/model-contract.md](references/model-contract.md) when creating or changing it, then run `scripts/validate_model.py` for JSON manifests. Read [references/domain-grammars.md](references/domain-grammars.md) only for the active domain section; use heading search rather than loading unrelated sections.

## Pick dimensionality by meaning

- **2D:** hierarchy, sequence, state machine, dependency, document structure, and fastest delivery.
- **2.5D:** visual hierarchy, containment, parallel lanes, or polished teaching views where text inspection remains primary. This is the normal interactive default.
- **3D:** only when depth encodes real parallelism, nesting, routing, spatial structure, scale, tensor axes, or state. Never use 3D as a quality badge.

Honor the user's requested dimension, but disclose when it adds no semantic information.

## Interaction and UI

For a webpage, preserve the existing stack and design system. Reuse a working renderer or template before writing a custom shell. For React work without an equivalent host component system, start from `assets/web-model-kit/`; read [references/web-component-kit.md](references/web-component-kit.md) when adapting it. Read [references/interaction-and-rendering.md](references/interaction-and-rendering.md) only for `normal`/`deep` interactive work.

UI must not cover the model:

- opening a detail panel must resize or offset the scene so the focused component and its local ports remain visible;
- opening a detail panel must not disable canvas drag, zoom, keyboard pan, or reset;
- secondary controls start collapsed and open as a popover, drawer, or modal;
- allow at most one primary explanatory surface open at a time;
- use collision-aware tooltips; reserve canvas-safe docking zones;
- on mobile, use a bottom sheet and pan the model into the remaining viewport;
- provide keyboard-accessible component navigation, reset, close, and reduced-motion behavior.

## Fast project memory for follow-up questions

In `normal` and `deep`, write `.visual-model/memory.json` unless the user forbids project-local artifacts. Build it with `scripts/project_memory.py` from the evidence index and manifest, then use its `update` command after evidence changes; unchanged items are reused and a no-op update does not rewrite the file. The memory is MAGMA-inspired but lightweight: each item can participate in semantic, temporal, causal, and entity graphs while retaining source references and confidence.

Before answering later questions about a modeled project:

1. If memory exists, run `scripts/project_memory.py query ...`; do not load the whole memory file.
2. Read only the returned evidence bundle and cited source slices.
3. Answer with source-grounded facts and distinguish inference from evidence.
4. If fingerprints are stale for relevant files, refresh the evidence and memory before answering.
5. Never store secrets, raw conversation history, generated/vendor files, or unsupported guesses.

Read [references/project-memory.md](references/project-memory.md) only when creating, updating, debugging, or explaining memory.

## Finish proportionally

- `lite`: validate paths and labels; deliver immediately with uncertainties.
- `normal`: exercise overview, one focus, one trace, each mode, and runtime errors.
- `deep`: read [references/audit-checklist.md](references/audit-checklist.md), audit every surface, and record deliberate simplifications.

Report the selected weight, dimensionality rationale, source coverage, memory location when created, and anything deliberately unresolved.
