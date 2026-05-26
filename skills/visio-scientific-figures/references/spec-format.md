# Figure Spec Format

The renderer accepts JSON files and JSON-compatible `.yaml` files without extra dependencies. Full YAML works when `PyYAML` is installed.

Minimum fields:

```json
{
  "template": "flowchart",
  "title": "Figure title",
  "canvas": { "width_in": 7.5, "height_in": 4.8 },
  "style": "chinese-journal",
  "nodes": [
    { "id": "input", "text": "Input" },
    { "id": "model", "text": "Model" }
  ],
  "groups": [],
  "connectors": [
    { "from": "input", "to": "model", "label": "feeds" }
  ],
  "exports": { "dir": "output", "stem": "figure" }
}
```

## Fields

- `template`: one of `flowchart`, `framework`, `layered-system`, `matrix`, `mechanism`.
- `title`: top title rendered as Visio text.
- `canvas.width_in`, `canvas.height_in`: page size in inches.
- `style`: one of `nature-muted`, `ieee-clean`, `chinese-journal`, `presentation-color`, or an object with a `base` and overrides.
- `nodes`: stable diagram elements. Each node requires `id`; use `text`, `x`, `y`, `w`, `h`, `shape`, `fill`, `line`, `font_size`, and `bold` when needed.
- `groups`: framework bands with `id`, `title`, and `nodes`.
- `connectors`: arrows with `from`, `to`, optional `label`, and optional `dashed`.
- `exports`: either `{ "dir": "...", "stem": "..." }` or explicit `vsdx`, `png`, and `emf` paths.

## Template Notes

- `flowchart` lays nodes left-to-right and wraps after five nodes unless explicit coordinates are provided.
- `framework` lays groups as horizontal bands and distributes each group's nodes.
- `layered-system` draws nested rectangles from the node order.
- `matrix` uses a `matrix` object with `rows`, `columns`, and `cells`.
- `mechanism` places nodes around an ellipse and connects specified edges.
