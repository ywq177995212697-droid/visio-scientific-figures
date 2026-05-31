# AI Image Asset Workflow

Use generated bitmap assets when a figure needs realistic, domain-specific icons or illustrative elements that Visio cannot reproduce well. Keep the main diagram editable in Visio, but import the generated asset as a contained visual element.

## When to Generate Assets

- The user provides an original figure with detailed icons, equipment, screens, maps, dashboards, or physical objects.
- Simple Visio shapes would make the figure look generic or obviously AI-drawn.
- A small realistic icon or pictorial element helps readers recognize a concept faster than text alone.

## Recommended Process

1. Identify the icon or illustration roles from the source figure.
2. Write one concise prompt per asset. Ask for clean, paper-friendly, low-decoration visuals with no text unless text is essential.
3. Generate each asset with the available image generation tool.
4. Save assets under the working example or project folder, for example `assets/sensor-data.png`.
5. Add the asset path to the node with `image`, and choose `image_mode`: `left`, `top`, `fill`, or `shape: image`.
6. Render the Visio file and run the quality checker.

## Prompt Pattern

Use prompts like:

```text
Create a clean scientific icon of [concept], flat semi-realistic style,
paper-friendly, no text, no watermark, white or transparent-looking background,
subtle blue/teal/gray palette, not cartoonish, not glossy, low AI-art look.
```

For diagram panels:

```text
Create a small scientific illustration panel showing [process/object],
minimal background, publication figure style, clear silhouette, no text,
consistent lighting, suitable for insertion into a Visio research diagram.
```

## Quality Rules

- Prefer square or mildly horizontal assets for node icons.
- Avoid generated text inside images; use editable Visio text next to the asset.
- Keep a copy of the generation prompt near the spec when reproducibility matters.
- Do not import private, copyrighted, or sensitive source images into open-source examples.
