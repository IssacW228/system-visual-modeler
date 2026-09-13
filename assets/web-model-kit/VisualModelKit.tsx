"use client";

import type { CSSProperties, KeyboardEvent as ReactKeyboardEvent, PointerEvent as ReactPointerEvent, ReactNode, WheelEvent as ReactWheelEvent } from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import type { RailItem, UtilityItem, VisualModeOption } from "./types";
import styles from "./visual-model-kit.module.css";

export function useExclusiveSurface(initial: string | null = null) {
  const [activeSurface, setActiveSurface] = useState<string | null>(initial);
  const open = useCallback((id: string) => setActiveSurface(id), []);
  const toggle = useCallback((id: string) => setActiveSurface((current) => current === id ? null : id), []);
  const close = useCallback(() => setActiveSurface(null), []);
  return { activeSurface, open, toggle, close };
}

export function usePanZoomViewport({ minScale = .55, maxScale = 1.8, step = .15, initialScale = 1 } = {}) {
  const [view, setView] = useState({ x:0, y:0, scale:initialScale });
  const [isDragging, setDragging] = useState(false);
  const drag = useRef({ pointerId:-1, x:0, y:0 });
  const clamp = useCallback((value:number) => Math.min(maxScale, Math.max(minScale, value)), [maxScale, minScale]);
  const reset = useCallback(() => setView({ x:0, y:0, scale:clamp(initialScale) }), [clamp, initialScale]);
  const panBy = useCallback((x:number, y:number) => setView(current => ({ ...current, x:current.x + x, y:current.y + y })), []);
  const zoomTo = useCallback((scale:number) => setView(current => ({ ...current, scale:clamp(scale) })), [clamp]);
  const zoomIn = useCallback(() => setView(current => ({ ...current, scale:clamp(current.scale + step) })), [clamp, step]);
  const zoomOut = useCallback(() => setView(current => ({ ...current, scale:clamp(current.scale - step) })), [clamp, step]);
  const onPointerDown = useCallback((event:ReactPointerEvent<HTMLDivElement>) => {
    if (event.button !== 0 || (event.target as HTMLElement).closest("button, a, input, select, textarea, [data-no-pan]")) return;
    drag.current = { pointerId:event.pointerId, x:event.clientX, y:event.clientY };
    event.currentTarget.setPointerCapture(event.pointerId);
    setDragging(true);
  }, []);
  const onPointerMove = useCallback((event:ReactPointerEvent<HTMLDivElement>) => {
    if (drag.current.pointerId !== event.pointerId) return;
    const nextX = event.clientX, nextY = event.clientY;
    panBy(nextX - drag.current.x, nextY - drag.current.y);
    drag.current = { pointerId:event.pointerId, x:nextX, y:nextY };
  }, [panBy]);
  const stopDragging = useCallback((event:ReactPointerEvent<HTMLDivElement>) => {
    if (drag.current.pointerId !== event.pointerId) return;
    drag.current.pointerId = -1;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
    setDragging(false);
  }, []);
  const onWheel = useCallback((event:ReactWheelEvent<HTMLDivElement>) => {
    event.preventDefault();
    const rect = event.currentTarget.getBoundingClientRect();
    const anchorX = event.clientX - rect.left - rect.width / 2;
    const anchorY = event.clientY - rect.top - rect.height / 2;
    setView(current => {
      const nextScale = clamp(current.scale * (event.deltaY > 0 ? .9 : 1.1));
      const ratio = nextScale / current.scale;
      return { scale:nextScale, x:anchorX - (anchorX - current.x) * ratio, y:anchorY - (anchorY - current.y) * ratio };
    });
  }, [clamp]);
  const onKeyDown = useCallback((event:ReactKeyboardEvent<HTMLDivElement>) => {
    const movement:Record<string,[number,number]> = { ArrowLeft:[-32,0], ArrowRight:[32,0], ArrowUp:[0,-32], ArrowDown:[0,32] };
    if (movement[event.key]) { event.preventDefault(); panBy(...movement[event.key]); }
    if (event.key === "+" || event.key === "=") { event.preventDefault(); zoomIn(); }
    if (event.key === "-") { event.preventDefault(); zoomOut(); }
    if (event.key === "0") { event.preventDefault(); reset(); }
  }, [panBy, reset, zoomIn, zoomOut]);
  return { view, isDragging, minScale, maxScale, reset, panBy, zoomTo, zoomIn, zoomOut, onPointerDown, onPointerMove, onPointerUp:stopDragging, onPointerCancel:stopDragging, onWheel, onKeyDown };
}

export function VisualWorkbench({
  eyebrow, title, status, modes, activeMode, onModeChange, onReset,
  utilities, activeUtility, onUtilityChange, utilityPanel, canvasToolbar,
  inspector, rail, children, onDismissSurface, accent = "#d6ff55",
}: {
  eyebrow: string;
  title: string;
  status?: string;
  modes: VisualModeOption[];
  activeMode: string;
  onModeChange: (id: string) => void;
  onReset: () => void;
  utilities: UtilityItem[];
  activeUtility?: string | null;
  onUtilityChange: (id: string) => void;
  onDismissSurface: () => void;
  utilityPanel?: ReactNode;
  canvasToolbar?: ReactNode;
  inspector?: ReactNode;
  rail?: ReactNode;
  children: ReactNode;
  accent?: string;
}) {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape" && (activeUtility || inspector)) onDismissSurface();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [activeUtility, inspector, onDismissSurface]);

  return (
    <main
      className={styles.workbench}
      data-utility-open={Boolean(activeUtility)}
      data-inspector-open={Boolean(inspector)}
      style={{ "--vm-accent": accent } as CSSProperties}
    >
      <header className={styles.header}>
        <div className={styles.identity}><small>{eyebrow}</small><h1>{title}</h1>{status && <span>{status}</span>}</div>
        <ModeSwitch options={modes} value={activeMode} onChange={onModeChange} />
        <button type="button" className={styles.reset} onClick={onReset}>重置视图</button>
      </header>
      <div className={styles.workspace}>
        <UtilityRail items={utilities} activeId={activeUtility ?? null} onChange={onUtilityChange} />
        {activeUtility && utilityPanel && <aside className={styles.utilityPanel} aria-label={`${utilities.find(item => item.id === activeUtility)?.label ?? "工具"}面板`}>{utilityPanel}</aside>}
        <section className={styles.canvas} aria-label="模型画布">
          {canvasToolbar && <div className={styles.canvasToolbar}>{canvasToolbar}</div>}
          <div className={styles.canvasInner}>{children}</div>
        </section>
        {inspector && <aside className={styles.inspector} aria-label="组件详情">{inspector}</aside>}
      </div>
      {rail && <div className={styles.railSlot}>{rail}</div>}
    </main>
  );
}

export function ViewportSurface({ controller, children, label = "可移动模型视口" }: {
  controller: ReturnType<typeof usePanZoomViewport>;
  children: ReactNode;
  label?: string;
}) {
  return <div
    className={styles.viewport}
    data-dragging={controller.isDragging}
    aria-label={label}
    tabIndex={0}
    onPointerDown={controller.onPointerDown}
    onPointerMove={controller.onPointerMove}
    onPointerUp={controller.onPointerUp}
    onPointerCancel={controller.onPointerCancel}
    onWheel={controller.onWheel}
    onKeyDown={controller.onKeyDown}
  >
    <div className={styles.viewportStage} style={{ transform:`translate3d(${controller.view.x}px, ${controller.view.y}px, 0) scale(${controller.view.scale})` }}>{children}</div>
  </div>;
}

export function ViewportControls({ controller, onHint, hintOpen = false, hint }: {
  controller: ReturnType<typeof usePanZoomViewport>;
  onHint?: () => void;
  hintOpen?: boolean;
  hint?: ReactNode;
}) {
  return <div className={styles.viewportControls} aria-label="视角控制">
    <div className={styles.gestureLabel}><span>DRAG TO EXPLORE</span><b>拖拽平移 · 滚轮缩放</b></div>
    <div className={styles.controlButtons}>
      <button type="button" onClick={controller.zoomOut} aria-label="缩小视角">−</button>
      <output aria-label="当前缩放比例">{Math.round(controller.view.scale * 100)}%</output>
      <button type="button" onClick={controller.zoomIn} aria-label="放大视角">＋</button>
      <button type="button" onClick={controller.reset} aria-label="重置视角">⌖</button>
      {onHint && <button type="button" aria-label="查看操作提示" aria-expanded={hintOpen} onClick={onHint}>?</button>}
      {hint}
    </div>
  </div>;
}

export function PopoverCard({ eyebrow, title, children, onClose }: { eyebrow:string; title:string; children:ReactNode; onClose:() => void }) {
  return <section className={styles.popoverCard} role="dialog" aria-label={title}>
    <SurfaceHeader eyebrow={eyebrow} title={title} onClose={onClose}/>
    <div className={styles.popoverBody}>{children}</div>
  </section>;
}

export function DialogModal({ eyebrow, title, children, onClose, actions }: { eyebrow:string; title:string; children:ReactNode; onClose:() => void; actions?:ReactNode }) {
  const closeRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    const onKey = (event:KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => { window.removeEventListener("keydown", onKey); previous?.focus(); };
  }, [onClose]);
  return <div className={styles.modalBackdrop} role="presentation" onMouseDown={event => event.target === event.currentTarget && onClose()}>
    <section className={styles.modalDialog} role="dialog" aria-modal="true" aria-label={title}>
      <header className={styles.modalHeader}><div><small>{eyebrow}</small><h2>{title}</h2></div><button ref={closeRef} type="button" onClick={onClose} aria-label={`关闭${title}`}>×</button></header>
      <div className={styles.modalBody}>{children}</div>
      {actions && <footer className={styles.modalActions}>{actions}</footer>}
    </section>
  </div>;
}

export function ModeSwitch({ options, value, onChange }: { options: VisualModeOption[]; value: string; onChange: (id: string) => void }) {
  return <div className={styles.modeSwitch} role="group" aria-label="模型模式">{options.map(option => <button type="button" key={option.id} aria-pressed={value === option.id} onClick={() => onChange(option.id)}><small>{option.shortLabel}</small>{option.label}</button>)}</div>;
}

export function UtilityRail({ items, activeId, onChange }: { items: UtilityItem[]; activeId: string | null; onChange: (id: string) => void }) {
  return <nav className={styles.utilityRail} aria-label="模型工具">{items.map(item => <button type="button" key={item.id} aria-label={item.label} aria-expanded={activeId === item.id} aria-pressed={activeId === item.id} onClick={() => onChange(activeId === item.id ? "" : item.id)}>{item.icon}<span>{item.label}</span></button>)}</nav>;
}

export function SurfaceHeader({ eyebrow, title, onClose }: { eyebrow: string; title: string; onClose: () => void }) {
  return <header className={styles.surfaceHeader}><div><small>{eyebrow}</small><h2>{title}</h2></div><button type="button" onClick={onClose} aria-label={`关闭${title}`}>×</button></header>;
}

export function ComponentRail({ items, activeId, onSelect }: { items: RailItem[]; activeId?: string | null; onSelect: (id: string) => void }) {
  return <nav className={styles.componentRail} aria-label="组件导航">{items.map(item => <button type="button" key={item.id} aria-current={activeId === item.id ? "true" : undefined} onClick={() => onSelect(item.id)}><i style={{ background:item.accent ?? "var(--vm-accent)" }}/>{item.index && <small>{item.index}</small>}<span>{item.label}</span></button>)}</nav>;
}

export function InspectorSection({ label, children, tone = "default" }: { label: string; children: ReactNode; tone?: "default" | "warning" }) {
  return <section className={tone === "warning" ? styles.warningSection : styles.inspectorSection}><small>{label}</small>{children}</section>;
}
