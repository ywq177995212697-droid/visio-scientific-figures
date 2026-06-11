# Contributing

## Scope

This repository is for editable Visio scientific figures, not a general-purpose diagramming toolkit. Keep contributions aligned with reproducible figure generation, validation, export, and quality assurance.

## Before Opening a PR

1. Keep examples open-source-safe. Do not add private manuscript text, proprietary diagrams, or unredacted project assets.
2. Prefer spec-driven changes over one-off manual output edits.
3. Update the relevant reference doc when you add or change a public field, style, or workflow.
4. Refresh `docs/gallery/` only when the visible example output actually changed.

## Verification

Run these before submitting changes:

```powershell
python -m py_compile .\skills\visio-scientific-figures\scripts\render_spec.py .\skills\visio-scientific-figures\scripts\check_quality.py .\skills\visio-scientific-figures\scripts\validate_spec.py .\skills\visio-scientific-figures\scripts\check_environment.py
python -m pytest
python .\skills\visio-scientific-figures\scripts\validate_spec.py .\examples\toy_flowchart\figure_spec.yaml
python .\skills\visio-scientific-figures\scripts\check_environment.py --skip-visio
```

If your change touches Visio rendering or output layout, also run at least one full render plus `check_quality.py`.

## Pull Request Notes

- Explain the user-facing effect first.
- Mention any new spec fields, validation rules, or quality checks.
- Include screenshot changes only when the visual output changed in a meaningful way.
