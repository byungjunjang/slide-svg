# Canvas Format Specification

> See shared-standards.md for SVG basic rules.

## Only Supported Format

The `slide` skill locks output to a single canvas: **PPT 16:9, 1280×720**. This is the Jangpm Slide Design System's canonical deck format; no other sizes are supported by this skill.

| Format | viewBox | Dimensions | Ratio | Use Case |
|--------|---------|------------|-------|----------|
| **PPT 16:9** | `0 0 1280 720` | 1280×720 | 16:9 | Korean lecture decks, business presentations (Jangpm default) |

If a user requests a different canvas (4:3, Xiaohongshu, Story, square, A4, etc.), redirect them:

> 이 스킬은 Jangpm 디자인 시스템에 맞춘 1280×720 데크 전용입니다. 다른 캔버스 포맷(세로형 포스터, SNS 카드 등)이 필요하면 별도 도구를 사용하세요.

## Layout Principles (1280×720)

- Visual flow: Z-pattern, left → right
- Margins: slide padding `var(--space-14)` (56px) on all sides; bottom `var(--space-16)` (64px) to reserve `.gm` line space
- Card dimensions (guideline): single-row 530–600px wide, double-row 265–295px wide
- Title area: ~100px tall at top (`.headline`, 32px)
- GM (governing message) bar: absolutely positioned, bottom 64px, horizontally centered

## ViewBox Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <!-- content -->
</svg>
```

## project_manager.py Format Flag

The `project_manager.py init --format` flag still accepts legacy values (`ppt169`, `ppt43`, `xhs`, `story`, …) for CLI compatibility. **Always use `ppt169` under this skill.** Other formats will build a project scaffold, but the Jangpm design rules (`design-system.md`, `anti-slop-core.md`, `anti-slop-theme.md`) are calibrated to 1280×720 and are not guaranteed to read correctly at other sizes.
