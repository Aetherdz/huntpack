#!/usr/bin/env python3
"""Validate every skill in the HuntPack library.

Checks, per skill folder:
  1. A SKILL.md exists (Agent Skills requirement).
  2. YAML frontmatter parses and contains `name` + `description`.
  3. `name` matches the folder name (kebab-case, lowercase).
  4. `description` is non-empty and <= 1024 chars.
  5. No absolute paths (/home/, /root/, /Users/), no private-key markers.
  6. No leftover internal cross-reference files (CROSS-REF.md).

Exit code 0 = all good, 1 = failures. Machine-readable output on stdout.

Usage:
    python3 scripts/validate-skills.py            # validate everything
    python3 scripts/validate-skills.py <path>     # validate one folder
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
LEAK_PATTERNS = [
    re.compile(r"/home/"), re.compile(r"/root/"), re.compile(r"/Users/"),
    re.compile(r"BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY"),
]

# Intentional, educational payload EXAMPLES — these are teaching content, not leaks.
# e.g. an LLM tool-poisoning PoC using file_read("/approved_evil/../../root/.ssh/id_rsa"),
# or a GitHub-dork pattern searching for exposed "BEGIN ... PRIVATE KEY".
ALLOWED_LEAK_FILES = {
    "skills/hunting/web2-vuln-classes/reference/11-llm-ai.md",
    "skills/recon/web2-recon/reference/github-dorking.md",
}

failures = []


def check(folder: Path) -> None:
    name = folder.name
    skill_md = folder / "SKILL.md"
    if not skill_md.exists():
        failures.append(f"[{name}] MISSING SKILL.md")
        return

    text = skill_md.read_text(encoding="utf-8", errors="replace")

    # frontmatter
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        failures.append(f"[{name}] no YAML frontmatter")
        return
    import yaml
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception as e:  # noqa: BLE001
        failures.append(f"[{name}] frontmatter YAML error: {e}")
        return

    fname = fm.get("name")
    fdesc = fm.get("description")
    if not fname:
        failures.append(f"[{name}] missing 'name' in frontmatter")
    elif fname != name:
        failures.append(f"[{name}] frontmatter name '{fname}' != folder name '{name}'")
    if not NAME_RE.match(fname or ""):
        failures.append(f"[{name}] name '{fname}' not lowercase kebab-case")
    if not fdesc:
        failures.append(f"[{name}] missing 'description' in frontmatter")
    elif len(str(fdesc)) > 1024:
        failures.append(f"[{name}] description > 1024 chars ({len(str(fdesc))})")

    # leaks across the whole folder
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".md", ".txt", ".py", ".js", ".sh", ".json", ".yaml", ".yml"):
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                continue
            for pat in LEAK_PATTERNS:
                rel = p.relative_to(ROOT)
                if str(rel) in ALLOWED_LEAK_FILES:
                    continue
                if pat.search(content):
                    failures.append(f"[{name}] leak pattern {pat.pattern} in {rel}")

    # leftover internal cross-ref files
    for cross in folder.rglob("CROSS-REF.md"):
        failures.append(f"[{name}] leftover internal file {cross.relative_to(folder)}")


def main() -> int:
    if len(sys.argv) > 1:
        targets = [Path(sys.argv[1])]
    else:
        targets = [p for p in ROOT.rglob("*/SKILL.md")
                   if p.parent != ROOT and p.parent.name != "references"
                   and not p.parent.parent.name.startswith(".")]
    folders = [t.parent if t.name == "SKILL.md" else t for t in targets]
    # dedupe + only real skill folders (contain SKILL.md)
    seen = set()
    for f in folders:
        r = f.resolve()
        if r in seen:
            continue
        seen.add(r)
        check(f)

    if failures:
        print("\n".join(failures))
        print(f"\n❌ {len(failures)} problem(s) found.")
        return 1
    print(f"✅ All {len(seen)} skills valid.")
    return 0


if __name__ == "__main__":
    try:
        import yaml  # noqa: F401
    except ImportError:
        print("❌ PyYAML required: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    sys.exit(main())
