# Visio COM Notes

This skill targets Windows with Microsoft Visio and `pywin32`.

## Startup Pattern

```python
import win32com.client

app = win32com.client.Dispatch("Visio.Application")
app.Visible = False
app.AlertResponse = 7
try:
    doc = app.Documents.Add("")
    page = app.ActivePage
finally:
    app.Quit()
```

## Useful Cells

- Page size: `PageSheet.CellsU("PageWidth")`, `PageSheet.CellsU("PageHeight")`
- Position and size: `PinX`, `PinY`, `Width`, `Height`, `LocPinX`, `LocPinY`
- Fill and line: `FillForegnd`, `FillPattern`, `LineColor`, `LineWeight`, `LinePattern`
- Text: `Char.Size`, `Char.Color`, `Char.Font`, `Char.Style`, `Para.HorzAlign`, `VerticalAlign`
- Arrows: `EndArrow`, `BeginArrow`
- Rounded rectangles: `Rounding`

## Coordinate Convention

The helper scripts use a top-left mental model for specs and convert to Visio's bottom-left page coordinates. Keep all spec coordinates in inches from the top-left corner.

## Editing Existing Files

- Create a backup before modifying a `.vsdx`.
- Use COM when shape IDs, groups, images, or exports matter.
- Use ZIP/XML editing only when changing known cells or text in `visio/pages/page1.xml`.
- Run a fresh export and quality report after every edit.
