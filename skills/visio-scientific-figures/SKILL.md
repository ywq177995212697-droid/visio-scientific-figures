---
name: visio-scientific-figures
description: Create, edit, export, and quality-check editable Microsoft Visio scientific figures for papers, theses, reports, and presentations. Use when Codex needs to turn research text into Visio diagrams, generate paper-ready flowcharts/frameworks/layered systems/matrices/mechanism figures, create or import AI-generated icon/image assets for Visio nodes, modify or export .vsdx files, or validate PNG/EMF/VSDX outputs for readability, layout, fonts, and publication quality.
---

# Visio Scientific Figures

## Core Workflow

1. Clarify the figure intent from the user's paper text, sketch, or existing `.vsdx`.
2. Choose a template: `flowchart`, `framework`, `layered-system`, `matrix`, or `mechanism`.
3. If the source figure needs realistic icons or pictorial elements, generate/import image assets first and reference them from nodes with `image`.
4. Write a `figure_spec.yaml` or `figure_spec.json` with `template`, `title`, `canvas`, `style`, `nodes`, `groups`, `connectors`, and `exports`.
5. Validate the spec before launching Visio:

```bash
python scripts/validate_spec.py path/to/figure_spec.yaml
```

6. Render with:

```bash
python scripts/render_spec.py path/to/figure_spec.yaml
```

7. Run the quality checker:

```bash
python scripts/check_quality.py path/to/output.vsdx --png path/to/output.png --emf path/to/output.emf --report path/to/quality_report.md
```

8. Read `quality_report.md`, fix the spec or script, and re-render until the report has no errors and only acceptable warnings.

## Template Selection

- Use `flowchart` for stage procedures, closed-loop workflows, decision paths, and method pipelines.
- Use `framework` for system architecture, LLM workflows, method modules, and layered support/output diagrams.
- Use `layered-system` for nested data systems, knowledge bases, capability hierarchies, and source coverage diagrams.
- Use `matrix` for comparison tables, capability-task maps, method-feature maps, and evaluation grids.
- Use `mechanism` for causal relations, feedback loops, interactions, and circular process figures.

Read `references/spec-format.md` before writing a new spec. Read `references/image-assets.md` when a figure needs icons, equipment illustrations, screenshots, or AI-generated bitmap assets. Read `references/recipes.md` for paper-paragraph-to-spec and quality-loop patterns. Read `references/visio-com-notes.md` before patching scripts or editing existing `.vsdx` files. Read `references/quality-guidelines.md` when a figure is meant for a paper submission.

## Figure Spec Rules

- Keep specs portable: use relative output paths and avoid user-specific absolute paths.
- Use `canvas.width_in` and `canvas.height_in` in inches. Paper figures usually work best between 4-8 inches wide for single-column and 7-12 inches wide for double-column figures.
- Put stable IDs on all nodes. Connectors refer to `from` and `to` IDs.
- Use node `image` paths for generated icons or figure panels; keep labels as editable Visio text whenever possible.
- Run `scripts/validate_spec.py` before rendering when a spec is hand-written or derived from a paper paragraph.
- Prefer short node text. Use line breaks only when they improve readability.
- Use one of the style packs unless the user asks for a custom palette: `nature-muted`, `ieee-clean`, `chinese-journal`, `presentation-color`.
- For Chinese papers, prefer `chinese-journal` unless the target journal or slide style suggests otherwise.

## Editing Existing VSDX

- Always create a timestamped backup before destructive edits.
- Prefer Visio COM automation for shape movement, import/export, font styling, and page export.
- Use direct VSDX XML editing only for scoped batch changes such as recoloring, text replacement, or adding simple cloned shapes.
- After editing, export PNG/EMF and run `check_quality.py`.

## Output Standards

- Always keep the `.vsdx` as the editable source of truth.
- Export `.png` for visual review and `.emf` for Word/paper insertion when Visio supports it.
- Verify that text is readable, no important shapes overlap, arrows terminate near intended nodes, and the image is not blank.
- If Visio or pywin32 fails, run `scripts/check_environment.py` and fix the reported dependency before editing figure logic.
- Do not include private paper text, original manuscript files, or sensitive project assets in open-source examples.
