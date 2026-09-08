# Interaction and Rendering Playbook

Apply this reference when the deliverable is an interactive webpage or rendered scene.

## Architecture

Keep these concerns separate:

- `model`: components, ports, edges, modes, explanations, formulas, and shapes;
- `layout`: positions, sizes, routing anchors, focus targets, and scale mapping;
- `scene`: geometry and object IDs;
- `flow`: paths derived from edges and mode state;
- `camera`: overview, focus, reset, and navigation rail;
- `overlay`: legend, mode controls, trace controls, navigation, and detail panels;
- `preview`: isolated component rendering based on the same visual encoding;
- `audit`: invariant and cross-surface checks.

In React projects, keep the model data framework-agnostic. Use React Three Fiber or another existing scene layer only when it fits the project; do not migrate a working renderer without need.

## Camera and focus

- Frame the complete topology on reset.
- Focus on a component's semantic center, not merely its mesh origin.
- Reserve screen space for the detail panel by offsetting the camera projection or target; do not cover the focused object.
- Keep local upstream and downstream ports visible when they explain the component.
- Hide unrelated annotations during focus.
- If the architecture is longer than one viewport, provide a continuous pan/scrubber that navigates without opening component details.
- Give the scrubber's region label from the actual camera position and component bounds.

## Labels and overlays

- Use HTML overlays for readable teaching copy and accessible controls.
- Use a consistent type scale.
- Place concise labels near the geometry and long explanations in a panel.
- Scope labels to the current component during focus.
- Prevent label stacks from hiding ports, animation junctions, or the traced item.
- Keep scene label names, navigation names, and panel titles sourced from the same metadata.

## Flow rendering

Derive paths from edge source and target anchors. Each path must have:

- referenced edge ID;
- direction;
- payload;
- active modes;
- visual style; and
- trace eligibility.

Particles show movement; continuous lines show topology; a hybrid shows both. Switching styles must not change the graph. For parallel lanes, animate the real number of pedagogical lanes or state the aggregation ratio. For large cardinalities, use representative bundles plus an explicit count.

Avoid:

- particles that loop through a component in the wrong order;
- one animated line standing in for several semantically different paths without a bundle label;
- construction edges that glow like data;
- animation through disabled, masked, or cached-only paths;
- decorative pulses that imply computation where none occurs.

## Modes and tracing

Represent mode behavior as data. A mode selects component state, edge state, labels, timing, and state-store behavior. Tracing selects one item from the currently valid execution without rewriting the topology.

If the traced item is inactive in the current mode, say so or move the simulation to the corresponding step. Do not show a trace traversing an inactive edge while the surrounding component claims it is disabled.

## Isolated previews

An isolated component preview should include only:

- the component shell or operator;
- required input/output anchors;
- its internal operation order;
- a small number of scoped labels; and
- the same colors, materials, and geometry meaning as the main scene.

Do not introduce a simplified preview that changes the operation. A preview of dense projection should not become a set of fixed local merges.

## Performance

- Instance repeated geometry and particles.
- Memoize curves and custom geometry; dispose resources.
- Keep bloom selective and subordinate to legibility.
- Limit expensive postprocessing on mobile or low-power devices.
- Avoid hundreds of DOM-backed labels.
- Test interaction while animations run, not only in a static frame.

## Accessibility and fallback

- Mirror canvas picking with keyboard-accessible navigation controls.
- Give every control an accessible name and visible focus state.
- Respect reduced motion.
- Preserve explanations and component navigation when WebGL is unavailable.
- Do not encode role only by color; pair color with labels, position, or shape.
