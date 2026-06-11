from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "skills" / "visio-scientific-figures" / "scripts" / "validate_spec.py"
SPEC = importlib.util.spec_from_file_location("validate_spec", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def base_spec() -> dict:
    return {
        "template": "flowchart",
        "title": "Example",
        "canvas": {"width_in": 7.5, "height_in": 4.0},
        "style": "ieee-clean",
        "nodes": [{"id": "a", "text": "Start"}],
        "groups": [],
        "connectors": [],
        "exports": {"dir": "output", "stem": "example"},
    }


def test_validate_warns_on_overlong_text(tmp_path: Path) -> None:
    spec = base_spec()
    spec["nodes"][0]["text"] = "x" * 501
    findings = MODULE.validate(spec, tmp_path / "figure_spec.yaml")
    assert any("unusually long" in finding.message for finding in findings)


def test_validate_rejects_unknown_route(tmp_path: Path) -> None:
    spec = base_spec()
    spec["nodes"].append({"id": "b", "text": "End"})
    spec["connectors"] = [{"from": "a", "to": "b", "route": "diagonal"}]
    findings = MODULE.validate(spec, tmp_path / "figure_spec.yaml")
    assert any("route must be auto or elbow" in finding.message for finding in findings)


def test_matrix_warns_when_nodes_are_present(tmp_path: Path) -> None:
    spec = base_spec()
    spec["template"] = "matrix"
    spec["matrix"] = {"rows": ["r1"], "columns": ["c1"], "cells": {"r1|c1": "x"}}
    findings = MODULE.validate(spec, tmp_path / "figure_spec.yaml")
    assert any("ignore `nodes`" in finding.message for finding in findings)
