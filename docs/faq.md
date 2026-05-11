# FAQ

## Q: When should I run `/slide-plan` before `/slide`? (체계적인 데크가 필요할 때)

`/slide-plan` is an **optional** planning layer that runs before `/slide`. Both modes coexist; the right choice depends on deck complexity.

**Use `/slide-plan` first when**:
- The deck has **> 8 slides** and a story arc matters (lecture, executive review, sales pitch — not a quick info dump)
- You're feeding **multiple source files** and need explicit evidence mapping per slide
- The audience is specific (executives, students, prospects) and **role-aware structure** helps (cover → exec_summary → findings → insight → cta vs. just bullets)
- You expect to **iterate on structure** before generating SVGs (cheap to revise a JSON plan; expensive to redo 12 SVGs)
- You want **plan-time quality enforcement** — `validate_plan.py` rejects chart slides without takeaway, slides without evidence sources, lazy 3-consecutive-same-family runs, etc.

**Skip `/slide-plan` (use `/slide` directly) when**:
- The deck is **< 6 slides**
- A single source document is being summarized
- You want a **quick draft** without planning overhead
- You explicitly say "간단하게", "빠르게", "그냥 슬라이드만"

**How `/slide` reacts to either mode**:
- If `output/<project>/slide_plan.json` exists → **Plan-Consuming mode**. Strategist transcribes the plan + active theme into `design_spec.md`; Eight Confirmations are reduced to a one-screen active-theme lock confirmation.
- If no plan exists → **Standalone mode**. Eight Confirmations run as before. **No regression** for legacy users.

In both modes, Layer 1 quality rules **R2** (chart needs takeaway), **R3** (length pressure), **R4** (no lazy repetition) are checked at the Strategist→Executor boundary as a common quality floor.

**Typical commands**:
```
# Quick deck — Standalone
/slide AI 도입 효과 발표 6장 만들어줘.

# Systematic deck — Plan-Consuming
/slide-plan AI 도입 효과 임원 보고서 12장. KPI 중심, 다음 분기 OKR 승인 요청.
# (review markdown summary, confirm, then:)
/slide
```

`/slide-plan` writes `output/<project>/slide_plan.json` (the plan SSOT) plus a markdown summary printed in the chat for review. `validate_plan.py` runs automatically inside the skill; you can re-run it anytime:
```bash
python3 .claude/skills/slide-plan/scripts/validate_plan.py output/<project>/slide_plan.json
```

See `.claude/skills/slide-plan/SKILL.md` for the full schema and the `slide_role` / `chart_strategy` enums.

---

## Q: How do I change the design system / theme? (테마 교체)

Run **`/theme-init`**. The skill is a **one-shot full replacement** — it does not layer themes, and runtime multi-theming is not supported (PPTX bakes tokens into DrawingML at export time).

The flow is **agent-driven** — no API key, no external SDK:

1. You (or the Claude agent invoking `/theme-init`) read the user's design guide and extract tokens into a partial JSON matching the v1 token contract (`references/token-contract.json`). Any token the guide doesn't specify should stay `null`.
2. `fill_theme_defaults.py` fills those nulls with monochrome grayscale safe defaults and writes the complete theme to `references/theme-active.json`.
3. `validate_theme.py` checks the result against the v1 contract schema. Any violation aborts the run with a pointed error list.
4. Every downstream reference is regenerated from templates: the four layout SVGs (`templates/layouts/<name>/*.svg`), `design-system.md`, `anti-slop-theme.md`, `strategist.md`, `executor.md`, and the HTML-gallery CSS.
5. A diff summary shows which token groups changed versus the prior theme.

Typical command (one line, all steps):
```bash
python3 .claude/skills/theme-init/scripts/init_theme.py --fill-from /tmp/theme-draft.json
```

Re-render without changing tokens (after hand-editing `theme-active.json`):
```bash
python3 .claude/skills/theme-init/scripts/init_theme.py
```

**Canvas stays locked at 1280×720** across themes — that constraint is baked into every `_source/*.tpl.svg` and the executor's remediation math. A different canvas format is out of scope for this skill and requires a separate tool.

The only Python dependency is `jsonschema` (for validate). See `.claude/skills/theme-init/SKILL.md` for the full extraction rules, examples, and failure modes.

---

## Q: What source formats does PPT Master accept?

Almost anything: **PDF**, **DOCX**, **PPTX**, **EPUB**, **HTML**, **LaTeX**, **RST**, **URLs** (including WeChat articles), **Markdown**, or just plain text pasted into the conversation. The AI agent converts your source material to Markdown automatically before generating slides.

## Q: Can PPT Master produce formats other than PowerPoint?

Yes. Besides the standard **16:9** and **4:3** presentation formats, PPT Master supports social media and marketing formats out of the box:

| Format | Use Case |
|--------|----------|
| Xiaohongshu (RED) 3:4 | Image-text sharing, knowledge posts |
| WeChat Moments / IG 1:1 | Square posters, brand showcases |
| Story / TikTok 9:16 | Vertical stories, short video covers |
| WeChat Article Header | WeChat article cover images |
| A4 Print | Print posters, flyers |

Just specify the format when starting a project (e.g., `--format xhs`). The output is still a `.pptx` file containing native shapes.

## Q: What AI tools work with PPT Master?

PPT Master works with any AI coding agent that can read files and run shell commands — **Claude Code** (CLI / VS Code / JetBrains / Web), **VS Code Copilot**, **Codex**, and others. See the cost comparison below for pricing differences.

## Q: Can I use AI-generated images in my presentation?

Yes. PPT Master includes a built-in image generation script that supports multiple providers (Gemini, OpenAI, FLUX, Qwen, Zhipu, etc.). During the Strategist phase, if you choose "AI generation" for the image approach, the pipeline will automatically generate images based on your content. You can also provide your own images — just place them in the project's `images/` folder.

## Q: Can I edit the generated presentations?

Yes! Both files are saved to `exports/` with a timestamp. The native `.pptx` produces **native PowerPoint shapes** — all text, graphics, and colors are directly editable without any conversion. The `_svg.pptx` is an SVG snapshot kept as a visual reference backup. Requires **Office 2016** or later.

## Q: Isn't using Claude too expensive?

It depends on how you use it. If you're using a direct API or subscription quota, a single presentation may cost around **$5** — but compared to spending 1–2 days building a presentation manually, this is a reasonable trade-off.

There are much cheaper options. **VS Code Copilot** at $10/month gives you 300 standard requests, which converts to roughly **100 premium (Opus-level) requests**. By default PPT Master has 2 confirmation rounds (template selection + eight confirmations), but if you specify "no template" upfront, it reduces to just **1 confirmation round — only 2 messages** (AI asks, you confirm). That means each presentation costs about **6 Opus requests** or **2 Sonnet requests**. At the $0.04 USD/request overage rate:

| Model | Requests per PPT | Overage Cost |
|-------|:-----------------:|:------------:|
| Opus | ~6 | ~$0.24 USD |
| Sonnet | ~2 | ~$0.08 USD |

For a complete presentation, **$0.08–$0.24 USD** is not expensive at all.

## Q: Are the charts in the generated PPTX editable?

Charts are rendered as **custom-designed SVG graphics** converted to native PowerPoint shapes — not Excel-driven chart objects. This gives them a polished, high-fidelity appearance that often looks better than default PowerPoint charts. However, the underlying data is not editable via PowerPoint's chart editor. If you need a live, data-driven chart (e.g., one you can update by editing a spreadsheet), you will need to manually replace it with a native PowerPoint chart after export.

## Q: Which AI model works best?

**Claude** (Opus / Sonnet) is the recommended and most tested model. SVG layout requires precise absolute-coordinate calculations (font size x character count x container width), and Claude handles this significantly better than alternatives.

**GPT series** models tend to produce more layout issues — text overflowing containers, misaligned elements, coordinate miscalculations. If you must use a non-Claude model, try enabling Fast mode and keep expectations for layout precision lower.

Other models (Gemini, GLM, MiniMax, etc.) vary in quality. In general, models with stronger frontend/visual capabilities produce better results.

## Q: Text overflows or elements are misaligned — what can I do?

This is almost always a model capability issue, not a bug in PPT Master. SVG layout is essentially manual absolute positioning — the model must calculate coordinates, font metrics, and container sizes correctly.

**Fixes to try**:
1. Switch to **Claude** (Opus or Sonnet) if you're using another model
2. Tell the AI which specific page has the problem and describe the issue — it can regenerate individual pages
3. Open the SVG source file directly and ask the AI to fix coordinates
4. Remember: the generated PPTX is a **high-quality starting point**, not a final deliverable — minor adjustments in PowerPoint are expected

## Q: How long does a presentation take to generate?

A typical 10–15 page presentation takes about **10–20 minutes** with a fast model. Generation is **intentionally serial** (one page at a time) to maintain visual consistency across slides — parallel generation was tested and produced inconsistent styles.

If generation feels slow, check your model's token throughput. The bottleneck is usually the model's output speed, not the scripts.

## Q: Can I preview or fix individual pages before the full export?

Yes. You can **interrupt the workflow at any time** — after the first few pages are generated, review them and give feedback. The AI can regenerate specific pages based on your comments. You don't need to wait until the end to make corrections.

For post-generation fixes, simply tell the AI: "Page 3 has a layout issue — the title overlaps the chart" and it will fix that specific SVG.

## Q: How do I create a custom template?

Want to turn a PPT you love into a reusable template for PPT Master? Here's how:

**Step 1 — Prepare Reference Material**

The simplest path is still to prepare screenshots of the key page types from your reference PPT — cover page, table of contents, chapter divider, content page, and closing page. Save them as images in a single folder with clear, descriptive filenames (e.g., `cover.png`, `toc.png`, `chapter.png`, `content.png`, `closing.png`).

If you already have the original `.pptx` template file, you can also provide it as a reference source. PPT Master can extract reusable background images, logos, theme colors, and font metadata from the PPTX first, then use those assets during template reconstruction.

**Step 2 — Let AI Create the Template**

Use an AI coding agent (Claude Code, Codex, etc.) and ask it to use the **PPT Master `/create-template` workflow** to convert your reference material into a template. The more context you give, the better the result — for example:

- Template name and intended use case (e.g., government reports, premium consulting)
- Desired tone and color palette (e.g., "modern and restrained, dark blue primary")
- Category preference (`brand` / `general` / `scenario` / `government` / `special`)
- Canvas format, if not the default 16:9

You don't need to supply every detail upfront — the AI agent will ask follow-up questions to fill in anything missing (template ID, theme mode, etc.).

**Step 3 — Wait for the Result**

The AI agent will handle the rest — analyzing your screenshots, building the layout definitions, and registering the template so it appears as a selectable option in the PPT Master workflow.

> **Tip**: The more specific you are about the style and use case, the better the generated template will match your expectations.

---

> For more questions, see [`.claude/skills/slide/SKILL.md`](../.claude/skills/slide/SKILL.md) and the project [`CLAUDE.md`](../CLAUDE.md).
