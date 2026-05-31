# Visio Scientific Figures

Editable Microsoft Visio scientific figures for papers, theses, reports, and presentations.

面向科研论文和报告的 Codex skill：把论文段落、图形草稿或结构化 spec 转成可编辑的 `.vsdx`，并导出 `.png` / `.emf`，同时生成质量检查报告。

## Features / 功能

- Template-driven Visio generation: `flowchart`, `framework`, `layered-system`, `matrix`, `mechanism`.
- Import generated PNG/JPG/SVG/EMF assets into Visio nodes for richer icons and figure panels.
- Paper-friendly style packs: `nature-muted`, `ieee-clean`, `chinese-journal`, `presentation-color`.
- Editable `.vsdx` as the source of truth, with `.png` preview and `.emf` Word-friendly export.
- Quality checks for missing outputs, blank/small files, page bounds, likely text overflow, contrast, overlap, and Chinese font availability.
- Open-source-safe toy examples. No private manuscript or real research assets are included.

## Requirements / 环境要求

- Windows
- Microsoft Visio
- Python 3.10+
- `pywin32`
- Optional: `PyYAML` for full YAML syntax

Install dependencies:

```powershell
python -m pip install pywin32 pyyaml
```

`PyYAML` is optional if your `.yaml` file uses JSON-compatible syntax, as the bundled examples do.

## Install as a Codex Skill / 安装为 Codex Skill

Copy or symlink the skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\skills\visio-scientific-figures $env:USERPROFILE\.codex\skills\
```

If `CODEX_HOME` is set, install into `$env:CODEX_HOME\skills` instead.

## Use with Claude Code / 在 Claude Code 中使用

Claude Code supports Skills with `SKILL.md`. Copy this skill folder to your user or project skills directory:

```powershell
Copy-Item -Recurse .\skills\visio-scientific-figures $env:USERPROFILE\.claude\skills\
```

Or for one project:

```powershell
Copy-Item -Recurse .\skills\visio-scientific-figures .\.claude\skills\
```

The `agents/openai.yaml` file is Codex UI metadata; Claude Code mainly uses `SKILL.md`, `scripts/`, `references/`, and `assets/`.

## Quick Start / 快速开始

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

See `skills/visio-scientific-figures/references/spec-format.md` for details.

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

Use editable Visio text for labels and generated image assets only for the visual icon or panel. See `skills/visio-scientific-figures/references/image-assets.md`.

## 中文使用建议

- 中文期刊图优先使用 `chinese-journal` 风格包。
- 保留 `.vsdx` 作为可编辑源文件，投稿或插入 Word 时优先尝试 `.emf`。
- 生成后必须查看 `quality_report.md`，再人工检查 PNG 预览。
- 不建议把真实论文正文、涉密项目图、原始 `.docx` 或未脱敏素材放进开源示例。

## License

MIT License.
