# Visual Model Contract

Use a manifest to separate system truth from rendering code. JSON is recommended when validation or reuse matters; an equivalent typed object is acceptable when the project already has a strong type system.

Copy [example-manifest.json](example-manifest.json) when a concrete starting point is useful, then replace its domain data rather than preserving its example metaphors.

## Required concepts

### Project metadata

- `version`: contract version.
- `title`: learner-facing name.
- `subject`: code, architecture, agent, algorithm, formula, tensor pipeline, or another explicit domain.
- `orientation`: dominant reading direction.
- `scale`: quantitative visual scales and declared compressions.
- `legend`: stable meanings for colors, materials, line styles, and motion.

### Components

Each component needs:

- stable `id`, visible `index`, `title`, and `role`;
- `category` such as source, transform, router, state, merge, sink, or container;
- typed input/output `ports`;
- `operation` describing what changes and what is preserved;
- `visual` describing metaphor, geometry, encoding, and accent;
- `inspect` containing intuition, detailed explanation, shapes or types, and symbol definitions;
- mode overrides only where behavior actually changes.

Formulae are optional for systems without meaningful mathematics. Use pseudocode, an interface contract, or a source excerpt instead.

### Ports

A port should name:

- `id` local to its component;
- `direction`: `input`, `output`, or `inout`;
- `payload`: what moves through it;
- `shape`: tensor shape, collection cardinality, schema, type, or state contract;
- `magnitude`: optional numeric quantity used by a declared visual scale.

### Edges

Each edge needs:

- stable `id`;
- source component and source port;
- target component and target port;
- `kind`: data, control, state, residual, feedback, dependency, call, or event;
- payload and shape;
- a transform when source and target shapes differ;
- direction and optional mode availability.

Every animated path must reference a real edge. Construction lines and decorative geometry must not be registered as edges.

## Compact example

```json
{
  "version": "1.0",
  "title": "Request Processing Model",
  "subject": "software-architecture",
  "orientation": "left-to-right",
  "scale": {
    "throughput": "lane count is qualitative; values are labeled explicitly"
  },
  "legend": [
    { "channel": "cyan line", "meaning": "request data" },
    { "channel": "amber enclosure", "meaning": "persistent state" }
  ],
  "components": [
    {
      "id": "router",
      "index": "02",
      "title": "Request Router",
      "role": "Selects one worker without changing the request payload",
      "category": "router",
      "ports": [
        { "id": "request_in", "direction": "input", "payload": "Request", "shape": "Request" },
        { "id": "worker_out", "direction": "output", "payload": "Request", "shape": "Request" }
      ],
      "operation": {
        "kind": "route",
        "preserves": ["payload schema"],
        "changes": ["destination"]
      },
      "visual": {
        "metaphor": "switching junction",
        "geometry": "one inlet with multiple selectable outlets",
        "encoding": "the lit outlet is the selected destination"
      },
      "inspect": {
        "intuition": "A junction chooses where the unchanged request travels.",
        "details": "Routing does not split the request into smaller requests.",
        "symbols": []
      }
    }
  ],
  "edges": [],
  "modes": [],
  "flow_animations": []
}
```

## Shape-change rule

When an edge changes shape or type, state why:

```json
"transform": {
  "operation": "dense projection",
  "from": "[S, 16384]",
  "to": "[S, 4096]",
  "preserves": ["sequence axis"],
  "mixing": "every output feature depends on the full input feature axis"
}
```

Do not use a visual shortcut that contradicts this declaration.

## Repeated structures

Define one reusable component or block and instantiate it with:

- instance ID;
- position or layer index;
- independent/shared parameter policy;
- local state ownership; and
- any mode-specific override.

Repeated geometry must not imply shared parameters or shared state unless that is true.
