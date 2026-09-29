#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path

PORTS = (8767, 8768, 8769)

HOSTED = {
    "algebra": "https://tnezki.github.io/teacher_shared/algebra/",
    "physics": "https://tnezki.github.io/teacher_shared/physics/",
    "calc": "https://tnezki.github.io/teacher_shared/calc/",
}

LOCAL_TARGETS = {
    "algebra": [
        "http://127.0.0.1:8767/shared/algebra/index.html",
        "http://127.0.0.1:8767/shared/algebra/",
        "/shared/algebra/index.html",
        "/shared/algebra/",
        "shared/algebra/index.html",
    ],
    "physics": [
        "http://127.0.0.1:8768/shared/physics/index.html",
        "http://127.0.0.1:8768/shared/physics/",
        "/shared/physics/index.html",
        "/shared/physics/",
        "shared/physics/index.html",
    ],
    "calc": [
        "http://127.0.0.1:8769/shared/calc/index.html",
        "http://127.0.0.1:8769/shared/calc/",
        "/shared/calc/index.html",
        "/shared/calc/",
        "shared/calc/index.html",
        "http://127.0.0.1:8769/shared/apcalc/index.html",
        "http://127.0.0.1:8769/shared/apcalc/",
        "/shared/apcalc/index.html",
        "/shared/apcalc/",
        "shared/apcalc/index.html",
    ],
}

TEXT_EXTS = {
    ".py", ".html", ".htm", ".js", ".json", ".txt", ".command", ".sh",
    ".css", ".md", ".yaml", ".yml", ".toml",
}
SKIP_DIRS = {
    ".git", "__pycache__", "logs", "_logs", "backups", "_backups",
    "migration_backups", "node_modules", ".venv", "venv",
}

TOP_SYNC_MARKER = "local-tools-top-sync"
BACK_TOP_MARKER = "local-tools-back-to-top"

TOP_SYNC_HTML = '''<form class="local-tools-top-sync" method="post" action="http://127.0.0.1:8770/" target="_blank" style="display:contents">
<button type="submit" name="action" value="sync-pull" style="background:#fff;color:#173f73;border:2px solid #173f73;border-radius:14px;padding:12px 18px;font-weight:800;font-size:inherit;cursor:pointer">Pull All Repos</button>
<button type="submit" name="action" value="sync-push" onclick="return confirm('Commit and push current changes in memories, algebra, physics, apcalc, and teacher_shared?');" style="background:#173f73;color:#fff;border:2px solid #173f73;border-radius:14px;padding:12px 18px;font-weight:800;font-size:inherit;cursor:pointer">Commit + Push All Repos</button>
</form>'''

BACK_TOP_HTML = '''<a id="local-tools-back-to-top" href="#" onclick="window.scrollTo({top:0,behavior:'smooth'});return false;" aria-label="Back to top" style="position:fixed;right:22px;bottom:22px;z-index:9999;background:#173f73;color:#fff;text-decoration:none;font-weight:900;border-radius:999px;padding:12px 16px;box-shadow:0 6px 18px rgba(0,0,0,.22)">↑ Top</a>'''


def detect_root() -> Path:
    env = os.environ.get("GITHUB_ROOT", "").strip()
    candidates = []
    if env:
        candidates.append(Path(env).expanduser())
    candidates.extend([Path.home() / "GitHub", Path.home() / "Documents" / "GitHub"])
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "memories").exists():
            return candidate.resolve()
    raise RuntimeError("Could not locate the GitHub workspace root.")


def candidate_files(root: Path):
    tool_roots = [
        root / "_algebra_teacher_tools",
        root / "_physics_teacher_tools",
        root / "_apcalc_teacher_tools",
    ]
    seen = set()
    for tool_root in tool_roots:
        if not tool_root.is_dir():
            continue
        for path in tool_root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix.lower() not in TEXT_EXTS:
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue
            key = str(path.resolve())
            if key not in seen:
                seen.add(key)
                yield path


def co_teacher_context_lines(lines: list[str]) -> set[int]:
    anchors = []
    for i, line in enumerate(lines):
        low = line.lower()
        if "co-teacher agenda" in low or "coteacher agenda" in low or "co teacher agenda" in low:
            anchors.append(i)
    indexes = set()
    for i in anchors:
        a = max(0, i - 30)
        b = min(len(lines), i + 31)
        indexes.update(range(a, b))
    return indexes


def replace_targets(line: str) -> tuple[str, int]:
    changed = 0
    out = line
    for course, targets in LOCAL_TARGETS.items():
        hosted = HOSTED[course]
        for old in sorted(targets, key=len, reverse=True):
            if old in out:
                out = out.replace(old, hosted)
                changed += 1
    return out, changed


def patch_hosted_links(raw: str) -> tuple[str, int]:
    low = raw.lower()
    if not ("co-teacher agenda" in low or "coteacher agenda" in low or "co teacher agenda" in low):
        return raw, 0

    lines = raw.splitlines(keepends=True)
    context = co_teacher_context_lines(lines)
    replacements = 0
    for i in sorted(context):
        new_line, count = replace_targets(lines[i])
        if count:
            lines[i] = new_line
            replacements += count
    updated = "".join(lines)

    anchor_re = re.compile(
        r'(<a\b[^>]*?\bhref\s*=\s*)(["\'])([^"\']*(?:shared/(?:algebra|physics|calc|apcalc))[^"\']*)(\2)([^>]*>.*?co[- ]teacher\s+agenda.*?</a>)',
        re.IGNORECASE | re.DOTALL,
    )

    def anchor_sub(match: re.Match) -> str:
        nonlocal replacements
        href = match.group(3)
        new_href = href
        for course, targets in LOCAL_TARGETS.items():
            for old in sorted(targets, key=len, reverse=True):
                if old in new_href:
                    new_href = new_href.replace(old, HOSTED[course])
        if new_href != href:
            replacements += 1
            return match.group(1) + match.group(2) + new_href + match.group(4) + match.group(5)
        return match.group(0)

    return anchor_re.sub(anchor_sub, updated), replacements




PLANNER_CONTROLS_MARKER = "local-tools-planner-five-controls"

PLANNER_CONTROLS_HTML = """
<style id="local-tools-planner-five-controls-style">
#local-tools-planner-five-controls {
  background:#fff8e8;
  border-top:1px solid #e7bc58;
  border-bottom:1px solid #e7bc58;
  padding:14px 12px 18px;
}
#local-tools-planner-five-controls .lt-heading {
  color:#725714;
  font-weight:900;
  letter-spacing:.02em;
  margin:0 0 10px;
}
#local-tools-planner-five-controls .lt-row {
  display:flex;
  gap:12px;
  flex-wrap:wrap;
  align-items:center;
}
#local-tools-planner-five-controls button {
  border-radius:999px;
  padding:10px 18px;
  font:inherit;
  font-weight:700;
  cursor:pointer;
}
#local-tools-planner-five-controls .lt-outline {
  background:#fff;
  color:#173f73;
  border:2px solid #173f73;
}
#local-tools-planner-five-controls .lt-primary {
  background:#173f73;
  color:#fff;
  border:2px solid #173f73;
}
#local-tools-planner-five-controls .lt-apply {
  background:#d7aa36;
  color:#173f73;
  border:2px solid #9b7718;
}
</style>
<script id="local-tools-planner-five-controls">
// planner-five-controls-runtime-fix-20260929
(function () {
  function txt(el) {
    return (el && (el.textContent || "").replace(/\\s+/g, " ").trim()) || "";
  }
  function findExact(label) {
    var nodes = document.querySelectorAll("button,a");
    for (var i = 0; i < nodes.length; i++) {
      if (txt(nodes[i]) === label && !nodes[i].closest("#local-tools-planner-five-controls")) return nodes[i];
    }
    return null;
  }
  function findHeading(label) {
    var nodes = document.querySelectorAll("h1,h2,h3,h4,h5,h6,div,p,span");
    for (var i = 0; i < nodes.length; i++) {
      if (txt(nodes[i]) === label) return nodes[i];
    }
    return null;
  }
  function proxy(original, label, cls) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = cls;
    b.textContent = label;
    b.onclick = function () { original.click(); return false; };
    return b;
  }
  function syncButton(label, action, cls) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = cls;
    b.textContent = label;
    b.onclick = function () {
      if (action === "sync-push" && !confirm("Commit and push current changes in memories, algebra, physics, apcalc, and teacher_shared?")) return false;
      var form = document.createElement("form");
      form.method = "post";
      form.action = "http://127.0.0.1:8770/";
      form.target = "_blank";
      form.style.display = "none";
      var input = document.createElement("input");
      input.name = "action";
      input.value = action;
      form.appendChild(input);
      document.body.appendChild(form);
      form.submit();
      setTimeout(function(){ form.remove(); }, 1000);
      return false;
    };
    return b;
  }
  function hideLegacySync() {
    var nodes = document.querySelectorAll("button,a");
    for (var i = 0; i < nodes.length; i++) {
      var t = txt(nodes[i]);
      if (t === "Pull All Repos" || t === "Commit + Push All Repos") nodes[i].style.display = "none";
    }
    var headings = document.querySelectorAll("h1,h2,h3,h4,h5,h6,div,p,span");
    for (var j = 0; j < headings.length; j++) {
      if (txt(headings[j]) === "GITHUB") headings[j].style.display = "none";
    }
  }
  function run() {
    if (document.getElementById("local-tools-planner-five-controls")) return;
    var apply = findExact("Apply Changes + Update Agendas");
    var undo = findExact("Undo Changes");
    var jump = findExact("Jump to Current Week");
    var current = findHeading("Current State");
    if (!apply || !undo || !jump || !current) return;

    var originalActionParent = apply.parentElement;
    hideLegacySync();

    var section = document.createElement("section");
    section.id = "local-tools-planner-five-controls";
    var heading = document.createElement("div");
    heading.className = "lt-heading";
    heading.textContent = "GITHUB";
    var row = document.createElement("div");
    row.className = "lt-row";

    row.appendChild(syncButton("Pull All Repos", "sync-pull", "lt-outline"));
    row.appendChild(syncButton("Commit + Push All Repos", "sync-push", "lt-outline"));
    row.appendChild(proxy(apply, "Apply Changes + Update Agendas", "lt-apply"));
    row.appendChild(proxy(undo, "Undo Changes", "lt-outline"));
    row.appendChild(proxy(jump, "Jump to Current Week", "lt-outline"));

    section.appendChild(heading);
    section.appendChild(row);
    current.parentNode.insertBefore(section, current);

    apply.style.display = "none";
    undo.style.display = "none";
    jump.style.display = "none";
    if (originalActionParent) {
      var remaining = txt(originalActionParent);
      var visibleInteractive = 0;
      var controls = originalActionParent.querySelectorAll("button,a,input,select");
      for (var k = 0; k < controls.length; k++) {
        if (controls[k].style.display !== "none") visibleInteractive++;
      }
      if (!remaining || visibleInteractive === 0) originalActionParent.style.display = "none";
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();
</script>
"""


def patch_planner_html(raw: str) -> tuple[str, int]:
    # Only touch real owner Planner pages. Leave every other HTML file alone.
    required = ("Planner Editor", "Apply Changes + Update Agendas", "Current State")
    if not all(marker in raw for marker in required):
        return raw, 0

    out = raw
    changed = 0

    # Remove only our prior injected UI fragments by unique markers/classes.
    patterns = [
        r'<form\\b[^>]*class=["\\\'][^"\\\']*\\blocal-tools-top-sync\\b[^"\\\']*["\\\'][^>]*>.*?</form>',
        r'<section\\b[^>]*id=["\\\']local-tools-planner-controls["\\\'][^>]*>.*?</section>',
        r'<style\\b[^>]*id=["\\\']local-tools-safe-planner-controls-style["\\\'][^>]*>.*?</style>\\s*<script\\b[^>]*id=["\\\']local-tools-safe-planner-controls["\\\'][^>]*>.*?</script>',
        r'<style\\b[^>]*id=["\\\']local-tools-planner-five-controls-style["\\\'][^>]*>.*?</style>\\s*<script\\b[^>]*id=["\\\']local-tools-planner-five-controls["\\\'][^>]*>.*?</script>',
    ]
    for pattern in patterns:
        out, count = re.subn(pattern, '', out, flags=re.IGNORECASE | re.DOTALL)
        changed += count

    # Keep Teacher Tools retired, as already approved.
    teacher_patterns = [
        r'<li\\b[^>]*>\\s*<a\\b[^>]*>\\s*Teacher Tools\\s*</a>\\s*</li>',
        r'<a\\b[^>]*>\\s*Teacher Tools\\s*</a>',
        r'<button\\b[^>]*>\\s*Teacher Tools\\s*</button>',
    ]
    for pattern in teacher_patterns:
        out, count = re.subn(pattern, '', out, flags=re.IGNORECASE | re.DOTALL)
        changed += count

    if PLANNER_CONTROLS_MARKER not in out and '</body>' in out.lower():
        idx = out.lower().rfind('</body>')
        out = out[:idx] + PLANNER_CONTROLS_HTML + out[idx:]
        changed += 1

    if BACK_TOP_MARKER not in out and '</body>' in out.lower():
        idx = out.lower().rfind('</body>')
        out = out[:idx] + BACK_TOP_HTML + out[idx:]
        changed += 1

    return out, changed

def rewrite_file(path: Path) -> tuple[str | None, int]:
    try:
        raw = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None, 0

    updated, link_changes = patch_hosted_links(raw)
    ui_changes = 0
    if path.suffix.lower() in {".html", ".htm"}:
        updated, ui_changes = patch_planner_html(updated)

    total = link_changes + ui_changes
    if updated == raw:
        return None, 0
    return updated, total


def backup_and_write(root: Path, path: Path, updated: str, backup_root: Path) -> None:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        rel = Path(path.name)
    backup = backup_root / rel
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)
    path.write_text(updated, encoding="utf-8")


def listener_pids(port: int) -> list[int]:
    result = subprocess.run(
        ["/usr/sbin/lsof", "-tiTCP:%d" % port, "-sTCP:LISTEN"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    out = []
    for token in result.stdout.split():
        try:
            out.append(int(token))
        except ValueError:
            pass
    return out


def stop_planners() -> None:
    pids = sorted(set(pid for port in PORTS for pid in listener_pids(port)))
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.time() + 3
    while time.time() < deadline:
        alive = []
        for pid in pids:
            try:
                os.kill(pid, 0)
                alive.append(pid)
            except ProcessLookupError:
                pass
        if not alive:
            break
        time.sleep(0.1)


def start_planners(root: Path) -> bool:
    runtime = root / "_algebra_teacher_tools" / "runtime" / "Start Teacher Tools Runtime.command"
    if not runtime.exists():
        print(f"Planner runtime launcher not found: {runtime}")
        return False
    log_dir = root / "_algebra_teacher_tools" / "runtime" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log = log_dir / "planner_owner_ui_restart.log"
    with log.open("ab") as handle:
        subprocess.Popen(
            ["/bin/bash", str(runtime)],
            stdout=handle,
            stderr=handle,
            start_new_session=True,
        )
    deadline = time.time() + 30
    while time.time() < deadline:
        if all(listener_pids(p) for p in PORTS):
            return True
        time.sleep(0.5)
    return all(listener_pids(p) for p in PORTS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restart-if-changed", action="store_true")
    args = parser.parse_args()

    root = detect_root()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = root / "_curriculum_transfers" / "backups" / f"planner_owner_ui_{stamp}"

    changed_files: list[Path] = []
    total_changes = 0
    for path in candidate_files(root):
        updated, changes = rewrite_file(path)
        if updated is None:
            continue
        backup_and_write(root, path, updated, backup_root)
        changed_files.append(path)
        total_changes += changes

    if changed_files:
        print(f"Updated {len(changed_files)} Planner source file(s); {total_changes} owner-page/link change(s).")
        for path in changed_files:
            print(f"  UPDATED: {path}")
        print(f"Backups: {backup_root}")
        if args.restart_if_changed:
            print("Restarting Planner services on ports 8767-8769...")
            stop_planners()
            if start_planners(root):
                print("Planner runtime restarted successfully.")
            else:
                print("WARNING: Planner runtime did not fully return. Check the runtime log.")
                return 2
    else:
        print("Planner hosted links and owner-page polish already current, or no matching source was found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
