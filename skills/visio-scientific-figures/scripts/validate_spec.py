from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TEMPLATES = {"flowchart", "framework", "layered-system", "matrix", "mechanism"}
STYLE_PACKS = {"nature-muted", "ieee-clean", "chinese-journal", "presentation-color"}
IMAGE_MODES = {"left", "top", "fill"}
CONNECTOR_ROUTES = {"auto", "elbow"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".emf"}
REQUIRED_FIELDS = {"template", "title", "canvas", "style", "nodes", "groups", "connectors", "exports"}


@dataclass
class Finding:
    level: str
    message: str


def load_spec(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "YAML requires PyYAML unless the file is JSON-compatible. "
            "Install with `python -m pip install pyyaml` or use JSON syntax."
        ) from exc
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise SystemExit("Spec root must be an object.")
    return data


def as_list(value: Any, field: str, findings: list[Finding]) -> list[Any]:
    if isinstance(value, list):
        return value
    findings.append(Finding("error", f"`{field}` must be a list."))
    return []


def validate(spec: dict[str, Any], spec_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    missing = sorted(REQUIRED_FIELDS - set(spec))
    for field in missing:
        findings.append(Finding("error", f"missing required field: `{field}`"))
    validate_template(spec, findings)
    validate_canvas(spec, findings)
    validate_style(spec, findings)
    nodes = validate_nodes(spec, spec_path, findings)
    validate_groups(spec, nodes, findings)
    validate_connectors(spec, nodes, findings)
    validate_exports(spec, findings)
    validate_matrix(spec, findings)
    return findings


def validate_template(spec: dict[str, Any], findings: list[Finding]) -> None:
    template = spec.get("template")
    if template not in TEMPLATES:
        findings.append(Finding("error", f"`template` must be one of: {', '.join(sorted(TEMPLATES))}."))


def validate_canvas(spec: dict[str, Any], findings: list[Finding]) -> None:
    canvas = spec.get("canvas")
    if not isinstance(canvas, dict):
        findings.append(Finding("error", "`canvas` must be an object with `width_in` and `height_in`."))
        return
    for key in ("width_in", "height_in"):
        value = canvas.get(key)
        if not isinstance(value, (int, float)) or value <= 0:
            findings.append(Finding("error", f"`canvas.{key}` must be a positive number."))
    width = canvas.get("width_in", 0)
    height = canvas.get("height_in", 0)
    if isinstance(width, (int, float)) and isinstance(height, (int, float)) and (width > 15 or height > 12):
        findings.append(Finding("warn", "canvas is large for a paper figure; confirm this is intentional."))


def validate_style(spec: dict[str, Any], findings: list[Finding]) -> None:
    style = spec.get("style")
    if isinstance(style, str):
        if style not in STYLE_PACKS:
            findings.append(Finding("error", f"unknown style pack: `{style}`."))
        return
    if isinstance(style, dict):
        base = style.get("base", "nature-muted")
        if base not in STYLE_PACKS:
            findings.append(Finding("error", f"unknown style base: `{base}`."))
        return
    findings.append(Finding("error", "`style` must be a style-pack name or an object with `base`."))


def validate_nodes(spec: dict[str, Any], spec_path: Path, findings: list[Finding]) -> set[str]:
    nodes = as_list(spec.get("nodes"), "nodes", findings)
    ids: set[str] = set()
    for idx, node in enumerate(nodes):
        if not isinstance(node, dict):
            findings.append(Finding("error", f"`nodes[{idx}]` must be an object."))
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            findings.append(Finding("error", f"`nodes[{idx}].id` must be a non-empty string."))
            continue
        if node_id in ids:
            findings.append(Finding("error", f"duplicate node id: `{node_id}`."))
        ids.add(node_id)
        validate_node_geometry(node, node_id, findings)
        validate_node_image(node, node_id, spec_path, findings)
    if not ids and spec.get("template") != "matrix":
        findings.append(Finding("warn", "non-matrix templates usually need at least one node."))
    return ids


def validate_node_geometry(node: dict[str, Any], node_id: str, findings: list[Finding]) -> None:
    for key in ("x", "y", "w", "h", "font_size", "image_pad"):
        if key in node and not isinstance(node[key], (int, float)):
            findings.append(Finding("error", f"`{node_id}.{key}` must be numeric."))
    for key in ("w", "h"):
        if key in node and isinstance(node[key], (int, float)) and node[key] <= 0:
            findings.append(Finding("error", f"`{node_id}.{key}` must be positive."))
    shape = node.get("shape")
    if shape and shape not in {"rect", "ellipse", "image"}:
        findings.append(Finding("error", f"`{node_id}.shape` must be rect, ellipse, or image."))


def validate_node_image(node: dict[str, Any], node_id: str, spec_path: Path, findings: list[Finding]) -> None:
    image = node.get("image")
    if not image:
        return
    image_path = Path(str(image))
    if not image_path.is_absolute():
        image_path = spec_path.parent / image_path
    if image_path.suffix.lower() not in IMAGE_EXTS:
        findings.append(Finding("error", f"`{node_id}.image` has unsupported extension: {image_path.suffix}."))
    if not image_path.exists():
        findings.append(Finding("error", f"`{node_id}.image` does not exist: {image_path}."))
    mode = node.get("image_mode", "left")
    if mode not in IMAGE_MODES:
        findings.append(Finding("error", f"`{node_id}.image_mode` must be left, top, or fill."))


def validate_groups(spec: dict[str, Any], nodes: set[str], findings: list[Finding]) -> None:
    groups = as_list(spec.get("groups"), "groups", findings)
    seen: set[str] = set()
    for idx, group in enumerate(groups):
        if not isinstance(group, dict):
            findings.append(Finding("error", f"`groups[{idx}]` must be an object."))
            continue
        group_id = group.get("id")
        if not isinstance(group_id, str) or not group_id.strip():
            findings.append(Finding("error", f"`groups[{idx}].id` must be a non-empty string."))
            continue
        if group_id in seen:
            findings.append(Finding("error", f"duplicate group id: `{group_id}`."))
        seen.add(group_id)
        for key in ("x", "y", "w", "h", "title_x", "title_y", "title_w"):
            if key in group and not isinstance(group[key], (int, float)):
                findings.append(Finding("error", f"`groups[{idx}].{key}` must be numeric."))
        for key in ("w", "h", "title_w"):
            if key in group and isinstance(group[key], (int, float)) and group[key] <= 0:
                findings.append(Finding("error", f"`groups[{idx}].{key}` must be positive."))
        for node_id in group.get("nodes", []):
            if node_id not in nodes:
                findings.append(Finding("error", f"group `{group_id}` references unknown node `{node_id}`."))


def validate_connectors(spec: dict[str, Any], nodes: set[str], findings: list[Finding]) -> None:
    connectors = as_list(spec.get("connectors"), "connectors", findings)
    for idx, edge in enumerate(connectors):
        if not isinstance(edge, dict):
            findings.append(Finding("error", f"`connectors[{idx}]` must be an object."))
            continue
        for endpoint in ("from", "to"):
            value = edge.get(endpoint)
            if value not in nodes:
                findings.append(Finding("error", f"connector {idx} has unknown `{endpoint}` node `{value}`."))
        route = edge.get("route", "auto")
        if route not in CONNECTOR_ROUTES:
            findings.append(Finding("error", f"connector {idx} route must be auto or elbow."))


def validate_exports(spec: dict[str, Any], findings: list[Finding]) -> None:
    exports = spec.get("exports")
    if not isinstance(exports, dict):
        findings.append(Finding("error", "`exports` must be an object."))
        return
    has_dir_stem = "dir" in exports or "stem" in exports
    has_explicit = any(key in exports for key in ("vsdx", "png", "emf"))
    if not has_dir_stem and not has_explicit:
        findings.append(Finding("warn", "`exports` has no path fields; renderer will use output/output.* defaults."))


def validate_matrix(spec: dict[str, Any], findings: list[Finding]) -> None:
    if spec.get("template") != "matrix":
        return
    matrix = spec.get("matrix")
    if not isinstance(matrix, dict):
        findings.append(Finding("error", "`matrix` template requires a `matrix` object."))
        return
    rows = matrix.get("rows")
    columns = matrix.get("columns")
    cells = matrix.get("cells")
    if not isinstance(rows, list) or not rows:
        findings.append(Finding("error", "`matrix.rows` must be a non-empty list."))
    if not isinstance(columns, list) or not columns:
        findings.append(Finding("error", "`matrix.columns` must be a non-empty list."))
    if not isinstance(cells, dict):
        findings.append(Finding("error", "`matrix.cells` must be an object keyed as `row|column`."))


def write_report(findings: list[Finding], report: Path | None) -> None:
    errors = sum(1 for finding in findings if finding.level == "error")
    warnings = sum(1 for finding in findings if finding.level == "warn")
    lines = [
        "# Figure Spec Validation Report",
        "",
        f"Status: {'PASS' if errors == 0 else 'FAIL'}",
        f"Errors: {errors}",
        f"Warnings: {warnings}",
        "",
        "## Findings",
        "",
    ]
    lines.extend(f"- [{finding.level.upper()}] {finding.message}" for finding in findings)
    if not findings:
        lines.append("- No issues found.")
    text = "\n".join(lines) + "\n"
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(text, encoding="utf-8")
    print(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Visio scientific figure spec before rendering.")
    parser.add_argument("spec", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    spec_path = args.spec.resolve()
    findings = validate(load_spec(spec_path), spec_path)
    write_report(findings, args.report.resolve() if args.report else None)
    raise SystemExit(1 if any(f.level == "error" for f in findings) else 0)


if __name__ == "__main__":
    main()
