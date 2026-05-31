# Visio Scientific Figures

Editable Microsoft Visio scientific figures for papers, theses, reports, and presentations.

面向科研论文、学位论文和技术报告的 Codex/Claude Code skill：把论文段落、图形草稿或结构化 `figure_spec` 转成可编辑 `.vsdx`，并导出 `.png` / `.emf`，同时生成质量检查报告。

![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%2B%20Visio-blue)
![Skill](https://img.shields.io/badge/Codex%20Skill-Visio%20Figures-6f42c1)

## Why Star This

- Template-driven generation for common research diagrams.
- Editable Visio source files, not flat screenshots.
- AI image asset workflow for icons and pictorial panels that Visio primitives cannot reproduce well.
- Anonymized real-paper showcase: blurred source reference plus editable Visio reconstruction.
- Built-in spec validation, environment checks, and quality reports.
- Open-source-safe examples with no private manuscript material.
- Works as a Codex skill and can also be copied into Claude Code skills.

## Gallery

| Flowchart | Framework |
| --- | --- |
| ![Toy flowchart](docs/gallery/toy_flowchart.png) | ![Toy framework](docs/gallery/toy_framework.png) |

| Layered system | AI image assets |
| --- | --- |
| ![Toy layered system](docs/gallery/toy_layered_system.png) | ![Toy image assets](docs/gallery/toy_image_assets.png) |

| Anonymized real-paper reconstruction |
| --- |
| ![Anonymized real-paper reconstruction](docs/gallery/research_framework_with_assets.png) |

Render examples locally, then refresh the gallery:

```powershell
python .\skills\visio-scientific-figures\scripts\make_gallery.py
```

Gallery previews live in [`docs/gallery`](docs/gallery) after generation.

## Features / 功能

- Templates: `flowchart`, `framework`, `layered-system`, `matrix`, `mechanism`.
- Style packs: `nature-muted`, `ieee-clean`, `chinese-journal`, `presentation-color`.
- Image assets: import PNG/JPG/SVG/EMF assets into Visio nodes for richer icons and panels.
- Output formats: editable `.vsdx`, review `.png`, Word-friendly `.emf`.
- Validation: check spec fields, connector references, image paths, matrix fields, and export settings before launching Visio.
- Quality checks: missing outputs, small files, page bounds, likely text overflow, low contrast, overlap, detached arrows, short connectors, and Chinese font availability.
- Install helpers for Codex and Claude Code.

## Requirements / 环境要求

- Windows
- Microsoft Visio
- Python 3.10+
- `pywin32`
- Optional: `PyYAML` for full YAML syntax
- Optional: `Pillow` for future image inspection helpers

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Check the environment:

```powershell
python .\skills\visio-scientific-figures\scripts\check_environment.py
```

## Install as a Codex Skill / 安装为 Codex Skill

```powershell
.\install-codex.ps1
```

If `CODEX_HOME` is set, the script installs into `$env:CODEX_HOME\skills`; otherwise it installs into `$env:USERPROFILE\.codex\skills`.

## Use with Claude Code / 在 Claude Code 中使用

Claude Code supports Skills with `SKILL.md`. Install for the current user:

```powershell
.\install-claude-code.ps1
```

Install for one project:

```powershell
.\install-claude-code.ps1 -Project -ProjectPath C:\path\to\project
```

The `agents/openai.yaml` file is Codex UI metadata. Claude Code mainly uses `SKILL.md`, `scripts/`, `references/`, `schema/`, and `assets/`.

## Quick Start / 快速开始

Validate a spec:

```powershell
python .\skills\visio-scientific-figures\scripts\validate_spec.py .\examples\toy_flowchart\figure_spec.yaml
```

Render a toy flowchart:

```powershell
python .\skills\visio-scientific-figures\scripts\render_spec.py .\examples\toy_flowchart\figure_spec.yaml
```

Run quality checks:

```powershell
python .\skills\visio-scientific-figures\scripts\check_quality.py .\examples\toy_flowchart\output\toy_flowchart.vsdx --png .\examples\toy_flowchart\output\toy_flowchart.png --emf .\examples\toy_flowchart\output\toy_flowchart.emf --report .\examples\toy_flowchart\output\quality_report.md
```

## Spec Example / 规格示例

```json
{
  "template": "flowchart",
  "title": "Toy Research Workflow",
  "canvas": { "width_in": 7.5, "height_in": 3.8 },
  "style": "chinese-journal",
  "nodes": [
    { "id": "question", "text": "Define research question" },
    { "id": "data", "text": "Collect public data" }
  ],
  "groups": [],
  "connectors": [
    { "from": "question", "to": "data" }
  ],
  "exports": { "dir": "output", "stem": "toy_flowchart" }
}
```

See [`spec-format.md`](skills/visio-scientific-figures/references/spec-format.md) and the bundled JSON Schema at [`figure_spec.schema.json`](skills/visio-scientific-figures/schema/figure_spec.schema.json).

## AI Image Assets / AI 图标资产

When Visio shapes cannot faithfully reproduce a user's source icons, generate clean low-AI-look assets with an image model, save them under an `assets/` folder, and reference them in the spec:

```json
{
  "id": "sensor",
  "text": "Sensor data",
  "image": "assets/sensor-data.png",
  "image_mode": "left"
}
```

Use editable Visio text for labels and generated image assets only for the visual icon or panel. See [`image-assets.md`](skills/visio-scientific-figures/references/image-assets.md).

## 中文使用建议

- 中文期刊图优先使用 `chinese-journal` 风格包。
- 保留 `.vsdx` 作为可编辑源文件，投稿或插入 Word 时优先尝试 `.emf`。
- 生成后必须查看 `quality_report.md`，再人工检查 PNG 预览。
- 不要把真实论文正文、涉密项目图、原始 `.docx` 或未脱敏素材放进开源示例。

## License

MIT License.
