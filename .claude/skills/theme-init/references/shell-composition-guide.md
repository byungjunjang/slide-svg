# Shell Composition Guide — /theme-init Step 5 상세

> 이 파일은 /theme-init Step 5의 상세 절차이며 해당 스텝 진입 시 로드한다.

### 5. Shell Composition (agent task — re-compose coordinates, alignment, decoration, band)

Step 3 renders **baseline** shells from the global `_source/` (jangpm
geometry) by substituting tokens only. That gives a working light deck,
but the *composition* is still jangpm's. This step is where you (the
agent) re-author the shell composition itself — coordinates, alignment,
decorative elements, and (when the theme defines a band) the narrative
band — so the deck skeleton matches the new design's signature.

**This step is optional.** Skip it for a monochrome rebrand that's happy
with jangpm geometry — the baseline shells already work. Run it whenever
the design guide implies a distinct page architecture (a navy hero, a
spectrum dot row, tag-chip headers, band cards, etc.).

> **Rasterizer preflight (do this before 5b/5c).** The Step 5c review is a
> render-first BLOCKING checkpoint that shows the user PNG thumbnails of the
> composed shells. `preview_shells.py` needs `cairosvg` (crispest) or
> `svglib`+`reportlab` to emit PNGs; without one it can only drop filled
> SVGs and the visual review silently degrades. Install up front:
> `pip install cairosvg` (or `pip install -r .claude/skills/slide/requirements.txt`).
> The dual-mode "no browser binary" purity rule still holds — do **not** add
> Playwright; the cairosvg/svglib path is the supported rasterizer.

**Inputs** (read all four before composing):
1. `theme-active.json` — tokens, including any `colors.shell-*` band tokens.
2. This theme's `DESIGN.md` §1 (mood) · §5 (layout grammar) · §6.0 (shell
   composition) / §6 (page anatomy) — authored in Step 4.
3. The original `design.md` (the user's design guide) — the source of the
   visual signature.
4. The just-rendered **baseline shells** (`templates/layouts/<name>/*.svg`)
   — the starting reference you re-compose.

**5a. Compose the per-theme shell source.** Write four parametric
templates to `templates/layouts/<name>/_shell_src/`:

```
01_cover.tpl.svg  02_chapter.tpl.svg  03_content.tpl.svg  04_ending.tpl.svg
```

Rules for the templates:
- **Colors are tokens, never literals.** Use `{{TOKEN:colors.<name>}}`.
  For the narrative band use `{{TOKEN:colors.shell-bg}}`,
  `{{TOKEN:colors.shell-text}}`, `{{TOKEN:colors.shell-accent}}`; spectrum
  dots address entries by index: `{{TOKEN:colors.shell-spectrum.0}}`,
  `.1`, … (author exactly as many dots as the spectrum length). Null
  band tokens fall back to their light sibling automatically
  (`shell-text`→`text`, etc.), so a monochrome theme still renders.
- **Keep content placeholders** (`{{TITLE}}`, `{{PAGE_TITLE}}`,
  `{{GOVERNING_MESSAGE}}`, …) untouched for the Executor to fill.
- **Narrative shells** (`01_cover` / `02_chapter` / `04_ending`) may go
  full-bleed on `shell-bg`, place the spectrum row, and use a CTA button
  in `shell-accent`.
- **The content shell (`03_content`) stays light** — `bg`/`surface`
  background, `text`/`text-secondary` ink, single `accent`. It MUST keep
  the `{{GOVERNING_MESSAGE}}` GM line. Never paint the band fill or a
  spectrum hue here. (The light-mode relaxation is scoped to the
  narrative band; `validate_shells.py` enforces this.)
- **Permanent locks apply** (see "Locks that persist across themes"):
  viewBox `0 0 1280 720`; every `<text>` carries the full font chain; no
  `<style>`/`class`/`@font-face`/`<foreignObject>`/`textPath`/`rgba()`/
  `<mask>`/`<script>` (use `fill-opacity`, not `rgba`); native shapes,
  no flattened images.

**5b. Render + validate.**

```bash
python3 .claude/skills/theme-init/scripts/render_layouts.py     # now picks up _shell_src/
python3 .claude/skills/theme-init/scripts/validate_shells.py    # FATAL lock check
python3 .claude/skills/theme-init/scripts/preview_shells.py     # build _preview/index.html
```

Fix any `validate_shells` violation in `_shell_src/` and re-render — the
render is deterministic, so identical source yields a clean diff.

**5c. Review checkpoint (BLOCKING — render-first preview loop).** Open
`templates/layouts/<name>/_preview/index.html` (built by
`preview_shells.py`) and present the rendered shells to the user as the
**reference for the proposed shell composition** — the actual rendered
shells, not an ASCII sketch. State, per shell, the signature choices you
made (band, alignment, decoration). Collect feedback, edit `_shell_src/`,
re-render + re-preview, and **repeat until the user approves**. Do not
proceed to sync/verify on the first render. (This is the shell-only loop
inside optional Step 5; the whole-theme gate is Step 6.5 below, which runs
on every completion path.)

**5d. Sync DESIGN.md + anti-slop.** Once approved, bring the references
into line with the composition:
- `templates/layouts/<name>/DESIGN.md` §6.0 (shell composition table) and
  §5/§6 — describe the new layout grammar / page anatomy.
- `anti-slop-theme.md` — regenerated from `theme-active.json`; the band
  allowed-colors table and Rule T9 (band scope) appear automatically when
  `colors.shell-bg` is set. Re-run `init_theme.py` (or
  `render_anti_slop_theme.py`) to refresh.

**Idempotence / re-runs.** `_shell_src/` is agent-authored source and is
**preserved** across `/theme-init` re-runs (like the hand-authored
DESIGN.md) — `render_layouts.py` keeps consuming it, so a token-only
change re-propagates colors with a clean diff and no re-composition. To
re-compose from scratch, delete (or edit) `_shell_src/` and redo 5a–5c.
