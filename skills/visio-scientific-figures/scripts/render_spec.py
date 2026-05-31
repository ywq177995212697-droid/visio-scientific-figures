from __future__ import annotations

import argparse
import gc
import json
import math
import time
from pathlib import Path
from typing import Any

import win32com.client
import pythoncom


STYLE_PACKS = {
    "nature-muted": {
        "ink": "#1F2933",
        "muted": "#5B6675",
        "line": "#26384F",
        "fills": ["#C9D8F0", "#B9DFC9", "#F0D58A", "#91C9D7", "#C1A4D6"],
        "strokes": ["#5278B8", "#3F8D70", "#B88522", "#2F7F9B", "#7A4F9B"],
        "bg": "#FFFFFF",
        "font_candidates": ["Times New Roman", "Arial", "Microsoft YaHei", "SimSun"],
    },
    "ieee-clean": {
        "ink": "#111111",
        "muted": "#555555",
        "line": "#222222",
        "fills": ["#F7F7F7", "#EAEAEA", "#FFFFFF", "#D9D9D9"],
        "strokes": ["#222222", "#444444", "#666666", "#888888"],
        "bg": "#FFFFFF",
        "font_candidates": ["Times New Roman", "Arial", "Calibri"],
    },
    "chinese-journal": {
        "ink": "#1F2937",
        "muted": "#4B5563",
        "line": "#1F4E79",
        "fills": ["#EAF3FA", "#E8F3F0", "#FFF2D9", "#F6F7F9"],
        "strokes": ["#1F5F99", "#0F6B5F", "#A86A16", "#B9C4D0"],
        "bg": "#FFFFFF",
        "font_candidates": ["SimSun", "Microsoft YaHei", "Times New Roman", "Arial"],
    },
    "presentation-color": {
        "ink": "#172033",
        "muted": "#526070",
        "line": "#243B73",
        "fills": ["#DDEBFF", "#DFF4EA", "#FFF1CC", "#F5E1FF", "#FFE4DA"],
        "strokes": ["#2457A6", "#20835A", "#B47700", "#8A4BA8", "#C85432"],
        "bg": "#FFFFFF",
        "font_candidates": ["Arial", "Microsoft YaHei", "Calibri", "SimSun"],
    },
}


def rgb(hex_color: str) -> str:
    value = hex_color.strip("#")
    return f"RGB({int(value[0:2], 16)},{int(value[2:4], 16)},{int(value[4:6], 16)})"


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
    return yaml.safe_load(text)


def style_for(spec: dict[str, Any]) -> dict[str, Any]:
    name = spec.get("style", "nature-muted")
    if isinstance(name, dict):
        base = STYLE_PACKS.get(name.get("base", "nature-muted"), STYLE_PACKS["nature-muted"]).copy()
        base.update(name)
        return base
    return STYLE_PACKS.get(str(name), STYLE_PACKS["nature-muted"])


def output_paths(spec: dict[str, Any], spec_dir: Path) -> dict[str, Path]:
    exports = spec.get("exports") or {}
    stem = str(exports.get("stem") or "output")
    out_dir = spec_dir / str(exports.get("dir") or "output")
    out_dir.mkdir(parents=True, exist_ok=True)
    return {
        "vsdx": (spec_dir / exports["vsdx"]) if "vsdx" in exports else out_dir / f"{stem}.vsdx",
        "png": (spec_dir / exports["png"]) if "png" in exports else out_dir / f"{stem}.png",
        "emf": (spec_dir / exports["emf"]) if "emf" in exports else out_dir / f"{stem}.emf",
    }


class VisioCanvas:
    def __init__(self, app: Any, width: float, height: float, style: dict[str, Any], asset_base: Path):
        self.app = app
        self.width = width
        self.height = height
        self.style = style
        self.asset_base = asset_base
        self.doc = app.Documents.Add("")
        self.page = app.ActivePage
        self.page.PageSheet.CellsU("PageWidth").FormulaU = f"{width} in"
        self.page.PageSheet.CellsU("PageHeight").FormulaU = f"{height} in"
        self.font_id = self._find_font(self.style.get("font_candidates"))
        self.shapes: dict[str, Any] = {}

    def _find_font(self, candidates: list[str] | None = None) -> int | None:
        preferred = candidates or ["Times New Roman", "Arial", "Microsoft YaHei", "SimSun"]
        for name in preferred:
            for idx in range(1, self.doc.Fonts.Count + 1):
                font = self.doc.Fonts.Item(idx)
                if name.lower() in font.Name.lower():
                    return font.ID
        return None

    def font_id_for(self, family: str | None) -> int | None:
        if not family:
            return self.font_id
        return self._find_font([family]) or self.font_id

    def y(self, y_top: float) -> float:
        return self.height - y_top

    def apply_style(self, shape: Any, fill: str, line: str, font: str | None = None,
                    line_w: float = 1.1, font_size: float = 9.0, bold: bool = False,
                    font_family: str | None = None) -> None:
        shape.CellsU("FillForegnd").FormulaU = rgb(fill)
        shape.CellsU("LineColor").FormulaU = rgb(line)
        shape.CellsU("LineWeight").FormulaU = f"{line_w} pt"
        shape.CellsU("Char.Size").FormulaU = f"{font_size} pt"
        shape.CellsU("Char.Color").FormulaU = rgb(font or self.style["ink"])
        shape.CellsU("Char.Style").FormulaU = "1" if bold else "0"
        shape.CellsU("Para.HorzAlign").FormulaU = "1"
        shape.CellsU("VerticalAlign").FormulaU = "1"
        font_id = self.font_id_for(font_family)
        if font_id is not None:
            shape.CellsU("Char.Font").FormulaU = str(font_id)
        for margin in ("LeftMargin", "RightMargin", "TopMargin", "BottomMargin"):
            shape.CellsU(margin).FormulaU = "0.03 in"

    def rect(self, node_id: str, x: float, y: float, w: float, h: float, text: str,
             fill: str, line: str, font: str | None = None, radius: float = 0.06,
             font_size: float = 9.0, bold: bool = False, font_family: str | None = None) -> Any:
        shape = self.page.DrawRectangle(x, self.y(y + h), x + w, self.y(y))
        shape.Text = text
        shape.NameU = node_id
        self.apply_style(shape, fill, line, font, font_size=font_size, bold=bold, font_family=font_family)
        shape.CellsU("Rounding").FormulaU = f"{radius} in"
        self.shapes[node_id] = shape
        return shape

    def ellipse(self, node_id: str, x: float, y: float, w: float, h: float, text: str,
                fill: str, line: str, font: str | None = None, font_size: float = 9.0,
                bold: bool = False, font_family: str | None = None) -> Any:
        shape = self.page.DrawOval(x, self.y(y + h), x + w, self.y(y))
        shape.Text = text
        shape.NameU = node_id
        self.apply_style(shape, fill, line, font, font_size=font_size, bold=bold, font_family=font_family)
        self.shapes[node_id] = shape
        return shape

    def text(self, node_id: str, x: float, y: float, w: float, h: float, text: str,
             font_size: float = 11.0, bold: bool = False, align: int = 1,
             font_family: str | None = None) -> Any:
        shape = self.rect(node_id, x, y, w, h, text, "#FFFFFF", "#FFFFFF",
                          font_size=font_size, bold=bold, radius=0, font_family=font_family)
        shape.CellsU("FillPattern").FormulaU = "0"
        shape.CellsU("LinePattern").FormulaU = "0"
        shape.CellsU("Para.HorzAlign").FormulaU = str(align)
        return shape

    def image(self, node_id: str, x: float, y: float, w: float, h: float,
              path: str, register: bool = False) -> Any:
        asset = Path(path)
        if not asset.is_absolute():
            asset = self.asset_base / asset
        if not asset.exists():
            raise SystemExit(f"Missing image asset for {node_id}: {asset}")
        shape = self.page.Import(str(asset.resolve()))
        shape.NameU = node_id
        shape.CellsU("PinX").FormulaU = f"{x + w / 2} in"
        shape.CellsU("PinY").FormulaU = f"{self.y(y + h / 2)} in"
        shape.CellsU("Width").FormulaU = f"{w} in"
        shape.CellsU("Height").FormulaU = f"{h} in"
        shape.CellsU("LinePattern").FormulaU = "0"
        shape.CellsU("FillPattern").FormulaU = "0"
        if register:
            self.shapes[node_id] = shape
        return shape

    def line(self, x1: float, y1: float, x2: float, y2: float, dashed: bool = False,
             arrow: bool = True, color: str | None = None, label: str = "",
             name: str | None = None) -> Any:
        line = self.page.DrawLine(x1, self.y(y1), x2, self.y(y2))
        if name:
            line.NameU = name
        line.CellsU("LineColor").FormulaU = rgb(color or self.style["line"])
        line.CellsU("LineWeight").FormulaU = "1.15 pt"
        if arrow:
            line.CellsU("EndArrow").FormulaU = "4"
        if dashed:
            line.CellsU("LinePattern").FormulaU = "2"
        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            self.text(f"label_{line.ID}", mid_x - 0.35, mid_y - 0.12, 0.7, 0.18,
                      label, font_size=7.2)
        return line

    def connect(self, start_id: str, end_id: str, dashed: bool = False, label: str = "",
                route: str = "auto") -> None:
        start, end = self.shapes[start_id], self.shapes[end_id]
        sx, sy, sw, sh = self.bounds(start)
        ex, ey, ew, eh = self.bounds(end)
        start_pt, end_pt = connection_points((sx, sy, sw, sh), (ex, ey, ew, eh))
        if route == "elbow":
            self.elbow(start_pt, end_pt, dashed=dashed, label=label)
            return
        self.line(*start_pt, *end_pt, dashed=dashed, label=label)

    def elbow(self, start: tuple[float, float], end: tuple[float, float],
              dashed: bool = False, label: str = "") -> None:
        x1, y1 = start
        x2, y2 = end
        if abs(x2 - x1) >= abs(y2 - y1):
            mid = (x1 + x2) / 2
            points = [(x1, y1), (mid, y1), (mid, y2), (x2, y2)]
        else:
            mid = (y1 + y2) / 2
            points = [(x1, y1), (x1, mid), (x2, mid), (x2, y2)]
        for idx in range(len(points) - 1):
            self.line(*points[idx], *points[idx + 1], dashed=dashed,
                      arrow=idx == len(points) - 2, name=f"route_segment_{idx}")
        if label:
            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2
            self.text(f"label_{abs(hash((x1, y1, x2, y2, label))) % 100000}",
                      label_x - 0.32, label_y - 0.10, 0.64, 0.18, label, font_size=7.0)

    def bounds(self, shape: Any) -> tuple[float, float, float, float]:
        pin_x = shape.CellsU("PinX").ResultIU
        pin_y = shape.CellsU("PinY").ResultIU
        width = shape.CellsU("Width").ResultIU
        height = shape.CellsU("Height").ResultIU
        return pin_x - width / 2, self.height - (pin_y + height / 2), width, height

    def export(self, paths: dict[str, Path]) -> None:
        for path in paths.values():
            if path.exists():
                path.unlink()
        self._visio_call(lambda: self.page.Export(str(paths["png"].resolve())))
        self._visio_call(lambda: self.page.Export(str(paths["emf"].resolve())))
        time.sleep(0.2)
        self._visio_call(lambda: self.doc.SaveAs(str(paths["vsdx"].resolve())))
        self.doc.Close()

    def _visio_call(self, action: Any) -> Any:
        last_error = None
        for _attempt in range(3):
            try:
                return action()
            except Exception as exc:
                last_error = exc
                time.sleep(0.8)
        raise last_error


def node_box(node: dict[str, Any], fallback: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    return (
        float(node.get("x", fallback[0])),
        float(node.get("y", fallback[1])),
        float(node.get("w", node.get("width", fallback[2]))),
        float(node.get("h", node.get("height", fallback[3]))),
    )


def connection_points(start: tuple[float, float, float, float],
                      end: tuple[float, float, float, float]) -> tuple[tuple[float, float], tuple[float, float]]:
    sx, sy, sw, sh = start
    ex, ey, ew, eh = end
    scx, scy = sx + sw / 2, sy + sh / 2
    ecx, ecy = ex + ew / 2, ey + eh / 2
    dx, dy = ecx - scx, ecy - scy
    if abs(dx) >= abs(dy):
        if dx >= 0:
            return (sx + sw, scy), (ex, ecy)
        return (sx, scy), (ex + ew, ecy)
    if dy >= 0:
        return (scx, sy + sh), (ecx, ey)
    return (scx, sy), (ecx, ey + eh)


def draw_node(c: VisioCanvas, node: dict[str, Any], box: tuple[float, float, float, float],
              fill: str, line: str, default_shape: str = "rect",
              default_font_size: float = 9.0, default_bold: bool = True) -> Any:
    node_id = node["id"]
    text = node.get("text", node_id)
    image_path = node.get("image")
    shape_kind = node.get("shape", default_shape)
    font_size = float(node.get("font_size", default_font_size))
    bold = bool(node.get("bold", default_bold))
    font_family = node.get("font_family")
    if image_path and shape_kind == "image":
        return c.image(node_id, *box, image_path, register=True)
    shape_func = c.ellipse if shape_kind == "ellipse" else c.rect
    container_text = "" if image_path else text
    shape = shape_func(node_id, *box, container_text, fill, line,
                       font_size=font_size, bold=bold, font_family=font_family)
    if image_path:
        place_image_in_node(c, node, box, image_path, text, font_size, bold)
    return shape


def place_image_in_node(c: VisioCanvas, node: dict[str, Any], box: tuple[float, float, float, float],
                        image_path: str, text: str, font_size: float, bold: bool) -> None:
    x, y, w, h = box
    pad = float(node.get("image_pad", 0.08))
    mode = node.get("image_mode", "left")
    font_family = node.get("font_family")
    if mode == "top":
        img_h = min(h * 0.46, h - 2 * pad)
        img_w = min(w - 2 * pad, img_h * 1.35)
        c.image(f"{node['id']}_image", x + (w - img_w) / 2, y + pad, img_w, img_h, image_path)
        c.text(f"{node['id']}_label", x + pad, y + pad + img_h + 0.04,
               w - 2 * pad, max(0.12, h - img_h - 3 * pad), text,
               font_size=font_size, bold=bold, font_family=font_family)
        return
    if mode == "fill":
        c.image(f"{node['id']}_image", x + pad, y + pad, w - 2 * pad, h - 2 * pad, image_path)
        return
    img_size = min(h - 2 * pad, max(0.16, w * 0.28))
    c.image(f"{node['id']}_image", x + pad, y + (h - img_size) / 2, img_size, img_size, image_path)
    c.text(f"{node['id']}_label", x + pad * 2 + img_size, y + pad,
           max(0.12, w - img_size - 3 * pad), h - 2 * pad, text,
           font_size=font_size, bold=bold, font_family=font_family)


def draw_title(c: VisioCanvas, spec: dict[str, Any]) -> None:
    title = str(spec.get("title") or "")
    if title:
        c.text("title", 0.35, 0.12, c.width - 0.7, 0.34, title, font_size=12.5, bold=True)


def draw_flowchart(c: VisioCanvas, spec: dict[str, Any]) -> None:
    nodes = spec.get("nodes", [])
    n = max(1, len(nodes))
    cols = min(5, n)
    rows = math.ceil(n / cols)
    cell_w = (c.width - 1.0) / cols
    cell_h = (c.height - 1.2) / max(1, rows)
    for idx, node in enumerate(nodes):
        row, col = divmod(idx, cols)
        fill = node.get("fill") or c.style["fills"][idx % len(c.style["fills"])]
        line = node.get("line") or c.style["strokes"][idx % len(c.style["strokes"])]
        box = node_box(node, (0.55 + col * cell_w, 0.8 + row * cell_h, cell_w - 0.35, 0.58))
        draw_node(c, node, box, fill, line, default_font_size=9.2)
    connect_all(c, spec)


def draw_framework(c: VisioCanvas, spec: dict[str, Any]) -> None:
    groups = spec.get("groups") or [{"id": "main", "title": "", "nodes": [n["id"] for n in spec.get("nodes", [])]}]
    node_map = {n["id"]: n for n in spec.get("nodes", [])}
    band_h = (c.height - 1.0) / max(1, len(groups))
    for gi, group in enumerate(groups):
        x = float(group.get("x", 0.35))
        y = float(group.get("y", 0.70 + gi * band_h))
        w = float(group.get("w", c.width - 0.7))
        h = float(group.get("h", band_h - 0.22))
        fill = c.style["fills"][gi % len(c.style["fills"])]
        line = c.style["strokes"][gi % len(c.style["strokes"])]
        c.rect(f"group_{group['id']}", x, y, w, h, "", fill, line, font_size=10.5, bold=True)
        title_x = float(group.get("title_x", x + 0.20))
        title_y = float(group.get("title_y", y + 0.12))
        title_w = float(group.get("title_w", w - 0.4))
        c.text(f"group_{group['id']}_title", title_x, title_y, title_w, 0.22,
               group.get("title", ""), font_size=8.7, bold=True, align=0)
        ids = group.get("nodes", [])
        step = (w - 0.45) / max(1, len(ids))
        for ni, node_id in enumerate(ids):
            node = node_map[node_id]
            box = node_box(node, (x + 0.30 + ni * step, y + 0.48, step - 0.22, 0.46))
            draw_node(c, node, box, "#FFFFFF", line, default_font_size=8.0, default_bold=False)
    connect_all(c, spec)


def draw_layered_system(c: VisioCanvas, spec: dict[str, Any]) -> None:
    nodes = spec.get("nodes", [])
    count = max(1, len(nodes))
    max_w, max_h = c.width - 1.0, c.height - 1.2
    for idx, node in enumerate(nodes):
        shrink = idx * 0.42
        box = node_box(node, (0.5 + shrink, 0.75 + shrink, max_w - 2 * shrink, max_h - 2 * shrink))
        fill = node.get("fill") or c.style["fills"][idx % len(c.style["fills"])]
        line = node.get("line") or c.style["strokes"][idx % len(c.style["strokes"])]
        font = node.get("font") or c.style["ink"]
        if node.get("image"):
            draw_node(c, node, box, fill, line, default_font_size=10.0)
        else:
            c.rect(node["id"], *box, node.get("text", node["id"]), fill, line, font=font,
                   font_size=float(node.get("font_size", 10.0)), bold=True)


def draw_matrix(c: VisioCanvas, spec: dict[str, Any]) -> None:
    matrix = spec.get("matrix", {})
    rows, cols = matrix.get("rows", []), matrix.get("columns", [])
    cells = matrix.get("cells", {})
    left, top = 0.8, 0.85
    w, h = (c.width - 1.2) / (len(cols) + 1), (c.height - 1.3) / (len(rows) + 1)
    for ci, col in enumerate([""] + cols):
        c.rect(f"col_{ci}", left + ci * w, top, w, h, str(col), c.style["fills"][0], c.style["strokes"][0], bold=True)
    for ri, row in enumerate(rows, start=1):
        c.rect(f"row_{ri}", left, top + ri * h, w, h, str(row), c.style["fills"][1], c.style["strokes"][1], bold=True)
        for ci, col in enumerate(cols, start=1):
            value = cells.get(f"{row}|{col}", "")
            c.rect(f"cell_{ri}_{ci}", left + ci * w, top + ri * h, w, h, str(value), "#FFFFFF", "#B9C4D0")


def draw_mechanism(c: VisioCanvas, spec: dict[str, Any]) -> None:
    nodes = spec.get("nodes", [])
    cx, cy = c.width / 2, c.height / 2 + 0.15
    rx, ry = c.width * 0.34, c.height * 0.28
    for idx, node in enumerate(nodes):
        angle = 2 * math.pi * idx / max(1, len(nodes)) - math.pi / 2
        box = node_box(node, (cx + rx * math.cos(angle) - 0.65, cy + ry * math.sin(angle) - 0.25, 1.3, 0.5))
        fill = c.style["fills"][idx % len(c.style["fills"])]
        line = c.style["strokes"][idx % len(c.style["strokes"])]
        draw_node(c, node, box, fill, line, default_font_size=8.5)
    connect_all(c, spec)


def connect_all(c: VisioCanvas, spec: dict[str, Any]) -> None:
    for edge in spec.get("connectors", []):
        if edge.get("from") in c.shapes and edge.get("to") in c.shapes:
            c.connect(edge["from"], edge["to"], dashed=bool(edge.get("dashed")),
                      label=edge.get("label", ""), route=edge.get("route", "auto"))


TEMPLATES = {
    "flowchart": draw_flowchart,
    "framework": draw_framework,
    "layered-system": draw_layered_system,
    "matrix": draw_matrix,
    "mechanism": draw_mechanism,
}


def render(spec_path: Path) -> dict[str, Path]:
    pythoncom.CoInitialize()
    spec = load_spec(spec_path)
    style = style_for(spec)
    canvas = spec.get("canvas", {})
    width = float(canvas.get("width_in", 7.5))
    height = float(canvas.get("height_in", 5.0))
    paths = output_paths(spec, spec_path.parent)
    app = win32com.client.DispatchEx("Visio.Application")
    app.Visible = False
    app.AlertResponse = 7
    c = None
    try:
        c = VisioCanvas(app, width, height, style, spec_path.parent)
        draw_title(c, spec)
        template = spec.get("template", "flowchart")
        if template not in TEMPLATES:
            raise SystemExit(f"Unsupported template: {template}")
        TEMPLATES[template](c, spec)
        c.export(paths)
    finally:
        try:
            for idx in range(app.Documents.Count, 0, -1):
                app.Documents.Item(idx).Close()
        except Exception:
            pass
        try:
            app.Quit()
        except Exception:
            pass
        c = None
        app = None
        gc.collect()
        pythoncom.CoUninitialize()
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a figure_spec.yaml/json to editable Visio outputs.")
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    for kind, path in render(args.spec.resolve()).items():
        print(f"{kind}={path}")


if __name__ == "__main__":
    main()
