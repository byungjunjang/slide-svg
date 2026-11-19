#!/usr/bin/env python3
"""
Package the /slide skill as the claude.ai custom skill `slide-svg`.

What this produces:
    output/slide-svg.skill    (a zip; every path starts with slide-svg/, the
                               layout skill-creator's package_skill.py writes)
        slide-svg/SKILL.md
        slide-svg/scripts/...
        slide-svg/templates/...
        slide-svg/references/...
        slide-svg/assets/theme-dev-pack.tar.gz  (+ theme-dev-pack.README.md)

    Upload it on claude.ai: Settings > Plugins > Skills > slide-svg >
    upload a new version.

Which tree it packages:
    - A checkout with a `public` remote (the internal repo): the tree committed
      at public/main, i.e. the public edition. The internal working tree has
      internal-only content that must not ship. Push public (or run
      `git fetch public`) first so public/main is current.
    - Any other checkout (a clone of the public repo): the working tree, so a
      theme changed with /theme-init ships as it is.
    - --ref <git-ref> packages that commit instead.

What it changes (the hand-built 2026-11-19 upload is the reference):
    - SKILL.md: the name, title and invocation become `slide-svg`.
    - Text files (.md .py .sh .json .txt): `skills/slide/` becomes
      `skills/slide-svg/`, and line endings become LF.
    - Dev-only files (DEV_PACK: theme-rebake sources, layout previews,
      scripts/dev/) move into assets/theme-dev-pack.tar.gz, with a README
      beside it. No deck run reads them, and moving them keeps the bundle
      under the 200-file limit.

What it enforces:
    - SKILL.md frontmatter passes skill-creator's quick_validate rules.
    - No nested .zip files inside the bundle (claude.ai rejects zip-in-zip).
    - File count under the claude.ai 200-file upload limit.

Why the icon library is *not* included:
    The full Tabler icon library lives outside the skill folder at
    ${REPO_ROOT}/assets/icons/<lib>/<name>.svg. It is intentionally NOT bundled
    here — embedding 6000+ files would blow past the 200-file limit. The skill
    ships ~20 essentials at templates/icons/tabler-outline/ for claude.ai use,
    and embed_icons.py emits a [WARN] then skips when an icon is unavailable.

Why fonts are *not* bundled by default:
    Bundling .ttf files in a claude.ai skill upload does not install fonts on
    the user's machine — the resulting PPTX still falls back to whatever's
    installed locally. The font files are dead weight in the upload bundle.
    They are still kept under repo-root assets/fonts/ for separate (manual)
    distribution; pass --include-fonts if you want them in the upload anyway.

Usage:
    python3 .codex/skills/slide/scripts/package_for_claude_ai.py
    python3 .codex/skills/slide/scripts/package_for_claude_ai.py --ref HEAD
    python3 .codex/skills/slide/scripts/package_for_claude_ai.py --include-fonts
    python3 .codex/skills/slide/scripts/package_for_claude_ai.py --output my.skill
"""

from __future__ import annotations

import argparse
import io
import re
import subprocess
import sys
import tarfile
import time
import zipfile
from fnmatch import fnmatch
from pathlib import Path


# Path layout: <repo>/.codex/skills/slide/scripts/package_for_claude_ai.py
#   parents[0] = .../scripts
#   parents[1] = .../slide        (skill root)
#   parents[4] = repo root
SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]

SKILL_NAME = 'slide-svg'
CLAUDE_AI_FILE_LIMIT = 200
DEFAULT_OUTPUT = REPO_ROOT / 'output' / f'{SKILL_NAME}.skill'
PUBLIC_REF = 'public/main'

TEXT_SUFFIXES = ('.md', '.py', '.sh', '.json', '.txt')
# The trailing slash keeps `skills/slide-plan/` unchanged. Split so this file,
# which ships in the bundle too, does not rewrite its own token.
PATH_OLD, PATH_NEW = 'skills/' + 'slide/', f'skills/{SKILL_NAME}/'

# Each anchor must occur exactly once in SKILL.md; a miss means SKILL.md drifted.
SKILL_MD_RENAMES = (
    ('\nname: slide\n', f'\nname: {SKILL_NAME}\n'),
    ('invokes "/slide".', f'invokes "/{SKILL_NAME}".'),
    ('\n# /slide — ', f'\n# /{SKILL_NAME} — '),
    ('`slide` is a repository-specific workflow skill',
     f'`{SKILL_NAME}` is a repository-specific workflow skill'),
)

FRONTMATTER_KEYS = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}

# Files no deck run reads (fnmatch patterns over skill-relative paths).
DEV_PACK = {
    'charts': 'templates/charts/_source/*',
    'layouts': 'templates/layouts/_source/*',
    'previews': 'templates/layouts/*/_preview/*',
    'refs': 'references/*.tpl.md',
    'dev': 'scripts/dev/*',
}
DEV_PACK_TAR = 'assets/theme-dev-pack.tar.gz'
DEV_PACK_README = 'assets/theme-dev-pack.README.md'
DEV_PACK_README_TEXT = """\
# theme-dev-pack.tar.gz

Development-only and theme-rebake-only assets, archived so the packaged skill
stays under claude.ai's 200-file upload limit. **Nothing in this archive is read
during normal deck generation** — the Strategist → Executor → Export pipeline
never touches these paths, so the skill is fully functional without extracting.

Contents (paths are relative to the skill root; extraction restores them in place):

| Path | What it is | When you need it |
|---|---|---|
| `templates/charts/_source/` ({charts} × `.tpl.svg`) | Tokenized chart template sources | `/theme-init` rebake of the chart library |
| `templates/layouts/_source/` ({layouts} × `.tpl.svg`) | Tokenized layout shell sources | `/theme-init` rebake of the layout pack |
| {preview_dirs} | Rendered layout preview images | Visual reference only |
| `references/*.tpl.md` ({refs} files) | Tokenized reference-doc sources (`design-system.tpl.md`, `strategist.tpl.md`, …) | `/theme-init` re-render of theme-baked reference docs |
| `scripts/dev/` ({dev} files) | Developer utilities (`build_font_metrics.py`, `sync_codex_mirror.py`, `update_repo.py`, …) | Skill maintenance, not deck generation |

To extract (from the skill root directory):

```bash
tar xzf assets/theme-dev-pack.tar.gz
```

Note: `preflight.py` and `verify_deck.py` reference `scripts/dev/sync_codex_mirror.py`
but explicitly skip that check when the file is absent, so leaving this archive
unextracted is safe — and correct — on claude.ai / Cowork hosts.
"""


def _git(*args: str) -> bytes:
    # core.autocrlf=false: archive the stored (LF) blobs, not a CRLF checkout copy.
    r = subprocess.run(['git', '-c', 'core.autocrlf=false', *args], cwd=REPO_ROOT, capture_output=True)
    if r.returncode:
        raise SystemExit(f"[FAIL] git {' '.join(args)}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout


def default_ref() -> str | None:
    """public/main when this checkout has a `public` remote (the internal repo), else None."""
    try:
        r = subprocess.run(['git', 'remote', 'get-url', 'public'], cwd=REPO_ROOT, capture_output=True)
    except OSError:  # no git at all: package the working tree
        return None
    return PUBLIC_REF if r.returncode == 0 else None


def read_ref(ref: str) -> dict[str, bytes]:
    """Skill files as committed at `ref`."""
    prefix = SKILL_ROOT.relative_to(REPO_ROOT).as_posix() + '/'
    with tarfile.open(fileobj=io.BytesIO(_git('archive', '--format=tar', ref, prefix))) as tf:
        return {m.name.removeprefix(prefix): tf.extractfile(m).read()
                for m in tf.getmembers() if m.isfile()}


def read_worktree() -> dict[str, bytes]:
    return {p.relative_to(SKILL_ROOT).as_posix(): p.read_bytes()
            for p in SKILL_ROOT.rglob('*') if p.is_file()}


def rewrite(rel: str, data: bytes) -> bytes:
    """Text files: LF line endings, `skills/slide/` -> `skills/slide-svg/`."""
    if not rel.endswith(TEXT_SUFFIXES):
        return data
    return data.decode('utf-8').replace('\r\n', '\n').replace(PATH_OLD, PATH_NEW).encode('utf-8')


def rename_skill_md(text: str) -> str:
    for old, new in SKILL_MD_RENAMES:
        if text.count(old) != 1:
            raise SystemExit(f"[FAIL] SKILL.md: expected {old.strip()!r} exactly once; "
                             f"update SKILL_MD_RENAMES in {Path(__file__).name}")
        text = text.replace(old, new)
    return text


def frontmatter_errors(skill_md: str) -> list[str]:
    """skill-creator quick_validate.py rules, without PyYAML."""
    # ponytail: reads only the YAML subset SKILL.md uses (top-level `key: value`
    # lines, indented continuation and `>`/`|` block lines). Switch to
    # yaml.safe_load if the frontmatter grows lists or nested quoting.
    m = re.match(r'---\n(.*?)\n---\n', skill_md, re.S)
    if not m:
        return ['no YAML frontmatter']
    fields: dict[str, str] = {}
    key = None
    for line in m.group(1).splitlines():
        top = re.match(r'([\w-]+):\s*(.*)', line)
        if top:
            key, value = top.groups()
            fields[key] = '' if re.fullmatch(r'[>|][-+]?', value) else value.strip('\'"')
        elif key:
            fields[key] = f'{fields[key]} {line.strip()}'.strip()
    errors = []
    if extra := sorted(set(fields) - FRONTMATTER_KEYS):
        errors.append(f"unexpected key(s): {', '.join(extra)}")
    name = fields.get('name', '')
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', name) or len(name) > 64:
        errors.append(f'name {name!r} must be kebab-case and at most 64 chars')
    desc = fields.get('description', '')
    if not 0 < len(desc) <= 1024:
        errors.append(f'description must be 1-1024 chars (got {len(desc)})')
    if '<' in desc or '>' in desc:
        errors.append('description must not contain < or >')
    return errors


def make_tar_gz(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as tf:
        for rel, data in sorted(files.items()):
            info = tarfile.TarInfo(rel)
            info.size, info.mtime = len(data), int(time.time())
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def build(files: dict[str, bytes]) -> dict[str, bytes]:
    """Source skill tree -> upload tree (see the module docstring)."""
    out = {rel: rewrite(rel, data) for rel, data in files.items()
           if '__pycache__' not in rel.split('/') and not rel.endswith(('.pyc', '.pyo'))}
    out['SKILL.md'] = rename_skill_md(out['SKILL.md'].decode('utf-8')).encode('utf-8')

    dev = {rel: out.pop(rel) for rel in sorted(out) if any(fnmatch(rel, p) for p in DEV_PACK.values())}
    counts = {k: sum(fnmatch(rel, p) for rel in dev) for k, p in DEV_PACK.items()}
    previews = sorted({rel.split('/_preview/')[0] for rel in dev if fnmatch(rel, DEV_PACK['previews'])})
    out[DEV_PACK_TAR] = make_tar_gz(dev)
    out[DEV_PACK_README] = DEV_PACK_README_TEXT.format(
        preview_dirs=', '.join(f'`{d}/_preview/`' for d in previews), **counts).encode('utf-8')
    return out


def bundle_errors(files: dict[str, bytes]) -> list[str]:
    errors = [f'SKILL.md frontmatter: {e}' for e in frontmatter_errors(files['SKILL.md'].decode('utf-8'))]
    nested = sorted(rel for rel in files if rel.endswith('.zip'))
    if nested:
        errors.append(f"{len(nested)} nested .zip file(s), which claude.ai rejects: {', '.join(nested)}")
    if len(files) > CLAUDE_AI_FILE_LIMIT:
        errors.append(f'Bundle has {len(files)} files; claude.ai limit is {CLAUDE_AI_FILE_LIMIT}.')
    return errors


def write_skill(output: Path, files: dict[str, bytes]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for rel, data in sorted(files.items()):
            zf.writestr(f'{SKILL_NAME}/{rel}', data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--ref',
                        help=f'Git ref to package (default: {PUBLIC_REF} when a `public` remote '
                             'exists, else the working tree).')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT,
                        help=f'Output .skill path (default: {DEFAULT_OUTPUT})')
    parser.add_argument('--include-fonts', action='store_true',
                        help='Bundle assets/fonts/ into the upload. Off by default — font files do '
                             'not install on the recipient via a claude.ai upload, so they are dead '
                             'weight in the bundle. Useful only if you intend to distribute the zip '
                             'manually to someone who will install the fonts.')
    args = parser.parse_args(argv)

    ref = args.ref or default_ref()
    if ref:
        source = read_ref(ref)
        print(f"[SRC]  {ref} {_git('log', '-1', '--format=%h %cs', ref).decode().strip()}")
    else:
        source = read_worktree()
        print(f"[SRC]  working tree {SKILL_ROOT}")

    files = build(source)
    if args.include_fonts:
        fonts_dir = REPO_ROOT / 'assets' / 'fonts'
        files.update({f'assets/fonts/{p.relative_to(fonts_dir).as_posix()}': p.read_bytes()
                      for p in fonts_dir.rglob('*') if p.is_file()})

    # Warn if the external full icon library is missing — Claude Code mode
    # will silently fall back to the bundled essentials. Not a build error.
    icons_dir = REPO_ROOT / 'assets' / 'icons'
    if not icons_dir.exists():
        print(f"[WARN] {icons_dir} is absent; Claude Code runs will use only the bundled essentials.")

    errors = bundle_errors(files)
    if errors:
        print()
        print("[FAIL] Validation errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    write_skill(args.output, files)
    size_mb = args.output.stat().st_size / 1024 / 1024
    print()
    print(f"[OK] Wrote {args.output}  ({size_mb:.2f} MB, {len(files)} files)")
    print(f"     claude.ai: Settings > Plugins > Skills > {SKILL_NAME} > upload a new version.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
