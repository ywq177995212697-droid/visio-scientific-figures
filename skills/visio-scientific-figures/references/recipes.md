# Recipes

Use these recipes when turning fuzzy research requests into editable Visio outputs.

## Paper Paragraph to Framework Figure

1. Extract 3-5 modules from the paragraph.
2. Put supporting resources in lower bands, method modules in middle bands, and outputs/evaluation in upper bands.
3. Use `framework` with explicit `groups`.
4. Keep each node label under 8 words when possible.
5. Render, run `check_quality.py`, and revise until the report has no errors.

## Source Icon to Visio-Friendly Asset

1. Decide whether Visio primitives are enough. Use native Visio shapes for boxes, arrows, bands, and labels.
2. For icons, equipment, screenshots, or realistic panels, call Image 2 first and generate a clean first-pass asset.
3. If the source figure already contains a useful blurred or anonymized visual fragment, crop that screenshot area and use it as a supporting asset.
4. Save the asset under the example or project `assets/` folder.
5. Reference it from the node with `image` and choose `image_mode`: `left`, `top`, or `fill`.
6. Keep text labels editable in Visio unless the user explicitly wants a purely pictorial panel.

## Blurred Source Figure to Complex Showcase

1. Blur or anonymize the source figure before it enters the open-source example set.
2. Decide which parts should stay as screenshot-cropped context panels and which parts should be redrawn as editable Visio structure.
3. Use Image 2 for missing icons or small scientific illustrations that would otherwise look weak in Visio.
4. Replace private terms with neutral labels in the final `figure_spec`.
5. Rebuild the logic, grouping, and connector layout as native Visio content.
6. Export and run `check_quality.py` until the complex showcase reads clearly at paper scale.

## Quality Repair Loop

1. Run `validate_spec.py` before rendering.
2. Render with `render_spec.py`.
3. Run `check_quality.py`.
4. If the report flags bounds, overlap, contrast, or text overflow, fix the spec first.
5. Re-render from the spec so the figure remains reproducible.

## Claude Code Use

Claude Code can use the same `SKILL.md`, `scripts/`, `references/`, `schema/`, and `assets/`. The `agents/openai.yaml` file is Codex UI metadata and can be ignored by Claude Code.
