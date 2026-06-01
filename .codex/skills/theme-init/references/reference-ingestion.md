# Reference-deck ingestion — layout-device extraction (slide-svg)

`scripts/ingest_reference.py` parses a hand-made reference deck (the deck a new
theme should echo) **deterministically (SVG via regex, PPTX via python-pptx; no
LLM)** and reports the layout devices it uses, so the agent can recommend a
`surface.card_style`, seed the DESIGN.md §5 review draft with measured hints,
and review the signals before authoring §5/§6.

It is a **recommender, not an applier**: it never edits `theme-active.json`,
never re-renders, and never replaces the human-authored §5/§6 vocabulary (it
only adds a clearly-labeled, marker-fenced hint block). Applying a recommended
`card_style` means setting `surface.card_style` in the Step 2 theme JSON and
re-running `/theme-init` — Phase 1 owns rendering.

## Run it

```bash
python3 .codex/skills/theme-init/scripts/ingest_reference.py \
  --reference <deck-dir | deck.svg | deck.pptx> \
  [--out devices.json] [--design-md <theme>/DESIGN.md] [--no-seed] [--quiet]
```

`--reference` resolution: a directory uses `svg_final/*.svg` → `svg_output/*.svg`
→ `*.svg`, else the newest `*.pptx`; a single `.svg`/`.pptx` file is also
accepted. PDF / images / other formats are **unsupported** — the script prints
guidance and exits 1 without touching anything. Exit codes: `0` ok · `1`
unsupported/zero-slides · `2` path not found.

## Output JSON schema (v1.0)

The device set + schema mirror the slide-html reference implementation so
`card_style` and friends mean the same thing across slide-html / slide-svg /
slide-pencil. slide-svg's only schema delta: `source_format` ("svg" | "pptx")
replaces slide-html's HTML-specific `pptx_css` field.

```jsonc
{
  "version": "1.0",
  "source": "<reference path>",
  "source_format": "svg",            // svg | pptx  (replaces slide-html's pptx_css)
  "slides_analyzed": 12,
  "devices": {
    // value ∈ filled|hairline|borderless|null. confidence: high (read from card
    // shape fill/stroke) · medium (weak/mixed signal) · low/null (couldn't tell).
    "card_style":          { "value": "hairline", "confidence": "high", "evidence": "…" },
    "surface_alternation": { "present": true, "slides_using": 4, "ratio": 0.33 },
    "hairline_dividers":   { "present": true, "count": 9 },
    "cta":                 { "present": true, "count": 2 },   // low confidence (vector)
    "kicker":              { "present": true, "count": 14 }   // low confidence (vector)
  },
  "per_slide": [
    { "slide": "01_cover", "cards": 0, "surface_alt": false, "rules": 1, "cta": 0, "kicker": 1 }
  ]
}
```

## How signals are read (vector formats have no CSS classes)

slide-svg slides forbid the `class` attribute, so detection is **geometry- and
shape-based**, not class-based. `card_style` / `surface_alternation` /
`hairline_dividers` read reliably from shapes; `cta` / `kicker` are inherently
**lower-confidence** (heuristic on small rounded buttons / all-caps short text)
and cap at `medium`. Because the script only recommends, a missing signal just
falls back to the user authoring §5/§6 by hand.

| device | SVG signal | PPTX signal | feeds |
|---|---|---|---|
| `card_style` | rounded `<rect>` smaller than canvas: stroke → hairline · fill-only → filled · none → borderless | rounded/rect autoshape: `line.width`>0 → hairline · solid fill → filled · none → borderless | `surface.card_style` recommendation (re-init to apply) |
| `surface_alternation` | ≥2 distinct non-bg fills per slide | ≥2 distinct shape/background fills per slide | DESIGN.md §5 surface grouping |
| `hairline_dividers` | thin `<rect>` + `<line>` | connectors + very flat shapes | DESIGN.md §6 divider weight |
| `cta` | small rounded `<rect>` + text (low conf.) | small rounded autoshape + text (low conf.) | DESIGN.md §5 CTA device |
| `kicker` | small all-caps / positive-tracking `<text>` (low conf.) | all-caps short run (low conf.) | DESIGN.md §6 eyebrow |

## Integration

Run during `/theme-init` before authoring the theme JSON (Step 2) when the user
supplies a reference deck:

1. stores nothing in a manifest (slide-svg has none) — provenance lives in the
   DESIGN.md §5 fenced block;
2. prints the `card_style` recommendation, and — if it differs from the active
   `surface.card_style` — the exact way to apply it (set the Step 2 token,
   re-render);
3. with `--design-md`, inserts an **additive, marker-fenced** "참조 자동추출(초안)"
   hint block into DESIGN.md §5. It does **not** remove the AGENT-FILL prompts —
   the user still fills the canonical §5/§6 by hand. Re-running replaces the
   fenced block in place (idempotent).

PDF/image ingestion is a documented future extension (would need agent vision,
which breaks the deterministic-stdlib contract).

## Shell-composition harness note (Task 6b)

slide-svg already covers author-time validation/preview via `validate_shells.py`
(FATAL lock check) + `preview_shells.py` (render-first review) + the Step 5
`_shell_src/` recomposition + the BLOCKING Step 5c review. slide-html's
`author_layouts.py` manifest/prep/confirm state machine is therefore **not
ported** — its only capability slide-svg lacked was reference ingestion, which
this script provides. The manifest/classify/thumbs/confirm ceremony would
duplicate the existing Step 5 harness.
