---
name: system-visual-modeler
description: "Turn code execution, software architecture, agent workflows, algorithms, and mathematical or tensor pipelines into accurate, inspectable interactive visual models and explanatory web experiences. Use when a user wants to decompose a complex mechanism into spatial components, typed connections, dimensional encodings, animated flows, operating modes, formulas, and click-to-explain interactions. Do not use for decorative 3D scenes, ordinary dashboards, or diagrams where structural fidelity is not important."
---

# System Visual Modeler

Build a visual explanation that behaves like the system it represents. Treat visual fidelity as semantic correctness: position, width, branching, merging, animation, labels, and interaction must each correspond to a real relationship in the source model.

## Outcome

Deliver a model in which a learner can:

- understand the whole mechanism from an overview;
- follow one concrete item through every applicable path;
- inspect any component in context and in isolation;
- see inputs, outputs, dimensions or types, state, and direction of flow;
- connect the physical metaphor to formulas or source code; and
- switch operating modes without the visualization contradicting the underlying behavior.

The visual may be 2D, 2.5D, or 3D. Choose 3D only when depth materially clarifies parallelism, hierarchy, routing, containment, scale, or state. Preserve the user's requested stack and the existing product's design system.

## Start From Ground Truth

Inspect the authoritative material before choosing geometry. Depending on the task, this may be source code, architecture definitions, traces, schemas, equations, tensor shapes, protocol documentation, or user-provided specifications.

Resolve these facts:

1. Components and their responsibilities.
2. Input and output ports for each component.
3. Payload type, tensor shape, cardinality, or state at every port.
4. Directed connections and whether each is data, control, state, residual, feedback, dependency, call, or event flow.
5. Operations that preserve shape, split, branch, broadcast, aggregate, concatenate, reduce, project, cache, or mutate state.
6. Operating modes and which nodes, edges, or states differ between them.
7. Invariants that must remain visibly true.

Do not infer uncertain relationships from the desired appearance. Mark an unresolved relationship and investigate it before building the corresponding animation.

For a nontrivial project, create a visual-model manifest before implementing the scene. Read [references/model-contract.md](references/model-contract.md) for the contract and use `scripts/validate_model.py` when the manifest is JSON.

## Choose a Visual Grammar

Map one semantic property to one stable visual channel:

- spatial order for execution or transformation order;
- lanes or bundles for parallel channels;
- width, area, or repeated rails for meaningful cardinality or dimension;
- color for role or payload type, not arbitrary variety;
- enclosure for ownership, scope, layer, or cache;
- material for behavior, such as rigid residual paths versus active compute chambers;
- motion for actual direction and state transition;
- opacity for inactive, masked, unavailable, or historical state;
- repetition for real multiplicity.

Add an explicit legend whenever a viewer could reasonably interpret a visual channel in more than one way. If a quantitative scale is used, state it in the scene and keep it consistent. When exact proportional geometry becomes unreadable, use a declared nonlinear or compressed scale instead of silently distorting it.

Never let decorative lines resemble data edges. Wireframes, grids, bloom trails, braces, bounding boxes, and construction guides must either carry a named meaning or be visually subordinate and clearly different from flow paths.

Read [references/domain-grammars.md](references/domain-grammars.md) when selecting metaphors for code, system architecture, agents, algorithms, or mathematical pipelines.

## Preserve Operation Semantics

Use physically different visual actions for operations that are mathematically or architecturally different:

- **Split:** one payload is partitioned into disjoint parts.
- **Branch:** the same payload feeds multiple operations; branch widths do not add unless results are later concatenated.
- **Broadcast:** one value is reused across several consumers without being partitioned.
- **Concatenate:** ordered parts join along a named axis; show the resulting dimension.
- **Add or reduce:** inputs combine elementwise or through a reduction; show compatibility requirements.
- **Dense projection:** outputs mix the full input space. Do not depict it as fixed local grouping unless the real operator is grouped or sparse.
- **Gate:** expose the gate branch, activation location, content branch, and elementwise combination in their true order.
- **Cache or state:** show reads and writes separately, including ownership and lifetime.
- **Loop or feedback:** make the return path directional and identify what changes between iterations.

If a compact metaphor hides an essential distinction, add an intermediate state or a local exploded view rather than relying on prose to repair the picture.

## Build the Interaction Hierarchy

Provide three coordinated levels:

1. **Overview:** the complete topology, major stages, legend, mode selector, and a spatial navigation control when the model exceeds one viewport.
2. **Context focus:** click a component to fly the camera or pan the canvas so the component remains left of the explanation panel. Hide unrelated labels and keep only the current component's local annotations.
3. **Isolated component:** show the component alone with its ports, internal flow, operation order, and the same colors and geometry used in the main scene.

Every inspectable component should expose, when applicable:

- name and role;
- physical intuition;
- input and output types or shapes;
- formula, pseudocode, or source-code excerpt;
- definition of every symbol or important identifier;
- mode-specific behavior;
- state ownership and lifetime;
- visual legend and scale; and
- common misconception the model prevents.

Let the user trace one concrete token, request, variable, message, tensor row, or agent task through every real edge. A traced item may be highlighted without implying that other active items disappear. Offer particles, lines, or a restrained hybrid only when each representation follows the same validated paths.

Read [references/interaction-and-rendering.md](references/interaction-and-rendering.md) when implementing an interactive webpage or WebGL scene.

## Modes Must Change Behavior

A mode switch is not a copy switch. Define a state table showing, for each mode:

- active inputs;
- active components and edges;
- scheduling or concurrency;
- cache/state reads and writes;
- repeated or skipped computation;
- outputs; and
- animation timing.

Update the scene, trace behavior, labels, and detail explanation from the same mode data. Avoid separate hard-coded stories that can drift apart.

## Single Source of Truth

Drive the scene labels, navigation, detail panels, isolated previews, formulas, shapes, colors, focus coordinates, and mode copy from shared component metadata wherever practical. Component-specific geometry may remain code, but its visible semantics must be traceable to the manifest.

Use stable component IDs across the manifest, scene, UI, tests, and documentation. Model repeated components through instances of one definition plus explicit per-instance state or parameters.

## Implementation Guidance

- Extend a working project rather than replacing its architecture.
- Prefer accessible HTML controls and text overlays for explanations; use the canvas for the model itself.
- Use native geometry, curves, instancing, and shared materials before importing large bespoke assets.
- Separate geometry, animation paths, metadata, camera behavior, and UI state into focused modules.
- Use object picking with stable IDs, keyboard-accessible parallel navigation, smooth focus transitions, and a reset action.
- Keep labels readable under focus, zoom, and responsive layouts. Do not render all annotations simultaneously when they obscure the model.
- Animate representative data, not decorative noise. Pause or reduce motion when it competes with explanation.
- Respect reduced-motion preferences and provide a non-WebGL or textual fallback when the audience or product requires it.

## Audit Before Handoff

Perform a semantic audit after implementation and after every material visual change. Read [references/audit-checklist.md](references/audit-checklist.md).

At minimum, compare every component across:

```text
ground truth → manifest → geometry → flow animation → scene label
             → detail copy → formula/code → isolated preview → mode behavior
```

Correct mismatches in the model, not merely in the explanation. Then validate the project, exercise the primary interactions, and visually inspect at least the overview and the most complex focused component when browser testing is within scope.

Report the important visual decisions, the invariants verified, and any deliberate simplifications. Never claim exact dimensional or architectural fidelity when the model uses an undeclared approximation.
