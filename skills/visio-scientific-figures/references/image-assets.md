# AI Image Asset Workflow

Use generated or screenshot-cropped bitmap assets when a figure needs realistic, domain-specific icons or illustrative elements that Visio cannot reproduce well. Keep the main diagram editable in Visio, but import the asset as a contained visual element.

## When to Generate Assets

- The user provides an original figure with detailed icons, equipment, screens, maps, dashboards, or physical objects.
- Simple Visio shapes would make the figure look generic or obviously AI-drawn.
- A small realistic icon or pictorial element helps readers recognize a concept faster than text alone.

## Default Asset Order

1. Call Image 2 first for a clean icon or small illustration draft.
2. If the reference figure already contains a useful visual cue, crop that screenshot fragment and reuse it as a bitmap asset.
3. Put the bitmap inside the Visio node, but keep the text, title, and connector structure editable in Visio.

## Recommended Process

1. Identify the icon or illustration roles from the source figure.
2. Write one concise prompt per asset. Ask for clean, paper-friendly, low-decoration visuals with no text unless text is essential.
3. Generate each asset with the available image generation tool, such as Image 2 when available in the host environment.
4. If Image 2 is not enough on its own, crop supporting screenshot fragments from the blurred or anonymized reference figure.
5. Save assets under the working example or project folder, for example `assets/sensor-data.png`.
6. Add the asset path to the node with `image`, and choose `image_mode`: `left`, `top`, `fill`, or `shape: image`.
7. Render the Visio file and run the quality checker.

## Screenshot Crop Use

Screenshot crops are appropriate when:

- the reference figure has a panel silhouette, layout hint, or icon cluster worth preserving
- you have already blurred or anonymized the source image
- a direct crop communicates the source structure better than a full redraw

Do not use screenshot crops as a substitute for editable labels. Crop the visual part only, and rebuild labels and arrows as native Visio content.

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
- Prefer transparent, white, or very light backgrounds so imported assets blend into Visio nodes.
- Treat screenshot crops as supporting visuals, not the final editable figure.
- Keep a copy of the generation prompt near the spec when reproducibility matters.
- Do not import private, copyrighted, or sensitive source images into open-source examples.
