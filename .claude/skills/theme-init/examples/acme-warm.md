# Acme Warm — Design Guide

**Identifier:** `acme-warm`
**Display name:** Acme Warm

## Brand character

Acme Warm is an editorial-forward theme for Korean B2B lecture decks that want
approachability over corporate polish. Warm off-white paper, orange-600 accent,
and Noto Sans KR for bilingual readability.

## Color palette

| Token | Value | Notes |
|-------|-------|-------|
| bg | `#FFF8F0` | warm off-white, paper-like |
| surface | `#FFFFFF` | card white |
| surface-alt | `#FAF3E8` | subtle grouped background |
| text | `#1A1410` | espresso-black (not pure black) |
| text-secondary | `#6B5A4F` | muted secondary |
| text-tertiary | `#A89890` | tertiary / captions |
| border | `#E8DFD4` | default divider |
| border-strong | `#D4C8B8` | stronger divider |
| accent | `#FF6B35` | brand orange, primary accent |
| accent-soft | `#FFEDE0` | accent-tinted background |
| accent-ink | `#C04818` | pressed / dark accent |
| positive | `#2E7D32` | growth indicator |
| positive-soft | `#E8F5E9` |  |
| negative | `#C62828` | decline indicator |
| negative-soft | `#FFEBEE` |  |
| warning | `#E65100` | caution |
| warning-soft | `#FFF3E0` |  |

## Typography

**Primary font:** Noto Sans KR. The full CSS font-family chain should include
`"Apple SD Gothic Neo"`, `"Malgun Gothic"`, `sans-serif` fallbacks.

Use the default 7-step scale (display 56 / display-sm 40 / headline 32 /
title 18.4 / body 15.2 / caption 12.8 / label 12.8).

## Radius / stroke / spacing

Use the 8px-grid defaults (4/8/12/16/20/24/32/40/48/56/64). Radius scale:
xs 4, sm 8, md 12, lg 12, xl 20, pill 9999. Strokes: icon 2, divider 1,
emphasis 2.

## Assets

Icon library: **tabler-outline** (fallback tabler-filled). No brand character.

## Voice

- **Tone:** warm, practical, conversational-but-precise
- **POV:** second-person direct (Korean존댓말)
- **Register:** Korean B2B lecture / workshop
- **Forbidden phrases:** "킹왕짱", "혁신적인", "압도적"
- **GM hint:** One action-oriented sentence starting with a verb (가져가세요, 기억하세요, 시도하세요).
