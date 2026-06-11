from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "skills" / "visio-scientific-figures" / "scripts" / "check_quality.py"
SPEC = importlib.util.spec_from_file_location("check_quality", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_segment_hits_rect_detects_crossing() -> None:
    shape = MODULE.ShapeInfo("1", "title", "Layer Title", 1.0, 1.0, 2.0, 0.4, "#fff", "#000", "#000", False, 0, 0, 0, 0, "", False)
    assert MODULE.segment_hits_rect(0.0, 1.2, 4.0, 1.2, shape, pad=0.0) is True


def test_segment_hits_rect_ignores_clear_gap() -> None:
    shape = MODULE.ShapeInfo("1", "title", "Layer Title", 1.0, 1.0, 2.0, 0.4, "#fff", "#000", "#000", False, 0, 0, 0, 0, "", False)
    assert MODULE.segment_hits_rect(0.0, 0.2, 4.0, 0.2, shape, pad=0.0) is False


def test_route_segment_near_title_does_not_warn() -> None:
    title = MODULE.ShapeInfo("3", "group_title", "Generation Layer", 1.0, 1.0, 1.6, 0.32, "#fff", "#000", "#111", False, 0, 0, 0, 0, "", False)
    start = MODULE.ShapeInfo("5", "start_box", "Start", 0.75, 0.48, 0.35, 0.28, "#fff", "#000", "#111", False, 0, 0, 0, 0, "", False)
    end = MODULE.ShapeInfo("6", "end_box", "End", 0.75, 1.38, 0.35, 0.28, "#fff", "#000", "#111", False, 0, 0, 0, 0, "", False)
    route = MODULE.ShapeInfo("4", "route_segment_1", "", 0, 0, 0, 0, "#fff", "#000", "#111", True, 0.98, 0.6, 0.98, 1.5, "4", True)
    issues = MODULE.inspect_connectors([route, title, start, end], [title, start, end])
    assert [issue for issue in issues if "crosses text or title" in issue.message] == []


def test_parse_shapes_keeps_thin_text_strip_as_content() -> None:
    xml = """
    <PageContents xmlns="http://schemas.microsoft.com/office/visio/2012/main">
      <Shapes>
        <Shape ID="1" NameU="band_title">
          <Cell N="Width" V="2.0" />
          <Cell N="Height" V="0.05" />
          <Cell N="PinX" V="2.0" />
          <Cell N="PinY" V="2.0" />
          <Text>Generation Layer</Text>
        </Shape>
      </Shapes>
    </PageContents>
    """
    root = MODULE.ET.fromstring(xml)
    shapes = MODULE.parse_shapes(root, 5.0)
    assert len(shapes) == 1
    assert shapes[0].is_line is False
