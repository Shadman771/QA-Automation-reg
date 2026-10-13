"""Screenshot capture into the PASS/FAIL bucket, named by Test Case ID."""
import shutil
from pathlib import Path

from config.settings import SCREENSHOTS_DIR, PROJECT_ROOT, feature_dir


def capture(page, feature: str, case_id: str, passed: bool) -> Path:
    bucket = "PASS" if passed else "FAIL"
    out_dir = feature_dir(SCREENSHOTS_DIR / bucket, feature) / case_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{case_id}.png"
    page.screenshot(path=str(out_path), full_page=True)
    return out_path


def finalize_evidence(evidence: list, feature: str, case_id: str, passed: bool) -> list:
    """Moves the per-step screenshots a Case captured (in a temporary
    staging dir, screenshots/_pending/<Feature>/<CaseID>/) into the final
    PASS/FAIL bucket alongside the case's final screenshot, once the case's
    pass/fail outcome is known. Returns a list of {n, kind, label,
    screenshot} dicts (screenshot path relative to PROJECT_ROOT, forward
    slashes) ready to embed in the report/JSON."""
    bucket = "PASS" if passed else "FAIL"
    out_dir = feature_dir(SCREENSHOTS_DIR / bucket, feature) / case_id
    out_dir.mkdir(parents=True, exist_ok=True)

    result = []
    for item in evidence:
        rel = ""
        src = item.get("path")
        try:
            if src and Path(src).exists():
                dest = out_dir / Path(src).name
                shutil.move(str(src), str(dest))
                rel = str(dest.relative_to(PROJECT_ROOT)).replace("\\", "/")
        except Exception:
            rel = ""
        result.append({
            "n": item.get("n"), "kind": item.get("kind"),
            "label": item.get("label"), "screenshot": rel,
        })

    pending_dir = feature_dir(SCREENSHOTS_DIR / "_pending", feature) / case_id
    try:
        if pending_dir.exists() and not any(pending_dir.iterdir()):
            pending_dir.rmdir()
    except Exception:
        pass
    return result
