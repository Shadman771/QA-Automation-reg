"""Publishes the finished HTML report to GitHub Pages after every run.

Copies reports/automation_report.html to docs/index.html and pushes it on
the current branch. GitHub Pages (once enabled - see README.md > "Public
report link") serves whatever is at docs/index.html on that branch at a
stable public URL, so the link never changes between runs even though the
content does.

This is best-effort and must never fail a test run: any error (no network,
stale git credentials, nothing to commit, etc.) is swallowed and reported
as "not published" rather than raised.
"""
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from config.settings import PROJECT_ROOT

DOCS_DIR = PROJECT_ROOT / "docs"
PAGES_URL = "https://shadmanshilon.github.io/Reg-Automation/"


def publish_report(report_path: Path) -> Optional[str]:
    """Returns the public URL if the report was actually pushed this call,
    None if publishing did not happen for any reason."""
    try:
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(report_path, DOCS_DIR / "index.html")

        subprocess.run(
            ["git", "add", "docs/index.html"],
            cwd=PROJECT_ROOT, capture_output=True, timeout=15, check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "chore: publish latest QA report to GitHub Pages"],
            cwd=PROJECT_ROOT, capture_output=True, timeout=15, text=True,
        )  # non-zero exit here just means "nothing changed" - not an error
        push = subprocess.run(
            ["git", "push"],
            cwd=PROJECT_ROOT, capture_output=True, timeout=30, text=True,
        )
        if push.returncode != 0:
            return None
        return PAGES_URL
    except Exception:
        return None
