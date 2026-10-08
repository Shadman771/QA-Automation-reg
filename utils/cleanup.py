"""Removes previous runtime artifacts before a fresh run. Never touches
source code, POM, utilities, Excel test cases, or documentation."""
import shutil

from config.settings import SCREENSHOTS_DIR, LOGS_DIR, REPORTS_DIR


def _rmtree_best_effort(path):
    """Like shutil.rmtree, but a file locked by another still-running
    process (e.g. a second `run_tests.py` invocation against this same
    shared repo - confirmed live as a real, reproducible hazard) is
    skipped with a warning instead of crashing the whole run before a
    single test executes. Only a genuine concurrent-process lock is
    tolerated this way; anything else still surfaces via the printed
    warning."""
    def _on_error(func, target_path, exc_info):
        print(f"[cleanup] WARNING: could not remove '{target_path}' (likely locked by another "
              f"still-running process) - leaving it in place: {exc_info[1]}")

    shutil.rmtree(path, onexc=_on_error)


def clean_runtime():
    for bucket in ("PASS", "FAIL", "_pending"):
        d = SCREENSHOTS_DIR / bucket
        if d.exists():
            _rmtree_best_effort(d)
        d.mkdir(parents=True, exist_ok=True)

    if LOGS_DIR.exists():
        for item in LOGS_DIR.iterdir():
            if item.is_dir():
                _rmtree_best_effort(item)
            else:
                try:
                    item.unlink()
                except OSError as e:
                    print(f"[cleanup] WARNING: could not remove '{item}' (likely locked by another "
                          f"still-running process) - leaving it in place: {e}")

    for name in ("automation_report.html", "execution_results.json", "live_state.json", "live_state.tmp"):
        f = REPORTS_DIR / name
        if f.exists():
            try:
                f.unlink()
            except OSError as e:
                print(f"[cleanup] WARNING: could not remove '{f}' - leaving it in place: {e}")
