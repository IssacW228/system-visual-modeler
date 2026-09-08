#!/usr/bin/env python3
"""Validate a System Visual Modeler JSON manifest using only the standard library."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


EDGE_KINDS = {
    "data",
    "control",
    "state",
    "residual",
    "feedback",
    "dependency",
    "call",
    "event",
}
PORT_DIRECTIONS = {"input", "output", "inout"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("manifest root must be a JSON object")
    return data


def validate(manifest: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for field in ("version", "title", "subject", "orientation", "scale", "legend", "components", "edges"):
        if field not in manifest:
            errors.append(f"root: missing required field '{field}'")

    components = manifest.get("components", [])
    edges = manifest.get("edges", [])
    if not isinstance(components, list) or not components:
        errors.append("root.components: expected a non-empty array")
        components = []
    if not isinstance(edges, list):
        errors.append("root.edges: expected an array")
        edges = []

    component_map: dict[str, dict[str, Any]] = {}
    port_map: dict[tuple[str, str], dict[str, Any]] = {}
    indices: set[str] = set()

    for position, component in enumerate(components):
        location = f"components[{position}]"
        if not isinstance(component, dict):
            errors.append(f"{location}: expected an object")
            continue
        for field in ("id", "index", "title", "role", "category", "ports", "operation", "visual", "inspect"):
            if field not in component:
                errors.append(f"{location}: missing required field '{field}'")
        component_id = component.get("id")
        if not isinstance(component_id, str) or not component_id:
            errors.append(f"{location}.id: expected a non-empty string")
            continue
        if component_id in component_map:
            errors.append(f"{location}.id: duplicate component id '{component_id}'")
            continue
        component_map[component_id] = component

        index = component.get("index")
        if isinstance(index, str) and index:
            if index in indices:
                warnings.append(f"{location}.index: repeated visible index '{index}'")
            indices.add(index)

        visual = component.get("visual")
        if isinstance(visual, dict):
            for field in ("metaphor", "geometry", "encoding"):
                if not visual.get(field):
                    errors.append(f"{location}.visual: missing '{field}'")
        elif "visual" in component:
            errors.append(f"{location}.visual: expected an object")

        inspect = component.get("inspect")
        if isinstance(inspect, dict):
            for field in ("intuition", "details", "symbols"):
                if field not in inspect:
                    errors.append(f"{location}.inspect: missing '{field}'")
        elif "inspect" in component:
            errors.append(f"{location}.inspect: expected an object")

        ports = component.get("ports", [])
        if not isinstance(ports, list):
            errors.append(f"{location}.ports: expected an array")
            continue
        local_ids: set[str] = set()
        for port_position, port in enumerate(ports):
            port_location = f"{location}.ports[{port_position}]"
            if not isinstance(port, dict):
                errors.append(f"{port_location}: expected an object")
                continue
            for field in ("id", "direction", "payload", "shape"):
                if field not in port:
                    errors.append(f"{port_location}: missing required field '{field}'")
            port_id = port.get("id")
            if not isinstance(port_id, str) or not port_id:
                errors.append(f"{port_location}.id: expected a non-empty string")
                continue
            if port_id in local_ids:
                errors.append(f"{port_location}.id: duplicate port '{component_id}.{port_id}'")
            local_ids.add(port_id)
            direction = port.get("direction")
            if direction not in PORT_DIRECTIONS:
                errors.append(f"{port_location}.direction: expected one of {sorted(PORT_DIRECTIONS)}")
            port_map[(component_id, port_id)] = port

    edge_ids: set[str] = set()
    for position, edge in enumerate(edges):
        location = f"edges[{position}]"
        if not isinstance(edge, dict):
            errors.append(f"{location}: expected an object")
            continue
        for field in ("id", "source", "target", "kind", "payload", "shape"):
            if field not in edge:
                errors.append(f"{location}: missing required field '{field}'")
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not edge_id:
            errors.append(f"{location}.id: expected a non-empty string")
        elif edge_id in edge_ids:
            errors.append(f"{location}.id: duplicate edge id '{edge_id}'")
        else:
            edge_ids.add(edge_id)
        if edge.get("kind") not in EDGE_KINDS:
            errors.append(f"{location}.kind: expected one of {sorted(EDGE_KINDS)}")

        resolved: dict[str, dict[str, Any]] = {}
        for endpoint_name in ("source", "target"):
            endpoint = edge.get(endpoint_name)
            if not isinstance(endpoint, dict):
                errors.append(f"{location}.{endpoint_name}: expected component/port object")
                continue
            component_id = endpoint.get("component")
            port_id = endpoint.get("port")
            port = port_map.get((component_id, port_id))
            if port is None:
                errors.append(f"{location}.{endpoint_name}: unknown port '{component_id}.{port_id}'")
            else:
                resolved[endpoint_name] = port

        source = resolved.get("source")
        target = resolved.get("target")
        if source and source.get("direction") not in {"output", "inout"}:
            errors.append(f"{location}.source: source port is not output-capable")
        if target and target.get("direction") not in {"input", "inout"}:
            errors.append(f"{location}.target: target port is not input-capable")
        if source and target:
            source_shape = source.get("shape")
            target_shape = target.get("shape")
            if source_shape != target_shape and not edge.get("transform"):
                errors.append(
                    f"{location}: shape changes from '{source_shape}' to '{target_shape}' without a declared transform"
                )

    animations = manifest.get("flow_animations", [])
    if not isinstance(animations, list):
        errors.append("root.flow_animations: expected an array")
    else:
        for position, animation in enumerate(animations):
            location = f"flow_animations[{position}]"
            if not isinstance(animation, dict):
                errors.append(f"{location}: expected an object")
                continue
            edge_id = animation.get("edge")
            if edge_id not in edge_ids:
                errors.append(f"{location}.edge: unknown edge '{edge_id}'")
            if not animation.get("direction"):
                errors.append(f"{location}: missing direction")
            if not animation.get("meaning"):
                errors.append(f"{location}: missing meaning")

    modes = manifest.get("modes", [])
    if not isinstance(modes, list):
        errors.append("root.modes: expected an array when present")
    else:
        mode_ids: set[str] = set()
        for position, mode in enumerate(modes):
            location = f"modes[{position}]"
            if not isinstance(mode, dict) or not isinstance(mode.get("id"), str):
                errors.append(f"{location}: expected an object with string id")
                continue
            if mode["id"] in mode_ids:
                errors.append(f"{location}.id: duplicate mode id '{mode['id']}'")
            mode_ids.add(mode["id"])
            for component_id in mode.get("active_components", []):
                if component_id not in component_map:
                    errors.append(f"{location}.active_components: unknown component '{component_id}'")
            for edge_id in mode.get("active_edges", []):
                if edge_id not in edge_ids:
                    errors.append(f"{location}.active_edges: unknown edge '{edge_id}'")

    connected_components: set[str] = set()
    for edge in edges:
        if isinstance(edge, dict):
            for endpoint_name in ("source", "target"):
                endpoint = edge.get(endpoint_name)
                if isinstance(endpoint, dict) and isinstance(endpoint.get("component"), str):
                    connected_components.add(endpoint["component"])
    for component_id, component in component_map.items():
        if component_id not in connected_components and component.get("category") not in {"source", "sink", "container"}:
            warnings.append(f"component '{component_id}' is not connected by any edge")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to a visual-model JSON manifest")
    args = parser.parse_args()

    try:
        manifest = load_json(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    errors, warnings = validate(manifest)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK: visual model is structurally valid ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
