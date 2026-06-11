# Visio Scientific Figures

Editable Microsoft Visio scientific figures from structured specs.

把论文段落、框架草图或脱敏后的现有图，转成可编辑 `.vsdx`，并导出 `.png` / `.emf`，同时做版式与可读性检查。

![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%2B%20Visio-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

## Quickstart

```powershell
python -m pip install -r requirements.txt
python .\skills\visio-scientific-figures\scripts\check_environment.py
python .\skills\visio-scientific-figures\scripts\validate_spec.py .\examples\research_framework_with_assets\figure_spec.yaml
python .\skills\visio-scientific-figures\scripts\render_spec.py .\examples\research_framework_with_assets\figure_spec.yaml
python .\skills\visio-scientific-figures\scripts\check_quality.py .\examples\research_framework_with_assets\output\research_framework_with_assets.vsdx --png .\examples\research_framework_with_assets\output\research_framework_with_assets.png --emf .\examples\research_framework_with_assets\output\research_framework_with_assets.emf --report .\examples\research_framework_with_assets\output\quality_report.md
```

Install into local agents:

```powershell
.\install-codex.ps1
.\install-claude-code.ps1
```

## Why This Repo Exists

- Keeps `.vsdx` as the source of truth instead of a flat screenshot.
- Generates common research diagram types from a reproducible `figure_spec.yaml/json`.
- Defaults to Image 2 first-pass asset generation when Visio primitives are not enough.
- Reuses screenshot-cropped visual fragments from the reference figure when they preserve useful visual cues.
- Checks for bounds errors, overlaps, text overflow, connector issues, and weak typography before you ship the figure.

## Default Workflow

This skill is not meant to be a boxes-and-arrows toy. The default workflow is:

1. Ask Image 2 for a first-pass icon or small illustration when the figure needs realistic visual elements.
2. Crop usable bitmap fragments from the reference figure or screenshot when the original visual cue is worth preserving.
3. Import those assets into Visio nodes, but keep labels, titles, and connectors editable in Visio.
4. Run the quality checker and iterate until the editable figure is clean.

## Complex Example

This repo is intentionally centered on one complex showcase: an anonymized reconstruction derived from a blurred real-paper figure.

![Anonymized real-paper reconstruction](docs/gallery/research_framework_with_assets.png)

The showcase demonstrates the exact repository thesis:

- start from a blurred source figure instead of publishing private manuscript material
- generate or redraw missing icons with Image 2 first
- crop useful reference fragments when screenshots communicate the structure better
- rebuild the final figure as editable Visio shapes, text, and connectors
- export `.vsdx`, `.png`, and `.emf`, then run automated layout checks

## At a Glance

| Surface | Current state |
| --- | --- |
| Input | `figure_spec.yaml/json`, paper paragraph, sketch, blurred source figure, or screenshot |
| Output | Editable `.vsdx` plus `.png` and `.emf` |
| Templates | `flowchart`, `framework`, `layered-system`, `matrix`, `mechanism` |
| QA | Bounds, overlaps, text overflow, contrast, detached arrows, connector-over-text |
| Asset path | Image 2 first-pass assets, screenshot crops, plus native Visio shapes |
| Best fit | Paper figures, thesis diagrams, system frameworks, workflow figures with pictorial assets |

## Core Surface

Supported templates:

- `flowchart`
- `framework`
- `layered-system`
- `matrix`
- `mechanism`

Supported style packs:

- `nature-muted`
- `ieee-clean`
- `chinese-journal`
- `presentation-color`

Minimum spec shape:

```json
{
  "template": "flowchart",
  "title": "Figure title",
  "canvas": { "width_in": 7.5, "height_in": 4.8 },
  "style": "chinese-journal",
  "nodes": [{ "id": "input", "text": "Input" }],
  "groups": [],
  "connectors": [],
  "exports": { "dir": "output", "stem": "figure" }
}
```

Details live in:

- [`spec-format.md`](skills/visio-scientific-figures/references/spec-format.md)
- [`figure_spec.schema.json`](skills/visio-scientific-figures/schema/figure_spec.schema.json)
- [`quality-guidelines.md`](skills/visio-scientific-figures/references/quality-guidelines.md)
- [`image-assets.md`](skills/visio-scientific-figures/references/image-assets.md)

## How It Works

1. Start from a paper paragraph, sketch, or blurred source figure.
2. Call Image 2 first for icons or small figure panels when native Visio shapes will look weak.
3. Crop screenshot fragments from the reference figure when they preserve a useful visual cue.
4. Write or generate `figure_spec.yaml/json` with those assets referenced in `nodes[].image`.
5. Run `validate_spec.py`, then render `.vsdx`, `.png`, and `.emf`.
6. Run `check_quality.py`.
7. Fix the spec, not the screenshot, until the report is clean.

## Repository Layout

- `skills/visio-scientific-figures/`: the actual skill package
- `skills/visio-scientific-figures/scripts/`: render, validate, quality, environment, gallery
- `skills/visio-scientific-figures/references/`: spec rules, recipes, quality guidance
- `examples/`: open-source-safe sample specs and assets, with the main showcase under `research_framework_with_assets/`
- `docs/gallery/`: tracked PNG previews for the README hero example

## What Is Deliberately Not Here

- No hidden manual touch-up step after render.
- No bundling of real paper text, `.docx`, or undisguised project figures.
- No claim of cross-platform `.vsdx` generation yet. The current renderer is still Windows + Visio COM.

## Design Rules

- Prefer restrained journal typography over presentation-style fonts.
- Treat connector-over-text conflicts as defects, not acceptable noise.
- Use Image 2 or screenshot crops for icons and visual panels; keep labels editable in Visio.
- Do not publish real manuscript text, source `.docx`, or undisguised project diagrams.

## Roadmap

- Add more research-native templates: neural architecture, attention mechanism, and data pipeline.
- Add an XML-based `.vsdx` backend for CI and non-Windows environments.
- Add incremental update mode for large figures instead of full document rebuilds.
- Split `chinese-journal` into more journal-specific variants once real style constraints are stable.

## Limits

- Rendering currently depends on Windows + Microsoft Visio + `pywin32`.
- CI-friendly XML backend generation is not implemented yet.
- The templates cover common research figures, not every architecture or attention diagram.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for development flow and verification expectations.

## License

MIT License.
