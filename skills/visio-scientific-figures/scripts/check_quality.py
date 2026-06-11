from __future__ import annotations

import argparse
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


NS = {"v": "http://schemas.microsoft.com/office/visio/2012/main"}
FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/simsun.ttc"),
]


@dataclass
class Issue:
    level: str
    message: str


@dataclass
class ShapeInfo:
    shape_id: str
    name: str
    text: str
    x: float
    y: float
    w: float
    h: float
    fill: str
    line: str
    char_color: str
    is_line: bool
    begin_x: float
    begin_y: float
    end_x: float
    end_y: float
    end_arrow: str
    has_connector_cells: bool


def cell(shape: ET.Element, name: str) -> str | None:
    for item in shape.findall("v:Cell", NS):
        if item.attrib.get("N") == name:
            return item.attrib.get("V") or item.attrib.get("F")
    return None


def first_char_cell(shape: ET.Element, name: str) -> str | None:
    section = shape.find("v:Section[@N='Character']", NS)
    if section is None:
        return None
    for item in section.findall(".//v:Cell", NS):
        if item.attrib.get("N") == name:
            return item.attrib.get("V")
    return None


def text_content(shape: ET.Element) -> str:
    text = shape.find("v:Text", NS)
    if text is None:
        return ""
    return "".join(text.itertext()).strip()


def number(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def page_size(root: ET.Element) -> tuple[float, float]:
    sheet = root.find(".//v:PageSheet", NS)
    if sheet is None:
        return 0, 0
    width = height = 0.0
    for item in sheet.findall("v:Cell", NS):
        if item.attrib.get("N") == "PageWidth":
            width = number(item.attrib.get("V"))
        if item.attrib.get("N") == "PageHeight":
            height = number(item.attrib.get("V"))
    return width, height


def parse_shapes(root: ET.Element, page_h: float) -> list[ShapeInfo]:
    parsed = []
    for shape in root.findall(".//v:Shape", NS):
        w, h = number(cell(shape, "Width")), number(cell(shape, "Height"))
        pin_x, pin_y = number(cell(shape, "PinX")), number(cell(shape, "PinY"))
        text = text_content(shape)
        has_connector_cells = any(cell(shape, n) for n in ("BeginX", "EndX"))
        thin_without_text = not text and min(w, h) < 0.08 and max(w, h) > 0.18
        is_line = has_connector_cells or thin_without_text
        begin_x = number(cell(shape, "BeginX"), pin_x - w / 2)
        begin_y = page_h - number(cell(shape, "BeginY"), pin_y)
        end_x = number(cell(shape, "EndX"), pin_x + w / 2)
        end_y = page_h - number(cell(shape, "EndY"), pin_y)
        parsed.append(
            ShapeInfo(
                shape.attrib.get("ID", "?"),
                shape.attrib.get("NameU", shape.attrib.get("Name", "")),
                text,
                pin_x - w / 2,
                page_h - (pin_y + h / 2),
                w,
                h,
                cell(shape, "FillForegnd") or "#FFFFFF",
                cell(shape, "LineColor") or "#000000",
                first_char_cell(shape, "Color") or "#1F2933",
                is_line,
                begin_x,
                begin_y,
                end_x,
                end_y,
                cell(shape, "EndArrow") or "",
                has_connector_cells,
            )
        )
    return parsed


def hex_to_rgb(value: str) -> tuple[int, int, int] | None:
    if not value or not value.startswith("#") or len(value) not in (4, 7):
        return None
    if len(value) == 4:
        value = "#" + "".join(ch * 2 for ch in value[1:])
    try:
        return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16)
    except ValueError:
        return None


def contrast_ratio(fg: str, bg: str) -> float | None:
    def channel(v: int) -> float:
        n = v / 255
        return n / 12.92 if n <= 0.03928 else ((n + 0.055) / 1.055) ** 2.4

    fg_rgb, bg_rgb = hex_to_rgb(fg), hex_to_rgb(bg)
    if fg_rgb is None or bg_rgb is None:
        return None
    lum_fg = 0.2126 * channel(fg_rgb[0]) + 0.7152 * channel(fg_rgb[1]) + 0.0722 * channel(fg_rgb[2])
    lum_bg = 0.2126 * channel(bg_rgb[0]) + 0.7152 * channel(bg_rgb[1]) + 0.0722 * channel(bg_rgb[2])
    light, dark = max(lum_fg, lum_bg), min(lum_fg, lum_bg)
    return (light + 0.05) / (dark + 0.05)


def overlap_area(a: ShapeInfo, b: ShapeInfo) -> float:
    x = max(0.0, min(a.x + a.w, b.x + b.w) - max(a.x, b.x))
    y = max(0.0, min(a.y + a.h, b.y + b.h) - max(a.y, b.y))
    return x * y


def contains(a: ShapeInfo, b: ShapeInfo) -> bool:
    return (
        a.x <= b.x + 0.02
        and a.y <= b.y + 0.02
        and a.x + a.w >= b.x + b.w - 0.02
        and a.y + a.h >= b.y + b.h - 0.02
    )


def file_checks(path: Path, kind: str) -> list[Issue]:
    issues = []
    if not path.exists():
        return [Issue("error", f"{kind} missing: {path}")]
    if path.stat().st_size < 1024:
        issues.append(Issue("error", f"{kind} is suspiciously small: {path.stat().st_size} bytes"))
    return issues


def inspect_vsdx(vsdx: Path) -> tuple[list[Issue], tuple[float, float], list[ShapeInfo]]:
    issues: list[Issue] = []
    try:
        with zipfile.ZipFile(vsdx) as archive:
            pages_root = ET.fromstring(archive.read("visio/pages/pages.xml"))
            root = ET.fromstring(archive.read("visio/pages/page1.xml"))
    except Exception as exc:
        return [Issue("error", f"cannot read VSDX page XML: {exc}")], (0, 0), []
    page_w, page_h = page_size(pages_root)
    shapes = parse_shapes(root, page_h)
    if page_w <= 0 or page_h <= 0:
        issues.append(Issue("error", "page size is missing or invalid"))
    if not shapes:
        issues.append(Issue("error", "page has no shapes"))
    if page_w > 15 or page_h > 12:
        issues.append(Issue("warn", f"page is large for paper figures: {page_w:.2f} x {page_h:.2f} in"))
    return issues, (page_w, page_h), shapes


def inspect_shapes(shapes: list[ShapeInfo], page_size_in: tuple[float, float]) -> list[Issue]:
    page_w, page_h = page_size_in
    issues: list[Issue] = []
    content = [s for s in shapes if not s.is_line and s.w > 0 and s.h > 0]
    for shape in content:
        if shape.x < -0.02 or shape.y < -0.02 or shape.x + shape.w > page_w + 0.02 or shape.y + shape.h > page_h + 0.02:
            issues.append(Issue("error", f"shape out of page bounds: {label(shape)}"))
        if shape.text:
            capacity = max(1.0, shape.w * shape.h * 52)
            if len(shape.text) > capacity:
                issues.append(Issue("warn", f"text may overflow {label(shape)}: {len(shape.text)} chars in {shape.w:.2f}x{shape.h:.2f} in"))
            ratio = contrast_ratio(shape.char_color, shape.fill)
            if ratio is not None and ratio < 3.0:
                issues.append(Issue("warn", f"low text contrast in {label(shape)}: {ratio:.2f}:1"))
    overlap_candidates = [s for s in content if not s.name.startswith("group_")]
    for idx, first in enumerate(overlap_candidates):
        for second in overlap_candidates[idx + 1:]:
            area = overlap_area(first, second)
            if area <= 0:
                continue
            if contains(first, second) or contains(second, first):
                continue
            small = max(0.01, min(first.w * first.h, second.w * second.h))
            if area / small > 0.35 and first.text and second.text:
                issues.append(Issue("warn", f"major overlap: {label(first)} and {label(second)}"))
    issues.extend(inspect_connectors(shapes, content))
    return issues


def inspect_connectors(shapes: list[ShapeInfo], content: list[ShapeInfo]) -> list[Issue]:
    issues: list[Issue] = []
    text_shapes = [s for s in content if s.text and not s.name.endswith("_image")]
    for line in [s for s in shapes if s.has_connector_cells]:
        length = math.hypot(line.end_x - line.begin_x, line.end_y - line.begin_y)
        if length < 0.15:
            issues.append(Issue("warn", f"very short connector or line: {label(line)}"))
        if line.end_arrow in ("", "0") and "label_" not in line.name and not line.name.startswith("route_segment_"):
            issues.append(Issue("warn", f"line may be missing arrow head: {label(line)}"))
        if content and not endpoint_near_shape(line.begin_x, line.begin_y, content):
            issues.append(Issue("warn", f"connector start may be detached: {label(line)}"))
        if content and not endpoint_near_shape(line.end_x, line.end_y, content):
            issues.append(Issue("warn", f"connector end may be detached: {label(line)}"))
        for shape in text_shapes:
            if endpoint_near_shape(line.begin_x, line.begin_y, [shape], tolerance=0.04):
                continue
            if endpoint_near_shape(line.end_x, line.end_y, [shape], tolerance=0.04):
                continue
            cross_pad = 0.0 if line.name.startswith("route_segment_") else 0.03
            if segment_hits_rect(line.begin_x, line.begin_y, line.end_x, line.end_y, shape, pad=cross_pad):
                issues.append(Issue("warn", f"connector crosses text or title: {label(line)} over {label(shape)}"))
    return issues


def endpoint_near_shape(x: float, y: float, shapes: list[ShapeInfo], tolerance: float = 0.18) -> bool:
    for shape in shapes:
        close_x = shape.x - tolerance <= x <= shape.x + shape.w + tolerance
        close_y = shape.y - tolerance <= y <= shape.y + shape.h + tolerance
        if close_x and close_y:
            return True
    return False


def segment_hits_rect(x1: float, y1: float, x2: float, y2: float, shape: ShapeInfo, pad: float = 0.0) -> bool:
    left = shape.x - pad
    right = shape.x + shape.w + pad
    top = shape.y - pad
    bottom = shape.y + shape.h + pad
    if left <= x1 <= right and top <= y1 <= bottom:
        return True
    if left <= x2 <= right and top <= y2 <= bottom:
        return True
    edges = [
        (left, top, right, top),
        (right, top, right, bottom),
        (right, bottom, left, bottom),
        (left, bottom, left, top),
    ]
    return any(segments_intersect(x1, y1, x2, y2, *edge) for edge in edges)


def segments_intersect(ax: float, ay: float, bx: float, by: float,
                       cx: float, cy: float, dx: float, dy: float) -> bool:
    def orient(px: float, py: float, qx: float, qy: float, rx: float, ry: float) -> float:
        return (qx - px) * (ry - py) - (qy - py) * (rx - px)

    def overlaps(px: float, py: float, qx: float, qy: float, rx: float, ry: float) -> bool:
        return min(px, qx) - 1e-9 <= rx <= max(px, qx) + 1e-9 and min(py, qy) - 1e-9 <= ry <= max(py, qy) + 1e-9

    o1 = orient(ax, ay, bx, by, cx, cy)
    o2 = orient(ax, ay, bx, by, dx, dy)
    o3 = orient(cx, cy, dx, dy, ax, ay)
    o4 = orient(cx, cy, dx, dy, bx, by)
    if o1 * o2 < 0 and o3 * o4 < 0:
        return True
    if abs(o1) < 1e-9 and overlaps(ax, ay, bx, by, cx, cy):
        return True
    if abs(o2) < 1e-9 and overlaps(ax, ay, bx, by, dx, dy):
        return True
    if abs(o3) < 1e-9 and overlaps(cx, cy, dx, dy, ax, ay):
        return True
    if abs(o4) < 1e-9 and overlaps(cx, cy, dx, dy, bx, by):
        return True
    return False


def label(shape: ShapeInfo) -> str:
    name = shape.name or shape.shape_id
    text = shape.text.replace("\n", " ")[:28]
    return f"{name} ({text})" if text else name


def inspect_fonts() -> list[Issue]:
    if any(path.exists() for path in FONT_CANDIDATES):
        return []
    return [Issue("warn", "no common Chinese font found: Microsoft YaHei, SimHei, or SimSun")]


def write_report(report: Path, issues: Iterable[Issue], page: tuple[float, float], shape_count: int) -> None:
    issue_list = list(issues)
    errors = sum(1 for issue in issue_list if issue.level == "error")
    warns = sum(1 for issue in issue_list if issue.level == "warn")
    status = "PASS" if errors == 0 else "FAIL"
    lines = [
        "# Visio Figure Quality Report",
        "",
        f"Status: {status}",
        f"Page: {page[0]:.2f} x {page[1]:.2f} in",
        f"Shapes: {shape_count}",
        f"Errors: {errors}",
        f"Warnings: {warns}",
        "",
        "## Findings",
        "",
    ]
    if issue_list:
        lines.extend(f"- [{issue.level.upper()}] {issue.message}" for issue in issue_list)
    else:
        lines.append("- No issues found.")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def check(vsdx: Path, png: Path | None, emf: Path | None, report: Path) -> int:
    issues: list[Issue] = []
    issues.extend(file_checks(vsdx, "vsdx"))
    if png:
        issues.extend(file_checks(png, "png"))
    if emf:
        issues.extend(file_checks(emf, "emf"))
    vsdx_issues, page, shapes = inspect_vsdx(vsdx)
    issues.extend(vsdx_issues)
    issues.extend(inspect_shapes(shapes, page))
    issues.extend(inspect_fonts())
    report.parent.mkdir(parents=True, exist_ok=True)
    write_report(report, issues, page, len(shapes))
    return 1 if any(issue.level == "error" for issue in issues) else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Check editable Visio scientific figure outputs.")
    parser.add_argument("vsdx", type=Path)
    parser.add_argument("--png", type=Path)
    parser.add_argument("--emf", type=Path)
    parser.add_argument("--report", type=Path, default=Path("quality_report.md"))
    args = parser.parse_args()
    code = check(args.vsdx.resolve(), args.png.resolve() if args.png else None,
                 args.emf.resolve() if args.emf else None, args.report.resolve())
    print(args.report.resolve())
    raise SystemExit(code)


if __name__ == "__main__":
    main()
