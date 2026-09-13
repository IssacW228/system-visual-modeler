# Reusable Web Model Kit

Use `assets/web-model-kit/` as the default React shell for `normal` and `deep` web models when the host project has no equivalent component system. Copy the three files into the host project's component directory, preserve its existing dependency and styling conventions, then compose domain-specific geometry inside `VisualWorkbench`.

## Included primitives

- `VisualWorkbench`: fixed header, tool rail, model canvas, optional utility panel, optional inspector, and optional component rail.
- `useExclusiveSurface`: one state value for mutually exclusive tools and component detail surfaces.
- `usePanZoomViewport`: dependency-free drag, pointer-centered wheel zoom, button zoom, keyboard pan, and reset state.
- `ViewportSurface`: keyboard-focusable, touch-safe viewport that keeps panning and zooming active while an inspector is open.
- `ViewportControls`: reusable viewport status and controls with an optional contextual hint slot.
- `PopoverCard`: anchored, dismissible contextual guidance for small secondary explanations.
- `DialogModal`: focus-aware modal with backdrop click, Escape dismissal, visible close action, and optional footer actions.
- `ModeSwitch`: data-driven overview, trace, comparison, or other semantic modes.
- `UtilityRail`: compact secondary actions with accessible names and pressed/expanded state.
- `SurfaceHeader`: consistent title and close affordance for a panel.
- `ComponentRail`: keyboard-accessible component navigation outside the canvas.
- `InspectorSection`: repeatable fact, explanation, warning, or invariant groups.

## Layout contract

Panels are grid tracks, not overlays. Opening a utility or inspector reduces the canvas track, so explanatory UI cannot cover nodes, ports, or paths. On narrow viewports the active surface becomes a separate bottom track. Keep only one primary surface open by using `useExclusiveSurface`; Escape and visible close buttons dismiss it.

Small contextual help may use `PopoverCard` from a reserved toolbar zone. Longer explanations use `DialogModal`; component facts remain in the non-overlapping inspector. Opening any of these surfaces must not permanently lock or reset the viewport.

The shell owns chrome and layout only. The model manifest remains the source of labels, components, modes, and relationships. Domain-specific nodes, SVG, Canvas, WebGL, or other scene content belongs inside the `VisualWorkbench` canvas slot.

## Adaptation rules

1. Reuse host typography and tokens when they already meet contrast and hierarchy needs.
2. Keep `aria-label`, `aria-pressed`, `aria-expanded`, and focus behavior when restyling.
3. Preserve the separate layout tracks; do not convert the inspector or utility panel to an absolute layer.
4. Keep the component rail optional for small models.
5. Keep drag, wheel zoom, zoom controls, reset, and keyboard pan available after opening component details.
6. If 3D is justified, reserve camera safe space using the resulting canvas bounds rather than hard-coded screen offsets.
7. For Lite, do not copy the full shell unless a webpage is explicitly requested; a compact 2D artifact remains the faster default.

## Minimal composition

```tsx
const surfaces = useExclusiveSurface();
const selected = surfaces.activeSurface?.startsWith("node:")
  ? surfaces.activeSurface.slice(5)
  : null;

<VisualWorkbench
  eyebrow="SYSTEM MODEL"
  title={manifest.title}
  modes={manifest.modes}
  activeMode={mode}
  onModeChange={setMode}
  onReset={reset}
  utilities={utilities}
  activeUtility={null}
  onUtilityChange={(id) => id ? surfaces.open(`tool:${id}`) : surfaces.close()}
  onDismissSurface={surfaces.close}
  inspector={selected ? <ComponentInspector id={selected} /> : null}
>
  <ModelCanvas manifest={manifest} onSelect={(id) => surfaces.open(`node:${id}`)} />
</VisualWorkbench>
```
