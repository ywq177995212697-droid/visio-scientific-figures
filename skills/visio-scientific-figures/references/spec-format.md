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
    { "id": "input", "text": "Input", "image": "assets/input-icon.png" },
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
- `nodes`: stable diagram elements. Each node requires `id`; use `text`, `x`, `y`, `w`, `h`, `shape`, `fill`, `line`, `font_size`, `bold`, `image`, `image_mode`, and `image_pad` when needed.
- `groups`: framework bands with `id`, `title`, and `nodes`.
- `connectors`: arrows with `from`, `to`, optional `label`, and optional `dashed`.
- `exports`: either `{ "dir": "...", "stem": "..." }` or explicit `vsdx`, `png`, and `emf` paths.

## Template Notes

- `flowchart` lays nodes left-to-right and wraps after five nodes unless explicit coordinates are provided.
- `framework` lays groups as horizontal bands and distributes each group's nodes.
- `layered-system` draws nested rectangles from the node order.
- `matrix` uses a `matrix` object with `rows`, `columns`, and `cells`.
- `mechanism` places nodes around an ellipse and connects specified edges.

## Image Assets

Use `image` to import a local PNG, JPG, SVG, or EMF into a node. Relative paths are resolved from the spec file's directory.

```json
{
  "id": "sensor",
  "text": "Sensor data",
  "image": "assets/sensor-data.png",
  "image_mode": "left"
}
```

Supported image modes:

- `left`: image on the left, text on the right. Best for icon+label nodes.
- `top`: image above text. Best for larger illustrative nodes.
- `fill`: image fills the node frame with no label overlay.

Set `"shape": "image"` to import an image as the node itself, so connectors attach to the imported image bounds.
