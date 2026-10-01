#!/usr/bin/env python3
"""Build the single-folder Claude skill (claude.ai / Claude Code / Agent SDK) from the plugin source.

Claude skills accept exactly one SKILL.md per skill, so the seven expert skills become
`references/domains/<skill>.md`, their reference folders become `references/<skill>/`,
and every helper script is flattened into `scripts/`. Paths inside the markdown are
rewritten accordingly. Output: dist-claude/kosif-think-pro/ (+ .skill/.zip packages).
"""
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "skills"
OUT = ROOT / "dist-claude"
SKILL = OUT / "kosif-think-pro"
EXPERTS = ["kosif-vision", "kosif-image-studio", "kosif-lighting", "kosif-audio", "kosif-code-master",
           "kosif-video", "kosif-audit-ifrs", "kosif-prompt-master", "kosif-web-design", "kosif-github",
           "kosif-computer-use", "kosif-jev"]

DESCRIPTION = (
    "KOSIF Think Pro for Claude: think-first reasoning, a 100-member expert council and a measured expert studio. "
    "Use it for careful reasoning, verification, decisions and research, and for: image analysis and image/video "
    "prompts, prompt engineering for LLMs and agents, website and UI design with accessibility audits, GitHub work "
    "(commits, pull requests, CI), operating a browser or computer safely, Jev yes/no, choice and score judgements, "
    "lighting, audio and Arabic songs for Suno, programming and code review, stories and ads, accounting, VAT, IFRS "
    "and audit. Also for the commands /pro /verify /decide /bias /ideate /council /council100 /forge /prompt "
    "/site /webaudit /gh /pr /computer /jev /img /code /review /story /journal, and Arabic requests such as "
    "تحليل صورة، برومبت، تصميم موقع، جيت هاب، تحكم في الكمبيوتر، مجلس الخبراء، برمجة، قيد محاسبي. It measures "
    "with bundled Python helpers and never claims a tool ran when it did not."
)

HOST = """## Running inside Claude
- Helpers are plain Python 3 scripts in `scripts/` (numpy/Pillow needed only for image/audio analysis). Run them with the code-execution or bash tool, e.g. `echo '{...}' | python3 scripts/decision_sensitivity.py`. If no code tool is available, say the measurement did not run and label results as estimated.
- Claude does not generate images, video or audio by itself. Deliver the final, linted prompt (and Character/Style Locks) for the user's generator unless an image/design tool is actually connected in this conversation; then follow the Execution Contract and postcondition check.
- Wherever a domain file says "Code Interpreter", read it as Claude's code execution.
- The KOSIF live runtime/MCP bridge (kosif_mobile_*, kosif_auto) is optional; treat it as unavailable unless its tools are present in this conversation.
- Jev tools may appear under any MCP prefix (e.g. `…jev_noul`, `…jev_choice`, `…jev_score`); computer/browser tools may be computer-use, Claude in Chrome, the built-in browser, or Playwright in the sandbox; GitHub may be MCP tools, `gh`, or git. Use what is actually exposed and load the host's own skill for that tool first when one is listed.
- Domain protocols live in `references/domains/<name>.md`; read the one(s) the request needs before answering.
"""


def rewrite(text, domain=None):
    core = "\x00CORE\x00"
    text = re.sub(r"\.\./kosif-think-pro/references/", core, text)
    text = re.sub(r"\.\./kosif-think-pro/scripts/", "scripts/", text)
    text = re.sub(r"\.\./(kosif-[a-z-]+)/SKILL\.md", r"references/domains/\1.md", text)
    text = re.sub(r"\.\./kosif-[a-z-]+/scripts/", "scripts/", text)
    for e in EXPERTS:
        text = text.replace(f"../{e}/references/", f"references/{e}/")
    if domain:
        text = re.sub(r"(?<![\w/.-])references/(?!domains/|kosif-)([\w.-]+\.(?:md|json))", rf"references/{domain}/\1", text)
    text = re.sub(r"(?<![\w/.-])(kosif-[a-z-]+)/references/", r"references/\1/", text)
    text = re.sub(r"(?<![\w/.-])kosif-[a-z-]+/scripts/", "scripts/", text)
    text = text.replace(core, "references/")
    text = text.replace("Code Interpreter", "code execution")
    return text


def strip_front(md):
    if md.startswith("---"):
        return md.split("---", 2)[2].lstrip("\n")
    return md


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    (SKILL / "scripts").mkdir(parents=True)
    (SKILL / "references" / "domains").mkdir(parents=True)
    core = SRC / "kosif-think-pro"
    # core references (incl. books/) and scripts
    shutil.copytree(core / "references", SKILL / "references", dirs_exist_ok=True)
    for f in core.glob("scripts/*.py"):
        shutil.copy2(f, SKILL / "scripts" / f.name)
    for e in EXPERTS:
        d = SRC / e
        for f in d.glob("scripts/*.py"):
            if (SKILL / "scripts" / f.name).exists():
                raise SystemExit(f"script name clash: {f.name}")
            shutil.copy2(f, SKILL / "scripts" / f.name)
        if (d / "references").exists():
            dst = SKILL / "references" / e
            shutil.copytree(d / "references", dst)
            for md in dst.glob("*.md"):
                md.write_text(rewrite(md.read_text(encoding="utf-8"), e), encoding="utf-8")
        body = strip_front((d / "SKILL.md").read_text(encoding="utf-8"))
        (SKILL / "references" / "domains" / f"{e}.md").write_text(rewrite(body, e), encoding="utf-8")
    for md in [*(SKILL / "references").glob("*.md"), *(SKILL / "references" / "books").glob("*.md")]:
        md.write_text(rewrite(md.read_text(encoding="utf-8")), encoding="utf-8")
    body = strip_front((core / "SKILL.md").read_text(encoding="utf-8"))
    for e in EXPERTS:
        body = body.replace(f"| `{e}` |", f"| `references/domains/{e}.md` |")
    body = rewrite(body)
    body = body.replace("## Universal first hop", HOST + "\n## Universal first hop", 1)
    front = f"---\nname: kosif-think-pro\ndescription: {json.dumps(DESCRIPTION, ensure_ascii=False)}\n---\n"
    (SKILL / "SKILL.md").write_text(front + body, encoding="utf-8")
    for p in SKILL.rglob("__pycache__"):
        shutil.rmtree(p)
    r = subprocess.run([sys.executable, str(SKILL / "scripts" / "regression_self_test.py")], capture_output=True, text=True)
    print("claude-layout regression:", r.stdout.strip())
    if r.returncode != 0:
        raise SystemExit("regression failed in Claude layout")
    for p in SKILL.rglob("__pycache__"):
        shutil.rmtree(p)
    files = sorted(p for p in SKILL.rglob("*") if p.is_file())
    for ext in (".skill", ".zip"):
        out = OUT / f"kosif-think-pro{ext}"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for f in files:
                info = zipfile.ZipInfo(f.relative_to(OUT).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o755 if f.suffix == ".py" else 0o644) << 16
                z.writestr(info, f.read_bytes())
        print(f"built {out.relative_to(ROOT)} · {len(files)} files · {out.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    build()
