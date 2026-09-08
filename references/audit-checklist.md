# Semantic Audit Checklist

Audit from ground truth outward. Record deliberate abstraction rather than treating it as a defect.

## Per-component matrix

For every component verify:

| Surface | Questions |
|---|---|
| Identity | Do scene label, navigation label, panel title, preview, and component ID identify the same operation? |
| Position | Is it placed before and after the correct neighbors? Are branches and bypasses physically aligned? |
| Ports | Are all real inputs and outputs present, directed correctly, and named consistently? |
| Shape/type | Do displayed dimensions, lane counts, widths, and panel shapes agree? |
| Operation | Does the geometry depict split, branch, broadcast, concat, add, reduce, project, gate, cache, or loop correctly? |
| Flow | Does every animation enter, traverse, and leave in the true order? |
| Formula/code | Does it use the same inputs and outputs as the visual? Are all symbols or identifiers explained? |
| Modes | Does visibility, activity, timing, and state behavior match each mode? |
| Preview | Does the isolated model preserve the same semantics and encoding? |

## Cross-component invariants

- Every edge terminates at a compatible port or declares a transform.
- A bypass starts before the skipped operation and joins at the correct merge.
- A repeated block preserves the required external contract.
- Shared versus independent parameters and state are explicitly correct.
- Cache reads and writes belong to the correct layer, instance, user, or request.
- Quantitative encodings use one declared scale or an explicitly labeled compression.
- Branch widths are not summed unless a concatenate operation exists.
- Elementwise operations receive aligned shapes.
- Dense transforms are not drawn as arbitrary fixed groups.
- Disabled or masked paths do not carry active flow.
- Feedback paths state what changes and when they stop.

## Visual ambiguity scan

Look for elements a learner could mistake for architecture:

- wireframe diagonals;
- bounding-box edges;
- floor grids crossing ports;
- bloom streaks;
- decorative cables;
- overlapping transparent shells;
- labels pointing at the wrong object;
- lines that cross without a junction marker;
- identical colors used for unrelated payloads;
- identical shapes used for semantically different operators.

Remove, restyle, or explain ambiguous elements. Decorative geometry should never be more visually salient than a real edge.

## Interaction audit

- Every listed component can be focused.
- Clicking geometry and using navigation select the same ID.
- Focus keeps the object visible beside the panel.
- Unrelated labels disappear during focus.
- Reset restores the full model.
- Spatial navigation does not accidentally open details.
- Region labels match the actual position.
- Trace controls produce a valid path in every mode.
- Closing a panel does not corrupt camera or mode state.

## Handoff evidence

Before completion:

1. Validate the manifest if present.
2. Run the project's build or equivalent verification.
3. Check the overview.
4. Focus the most complex component and inspect its panel and preview.
5. Switch every operating mode.
6. Exercise one complete trace.
7. Check runtime errors.

Report discovered mismatches and the corrections made. If browser testing or a required runtime is unavailable, state exactly which checks remain unverified.
