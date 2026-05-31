from __future__ import annotations

import argparse
import platform
import sys
from dataclasses import dataclass
from pathlib import Path


FONT_CANDIDATES = {
    "Microsoft YaHei": Path("C:/Windows/Fonts/msyh.ttc"),
    "SimHei": Path("C:/Windows/Fonts/simhei.ttf"),
    "SimSun": Path("C:/Windows/Fonts/simsun.ttc"),
}


@dataclass
class Check:
    name: str
    status: str
    detail: str


def status(ok: bool, name: str, detail: str) -> Check:
    return Check(name, "PASS" if ok else "FAIL", detail)


def optional(name: str, ok: bool, detail: str) -> Check:
    return Check(name, "PASS" if ok else "WARN", detail)


def run_checks(skip_visio: bool = False) -> list[Check]:
    checks: list[Check] = []
    checks.append(status(platform.system() == "Windows", "Windows", platform.platform()))
    checks.append(status(sys.version_info >= (3, 10), "Python 3.10+", sys.version.split()[0]))
    checks.append(import_check("pywin32", "win32com.client"))
    checks.append(import_check("pythoncom", "pythoncom"))
    checks.append(optional("PyYAML", can_import("yaml"), "needed for full YAML syntax"))
    checks.append(optional("Pillow", can_import("PIL"), "optional; useful for image asset inspection"))
    font_hits = [name for name, path in FONT_CANDIDATES.items() if path.exists()]
    checks.append(optional("Chinese fonts", bool(font_hits), ", ".join(font_hits) or "none found"))
    if skip_visio:
        checks.append(Check("Visio COM", "SKIP", "skipped by --skip-visio"))
    else:
        checks.append(visio_check())
    return checks


def can_import(module: str) -> bool:
    try:
        __import__(module)
        return True
    except Exception:
        return False


def import_check(name: str, module: str) -> Check:
    try:
        __import__(module)
        return Check(name, "PASS", module)
    except Exception as exc:
        return Check(name, "FAIL", str(exc))


def visio_check() -> Check:
    try:
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        app = win32com.client.DispatchEx("Visio.Application")
        app.Visible = False
        version = getattr(app, "Version", "unknown")
        app.Quit()
        pythoncom.CoUninitialize()
        return Check("Visio COM", "PASS", f"Microsoft Visio {version}")
    except Exception as exc:
        try:
            pythoncom.CoUninitialize()  # type: ignore[name-defined]
        except Exception:
            pass
        return Check("Visio COM", "FAIL", str(exc))


def render_report(checks: list[Check]) -> str:
    failures = sum(1 for check in checks if check.status == "FAIL")
    warnings = sum(1 for check in checks if check.status == "WARN")
    lines = [
        "# Visio Scientific Figures Environment Report",
        "",
        f"Status: {'PASS' if failures == 0 else 'FAIL'}",
        f"Failures: {failures}",
        f"Warnings: {warnings}",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- [{check.status}] {check.name}: {check.detail}" for check in checks)
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Windows, Python, pywin32, fonts, and Visio COM readiness.")
    parser.add_argument("--skip-visio", action="store_true", help="Skip launching Microsoft Visio.")
    parser.add_argument("--report", type=Path, help="Optional markdown report path.")
    args = parser.parse_args()
    report = render_report(run_checks(skip_visio=args.skip_visio))
    print(report)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    raise SystemExit(1 if "[FAIL]" in report else 0)


if __name__ == "__main__":
    main()
