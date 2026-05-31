# Quality Guidelines

Use the quality checker as a first pass, then inspect the PNG manually.

## Paper Figure Targets

- Keep single-column figures around 3.3-4.0 inches wide and double-column figures around 6.8-7.5 inches wide when the journal uses IEEE-like layout.
- Keep Chinese labels at 8 pt or larger for dense figures and 9-11 pt for normal diagrams.
- Use consistent line weights, usually 0.9-1.4 pt for boxes and arrows.
- Avoid more than five dominant colors in one figure. Use color to separate semantic groups, not to decorate.
- Prefer EMF for insertion into Word when the journal workflow allows it; keep PNG for review and web preview.

## Review Checklist

- Title and node labels match the paper terminology.
- No label overlaps another label, arrow, or important shape.
- All arrows have clear direction and terminate near the intended target.
- No connector is suspiciously short, detached from nodes, or missing an arrowhead when it represents direction.
- Layered diagrams encode hierarchy visually, not only through labels.
- Framework diagrams distinguish input, processing, support, and output regions.
- The figure remains readable when zoomed to the size it will occupy in the paper.

## Common Fixes

- If text overflows, shorten labels first; increase box width second; reduce font only as a last resort.
- If the palette looks too loud for a paper, switch to `nature-muted` or `ieee-clean`.
- If the figure is for a Chinese journal, switch to `chinese-journal` and verify Microsoft YaHei, SimHei, or SimSun is available.
- If many arrows cross, change the template or add explicit `x`, `y`, `w`, and `h` coordinates to key nodes.
