#!/usr/bin/env python3
"""Validate and build the uploadable plugin archive: dist/kosif-think-pro-<version>.zip.
Checks: manifests parse and agree, regression suite passes, every skill has frontmatter,
no symlinks/secrets/bytecode, ChatGPT limits (<=100 MB, <=5000 entries, <=20 path segments).
The zip is reproducible (fixed timestamps, sorted entries)."""
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ["plugin.json", ".codex-plugin/plugin.json", "README.md", "CHANGELOG.md", "skills"]
SECRET = re.compile(r"\b(sk-(proj-)?[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}|xox[baprs]-[A-Za-z0-9-]{10,})")


def fail(msg):
    print(f"BUILD FAILED: {msg}")
    sys.exit(1)


def files():
    out = []
    for item in INCLUDE:
        p = ROOT / item
        if p.is_file():
            out.append(p)
        else:
            for f in sorted(p.rglob("*")):
                if f.is_file() and "__pycache__" not in f.parts and f.suffix != ".pyc":
                    out.append(f)
    return out


def main():
    m = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    c = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if m["version"] != c["version"] or m["name"] != c["name"]:
        fail("plugin.json and .codex-plugin/plugin.json disagree")
    for sk in sorted((ROOT / "skills").iterdir()):
        text = (sk / "SKILL.md").read_text(encoding="utf-8") if (sk / "SKILL.md").exists() else ""
        if not text.startswith(f"---\nname: {sk.name}\n") or "\ndescription: " not in text.split("---")[1]:
            fail(f"bad SKILL.md frontmatter in {sk.name}")
    r = subprocess.run([sys.executable, str(ROOT / "skills/kosif-think-pro/scripts/regression_self_test.py")],
                       capture_output=True, text=True)
    print("regression:", r.stdout.strip())
    if r.returncode != 0:
        fail("regression suite failed")
    fs = files()
    for f in fs:
        if f.is_symlink():
            fail(f"symlink not allowed: {f}")
        if len(f.relative_to(ROOT).parts) > 20:
            fail(f"path too deep: {f}")
        if f.suffix in {".py", ".md", ".json"} and "regression_self_test" not in f.name and "code_scan" not in f.name:
            if SECRET.search(f.read_text(encoding="utf-8", errors="ignore")):
                fail(f"possible secret in {f}")
    if len(fs) > 5000:
        fail("too many entries")
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    out = dist / f"{m['name']}-{m['version']}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in fs:
            info = zipfile.ZipInfo(f.relative_to(ROOT).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if f.suffix == ".py" else 0o644) << 16
            z.writestr(info, f.read_bytes())
    size = out.stat().st_size
    if size > 100 * 1024 * 1024:
        fail("archive exceeds 100 MB")
    print(f"built {out.relative_to(ROOT)} · {len(fs)} files · {size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
