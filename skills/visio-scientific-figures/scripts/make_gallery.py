from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_CASES = [
    "research_framework_with_assets",
]


def copy_gallery(repo_root: Path, cases: list[str], docs_dir: Path) -> list[Path]:
    docs_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for case in cases:
        src = repo_root / "examples" / case / "output" / f"{case}.png"
        if not src.exists():
            continue
        dst = docs_dir / f"{case}.png"
        shutil.copyfile(src, dst)
        copied.append(dst)
    return copied


def write_index(docs_dir: Path, copied: list[Path]) -> None:
    lines = [
        "# Gallery",
        "",
        "Generated preview image for the main open-source-safe showcase.",
        "",
    ]
    if not copied:
        lines.append("No gallery images found. Render examples first, then run `make_gallery.py`.")
    for image in copied:
        title = image.stem.replace("_", " ").title()
        lines.extend([f"## {title}", "", f"![{title}]({image.name})", ""])
    (docs_dir / "README.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy generated example PNGs into docs/gallery.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--docs-dir", type=Path, default=None)
    parser.add_argument("--case", action="append", dest="cases")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    docs_dir = args.docs_dir.resolve() if args.docs_dir else repo_root / "docs" / "gallery"
    copied = copy_gallery(repo_root, args.cases or DEFAULT_CASES, docs_dir)
    write_index(docs_dir, copied)
    for path in copied:
        print(path)


if __name__ == "__main__":
    main()
