#!/usr/bin/env python3
"""
PPT Master - SVG Quality Check Tool

Checks whether SVG files comply with project technical specifications.

Usage:
    python3 scripts/svg_quality_checker.py <svg_file>
    python3 scripts/svg_quality_checker.py <directory>
    python3 scripts/svg_quality_checker.py --all examples
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

try:
    from project_utils import CANVAS_FORMATS
    from error_helper import ErrorHelper
except ImportError:
    print("Warning: Unable to import dependency modules")
    CANVAS_FORMATS = {}
    ErrorHelper = None


def _active_primary_font():
    """Primary font name from the ACTIVE theme chain, or None if unavailable.

    The font check validates against the active theme (theme-active.json) instead
    of an obsolete system-UI allow-list, which warned on every themed slide because
    no deck uses 'system-ui'/'-apple-system'. None ⇒ theme unreadable ⇒ skip the
    check rather than emit a false warning.
    """
    try:
        import json
        theme_path = Path(__file__).resolve().parent.parent / "references" / "theme-active.json"
        chain = json.loads(theme_path.read_text(encoding="utf-8"))["typography"]["font-chain"]
    except Exception:
        return None
    first = chain.split(",")[0].strip().strip("'\"")
    return first or None


# ============================================================
# Warn-level composition measurements (anti-slop Rules 21/22/23 + chart-accent audit)
# Pure helpers: content string in, measured value out. Wired into check_file as
# advisory warnings (never errors) so they inform without blocking export.
# ============================================================

CANVAS_W, CANVAS_H = 1280, 720
# Content shell free-compose region (executor §1: x=56, y=160, w=1168, h=480).
CONTENT_AREA = (56, 160, 1168, 480)
# Top-right breathing corner kept clear of primary content (anti-slop Rule 22).
QUIET_ZONE = (1024, 0, 256, 160)

_HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}")


def _active_theme_hexes() -> set:
    """Every hex value in the active theme's color palette (uppercased).

    Empty set ⇒ theme unreadable ⇒ callers skip the off-theme audit rather than
    flag every color as off-theme.
    """
    try:
        import json
        theme_path = Path(__file__).resolve().parent.parent / "references" / "theme-active.json"
        colors = json.loads(theme_path.read_text(encoding="utf-8")).get("colors", {})
    except Exception:
        return set()
    return {v.upper() for v in colors.values()
            if isinstance(v, str) and _HEX_RE.fullmatch(v)}


def off_theme_hexes(content: str, allowed: set) -> set:
    """Hex colors in `content` that are not in the active theme palette.

    Catches hardcoded ppt-master / off-theme hues leaking into authored slides
    (chart-accent hardcode audit). White/black are common literals but
    are intentionally NOT auto-allowed — the theme palette is the contract.
    """
    allowed_up = {h.upper() for h in allowed}
    return {h.upper() for h in _HEX_RE.findall(content)} - allowed_up


COLOR_ALLOW_FILENAME = ".theme-color-allow"


def load_color_allowlist(project_dir: Path) -> set:
    """Per-project hex allowlist (`.theme-color-allow`, one #RRGGBB per line).

    Escape hatch for legitimate off-palette colors (brand logos, partner marks).
    Blank lines and non-hex lines are ignored, so the file tolerates comments.
    """
    allow_path = Path(project_dir) / COLOR_ALLOW_FILENAME
    if not allow_path.is_file():
        return set()
    hexes = set()
    for line in allow_path.read_text(encoding="utf-8", errors="replace").splitlines():
        token = line.strip()
        if _HEX_RE.fullmatch(token):
            hexes.add(token.upper())
    return hexes


def _tag_attr_strings(content: str, tag: str) -> list:
    """Attribute string for each `<tag ...>` occurrence."""
    return re.findall(rf"<{tag}\b([^>]*)", content)


def _attr_num(attrs: str, name: str):
    m = re.search(rf'\b{name}\s*=\s*"(-?[\d.]+)"', attrs)
    return float(m.group(1)) if m else None


def parse_boxes(content: str, tag: str) -> list:
    """`(x, y, w, h)` for each `<tag>` that has all four of x/y/width/height."""
    boxes = []
    for attrs in _tag_attr_strings(content, tag):
        x, y = _attr_num(attrs, "x"), _attr_num(attrs, "y")
        w, h = _attr_num(attrs, "width"), _attr_num(attrs, "height")
        if None not in (x, y, w, h):
            boxes.append((x, y, w, h))
    return boxes


def parse_text_anchors(content: str) -> list:
    """`(x, y)` anchor for each `<text>` element with both x and y."""
    pts = []
    for attrs in _tag_attr_strings(content, "text"):
        x, y = _attr_num(attrs, "x"), _attr_num(attrs, "y")
        if x is not None and y is not None:
            pts.append((x, y))
    return pts


def _point_in_box(px: float, py: float, box) -> bool:
    x, y, w, h = box
    return x <= px <= x + w and y <= py <= y + h


def _boxes_intersect(a, b) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def _is_background(box) -> bool:
    """A near-full-canvas rect is the slide background, not foreground content."""
    _, _, w, h = box
    return w * h >= 0.85 * CANVAS_W * CANVAS_H


def texts_over_images(content: str) -> int:
    """Count `<text>` anchors that fall inside any `<image>` bbox (Rule 23)."""
    images = parse_boxes(content, "image")
    if not images:
        return 0
    return sum(1 for (px, py) in parse_text_anchors(content)
               if any(_point_in_box(px, py, b) for b in images))


def quiet_zone_hits(content: str) -> int:
    """Count primary-content marks intruding the top-right quiet zone (Rule 22):
    foreground rect/image bboxes, plus text anchors and polyline/path points (a
    chart legend or annotation in the corner counts too). The zone is y<=160 —
    above the content area — so charts/tables drawn at y>=160 never intrude."""
    qx, qy, qw, qh = QUIET_ZONE
    n = sum(1 for b in parse_boxes(content, "rect") + parse_boxes(content, "image")
            if not _is_background(b) and _boxes_intersect(b, QUIET_ZONE))
    marks = parse_text_anchors(content) + _polyline_points(content) + _path_points(content)
    n += sum(1 for (px, py) in marks if qx <= px <= qx + qw and qy <= py <= qy + qh)
    return n


def _area(box) -> float:
    return box[2] * box[3] if box else 0.0


# ============================================================
# Text-box overlap + safe-area measurements (WARN-level)
# Text extents come from the export pipeline's measurer (real glyph advances
# when font_metrics.json is present) so the checker sees what PPTX will get.
# ============================================================

# Slide safe area: left/right padding --space-14 (56px, design-system §spacing),
# top 40px, bottom 680px (the band below is reserved for the .gm line).
SAFE_AREA = (56, 40, 1224, 680)
# GM line anchor band (matches verify_deck.GM_Y_RANGE) — exempt from safe-area.
_GM_Y_RANGE = (655, 705)
# Overlap is flagged only past this share of the smaller box — adjacent
# label/value pairs commonly touch by a few px without being a defect.
TEXT_OVERLAP_MIN_SHARE = 0.20
# Pairs whose font sizes differ by this factor are display+label compositions
# (e.g. a 200px stat over a 13px caption): the big glyph's em-box padding
# swallows the label without any visual collision, so they are skipped.
TEXT_OVERLAP_MAX_FS_RATIO = 2.5

try:
    from svg_to_pptx.drawingml_utils import estimate_text_width as _measure_text_width
except ImportError:
    _measure_text_width = None


_TEXT_ELEM_RE = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.DOTALL)


def parse_text_elements(content: str) -> list:
    """`(x, y, font_size, font_weight, anchor, text)` per `<text>` element.

    Elements without x/y or carrying a transform (coords not resolvable by a
    regex parser) are skipped.
    """
    out = []
    for m in _TEXT_ELEM_RE.finditer(content):
        attrs, inner = m.group(1), m.group(2)
        if "transform" in attrs:
            continue
        x, y = _attr_num(attrs, "x"), _attr_num(attrs, "y")
        if x is None or y is None:
            continue
        fs_m = re.search(r'font-size\s*=\s*"([\d.]+)', attrs)
        fw_m = re.search(r'font-weight\s*=\s*"([^"]+)"', attrs)
        anchor_m = re.search(r'text-anchor\s*=\s*"([^"]+)"', attrs)
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", inner)).strip()
        if not text:
            continue
        out.append((x, y, float(fs_m.group(1)) if fs_m else 16.0,
                    fw_m.group(1) if fw_m else "400",
                    anchor_m.group(1) if anchor_m else "start", text))
    return out


def _text_boxes_with_meta(content: str) -> list:
    """`(box, anchor_y, anchor, font_size, text)` per text element — box is the
    estimated visual extent (no export headroom). Mirrors convert_text's anchor
    math; height spans ascent (0.85em above the baseline) plus descent (0.25em)."""
    if _measure_text_width is None:
        return []
    out = []
    for (x, y, fs, fw, anchor, text) in parse_text_elements(content):
        w = _measure_text_width(text, fs, fw)
        if anchor == "middle":
            bx = x - w / 2
        elif anchor == "end":
            bx = x - w
        else:
            bx = x
        out.append(((bx, y - fs * 0.85, w, fs * 1.1), y, anchor, fs, text))
    return out


def _overlap_share(a, b) -> float:
    """Intersection area as a share of the smaller box."""
    ix = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    iy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    smaller = min(a[2] * a[3], b[2] * b[3])
    return (ix * iy) / smaller if smaller > 0 else 0.0


def text_box_overlaps(content: str) -> list:
    """Pairs of text boxes overlapping past TEXT_OVERLAP_MIN_SHARE.

    Skipped: display+label pairs (font-size ratio ≥ TEXT_OVERLAP_MAX_FS_RATIO)
    and decorative single-glyph texts (a giant pull-quote mark's em box is
    mostly empty space).
    """
    items = [(box, fs, text) for (box, _, _, fs, text)
             in _text_boxes_with_meta(content)
             if not (len(text) == 1 and not text.isalnum())]
    hits = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            (box_a, fs_a, text_a), (box_b, fs_b, text_b) = items[i], items[j]
            if max(fs_a, fs_b) / max(min(fs_a, fs_b), 1) >= TEXT_OVERLAP_MAX_FS_RATIO:
                continue
            share = _overlap_share(box_a, box_b)
            if share > TEXT_OVERLAP_MIN_SHARE:
                hits.append((text_a[:24], text_b[:24], int(round(share * 100))))
    return hits


def _is_bleed_band(box) -> bool:
    """Full-width or full-height rect — intentional shell band, not content."""
    _, _, w, h = box
    return w >= CANVAS_W * 0.98 or h >= CANVAS_H * 0.98


def safe_area_violations(content: str) -> list:
    """Foreground marks escaping the slide safe area (x<56 / x>1224 / y<40 /
    y>680). Backgrounds, bleed bands, full-bleed images, and the GM line are
    exempt; text is judged by its estimated visual box."""
    x_min, y_min, x_max, y_max = SAFE_AREA
    hits = []

    for ((bx, by, w, h), anchor_y, anchor, _fs, text) in _text_boxes_with_meta(content):
        if anchor_y >= _GM_Y_RANGE[0]:
            # Footer band: the GM line plus page numbers / footer captions
            # legitimately sit below the content area — x-only judgement.
            if bx < x_min or bx + w > x_max + 2:  # +2: page numbers end at 1224
                hits.append(f'text "{text[:24]}" '
                            f'({bx:.0f},{by:.0f},{w:.0f}×{h:.0f})')
            continue
        if bx < x_min or bx + w > x_max or by < y_min or by + h > y_max:
            hits.append(f'text "{text[:24]}" '
                        f'({bx:.0f},{by:.0f},{w:.0f}×{h:.0f})')

    for box in parse_boxes(content, "rect"):
        if _is_background(box) or _is_bleed_band(box):
            continue
        x, y, w, h = box
        if w >= 1000 and y >= 600 and x >= x_min and x + w <= x_max:
            continue  # deliberate full-content-width footer band behind the GM
        if x < x_min or x + w > x_max or y < y_min or y + h > y_max:
            hits.append(f"rect ({x:.0f},{y:.0f},{w:.0f}×{h:.0f})")

    for box in parse_boxes(content, "image"):
        if _is_background(box) or _is_bleed_band(box):
            continue
        x, y, w, h = box
        if x < x_min or x + w > x_max or y < y_min or y + h > y_max:
            hits.append(f"image ({x:.0f},{y:.0f},{w:.0f}×{h:.0f})")

    for attrs in _tag_attr_strings(content, "circle"):
        cx, cy, r = _attr_num(attrs, "cx"), _attr_num(attrs, "cy"), _attr_num(attrs, "r")
        if cx is None or cy is None:
            continue
        rr = r or 0
        if rr <= 8:
            continue  # decorative dot / bullet — its center is what's placed
        if cx - rr < x_min or cx + rr > x_max or cy - rr < y_min or cy + rr > y_max:
            hits.append(f"circle (cx={cx:.0f},cy={cy:.0f},r={rr:.0f})")

    return hits


def _bbox_of_points(points: list):
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def _polyline_points(content: str) -> list:
    pts = []
    for raw in re.findall(r'points\s*=\s*"([^"]+)"', content):
        nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", raw)]
        pts += list(zip(nums[0::2], nums[1::2]))
    return pts


def _circle_extents(content: str) -> list:
    pts = []
    for attrs in _tag_attr_strings(content, "circle"):
        cx, cy, r = _attr_num(attrs, "cx"), _attr_num(attrs, "cy"), _attr_num(attrs, "r")
        if cx is not None and cy is not None:
            rr = r or 0
            pts += [(cx - rr, cy - rr), (cx + rr, cy + rr)]
    return pts


def _foreground_rects(content: str) -> list:
    """Every non-background rect (rounded OR square) — cards, chart bars, table
    cells, diagram nodes. The near-full-canvas background rect is excluded."""
    out = []
    for attrs in _tag_attr_strings(content, "rect"):
        x, y = _attr_num(attrs, "x"), _attr_num(attrs, "y")
        w, h = _attr_num(attrs, "width"), _attr_num(attrs, "height")
        if None in (x, y, w, h):
            continue
        box = (x, y, w, h)
        if not _is_background(box):
            out.append(box)
    return out


def _rounded_rects(content: str) -> list:
    out = []
    for attrs in _tag_attr_strings(content, "rect"):
        x, y = _attr_num(attrs, "x"), _attr_num(attrs, "y")
        w, h = _attr_num(attrs, "width"), _attr_num(attrs, "height")
        if None in (x, y, w, h):
            continue
        rx = _attr_num(attrs, "rx")
        if rx and rx > 2 and not _is_background((x, y, w, h)):
            out.append((x, y, w, h))
    return out


def _path_points(content: str) -> list:
    """Coordinate pairs from every `<path d=...>` — a rough point cloud for a
    bounding box. Donut/pie/area/funnel/sankey charts are `<path>`-drawn."""
    pts = []
    for attrs in _tag_attr_strings(content, "path"):
        m = re.search(r'\bd\s*=\s*"([^"]+)"', attrs)
        if not m:
            continue
        nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", m.group(1))]
        pts += list(zip(nums[0::2], nums[1::2]))
    return pts


def _has_arc_path(content: str) -> bool:
    """A `<path>` carrying an elliptical-arc command — pie / donut / gauge segment."""
    for attrs in _tag_attr_strings(content, "path"):
        m = re.search(r'\bd\s*=\s*"([^"]+)"', attrs)
        if m and re.search(r"[Aa]\s", m.group(1)):
            return True
    return False


def _looks_like_bar_chart(content: str) -> bool:
    """≥3 foreground rects sharing a left edge with varying widths (horizontal bars)
    or a baseline with varying heights (vertical bars). Distinguishes a bar chart
    — whose rects often have rounded corners — from a uniform card grid."""
    from collections import Counter
    rects = _foreground_rects(content)
    if len(rects) < 3:
        return False
    lefts = Counter(round(r[0]) for r in rects)
    edge, n = lefts.most_common(1)[0]
    if n >= 3 and len({round(r[2]) for r in rects if round(r[0]) == edge}) >= 3:
        return True
    bases = Counter(round(r[1] + r[3]) for r in rects)
    base, n = bases.most_common(1)[0]
    if n >= 3 and len({round(r[3]) for r in rects if round(r[1] + r[3]) == base}) >= 3:
        return True
    return False


def _wide_hline_count(content: str) -> int:
    """Near-horizontal `<line>` spanning ≥ half the canvas width — table row rules."""
    n = 0
    for attrs in _tag_attr_strings(content, "line"):
        x1, y1 = _attr_num(attrs, "x1"), _attr_num(attrs, "y1")
        x2, y2 = _attr_num(attrs, "x2"), _attr_num(attrs, "y2")
        if None in (x1, y1, x2, y2):
            continue
        if abs(y1 - y2) < 2 and abs(x2 - x1) >= 600:
            n += 1
    return n


def visual_primary_fraction(content: str) -> float:
    """Graphic coverage — union-bbox area of every non-text, non-background visual
    primitive ÷ content area, clamped to ≤1.0.

    Counts images, polyline/path/circle drawing envelopes, and all foreground
    rects (cards, bars, cells, nodes). Used only to flag genuinely *text-led*
    slides (see `_check_visual_primary`); a near-zero score means "almost no
    graphics on the slide." Rough warn signal, not an exact occupancy.
    """
    content_area = CONTENT_AREA[2] * CONTENT_AREA[3]
    candidates = list(parse_boxes(content, "image"))
    for pts in (_polyline_points(content), _circle_extents(content), _path_points(content)):
        bb = _bbox_of_points(pts)
        if bb:
            candidates.append(bb)
    rects = _foreground_rects(content)
    if rects:
        corners = [(b[0], b[1]) for b in rects] + [(b[0] + b[2], b[1] + b[3]) for b in rects]
        candidates.append(_bbox_of_points(corners))
    if not candidates:
        return 0.0
    return min(1.0, max(_area(c) for c in candidates) / content_area)


def dominant_primitive(content: str) -> str:
    """Classify a slide's realized dominant primitive: image / chart / table /
    cards / text. A coarse, deterministic proxy for `lead_type`, feeding the
    deck-diversity signal.

    Order matters: chart before table (charts also draw gridlines), table before
    cards (a comparison table is rounded column cards + horizontal rules).
    """
    content_area = CONTENT_AREA[2] * CONTENT_AREA[3]
    if any(_area(b) >= 0.25 * content_area for b in parse_boxes(content, "image")):
        return "image"
    if (_polyline_points(content) or _has_arc_path(content)
            or len(_tag_attr_strings(content, "circle")) >= 6
            or _looks_like_bar_chart(content)):
        return "chart"
    if _wide_hline_count(content) >= 3:
        return "table"
    if len(_rounded_rects(content)) >= 2:
        return "cards"
    return "text"


_FONT_SIZE_RE = re.compile(r'font-size\s*[:=]\s*["\']?(\d+\.?\d*)')


def _max_font_size(content: str) -> float:
    sizes = [float(s) for s in _FONT_SIZE_RE.findall(content)]
    return max(sizes) if sizes else 0.0


def low_primitive_diversity(primitives: list, min_slides: int = 4,
                            threshold: float = 0.6):
    """Deck-level realized-primitive diversity (lead_type-diversity proxy).

    Returns a warning string when one dominant primitive owns > `threshold` of the
    body slides; None when varied or when the deck is too small to judge.
    """
    if len(primitives) < min_slides:
        return None
    from collections import Counter
    top, n = Counter(primitives).most_common(1)[0]
    share = n / len(primitives)
    if share > threshold:
        return (f"{int(round(share * 100))}% of body slides are '{top}'-led — low "
                f"primitive diversity; vary the lead_type / dominant primitive "
                f"(executor §0.1 Dominant Primitive Cap)")
    return None


class SVGQualityChecker:
    """SVG quality checker"""

    def __init__(self, strict_theme: bool = False):
        self.strict_theme = strict_theme
        self.results = []
        self.summary = {
            'total': 0,
            'passed': 0,
            'warnings': 0,
            'errors': 0
        }
        self.issue_types = defaultdict(int)
        self._allowlist_cache: Dict[str, set] = {}

    def _color_allowlist(self, svg_path: Path) -> set:
        """Project allowlist for `svg_path` — checked in the SVG's directory and
        its parent (svg_output/<file>.svg ⇒ the project root holds the file)."""
        merged = set()
        for d in (svg_path.parent, svg_path.parent.parent):
            key = str(d)
            if key not in self._allowlist_cache:
                self._allowlist_cache[key] = load_color_allowlist(d)
            merged |= self._allowlist_cache[key]
        return merged

    def check_file(self, svg_file: str, expected_format: str = None) -> Dict:
        """
        Check a single SVG file

        Args:
            svg_file: SVG file path
            expected_format: Expected canvas format (e.g., 'ppt169')

        Returns:
            Check result dictionary
        """
        svg_path = Path(svg_file)

        if not svg_path.exists():
            return {
                'file': str(svg_file),
                'exists': False,
                'errors': ['File does not exist'],
                'warnings': [],
                'passed': False
            }

        result = {
            'file': svg_path.name,
            'path': str(svg_path),
            'exists': True,
            'errors': [],
            'warnings': [],
            'info': {},
            'passed': True
        }

        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 1. Check viewBox
            self._check_viewbox(content, result, expected_format)

            # 2. Check forbidden elements
            self._check_forbidden_elements(content, result)

            # 3. Check fonts
            self._check_fonts(content, result)

            # 4. Check width/height consistency with viewBox
            self._check_dimensions(content, result)

            # 5. Check text wrapping methods
            self._check_text_elements(content, result)

            # 6. Check image references (file existence and resolution)
            self._check_image_references(content, svg_path, result)

            # 7-10. Composition signals — advisory warnings by default. The
            # off-theme hex audit is promoted to an error under --strict-theme
            # (deck gate); photo overlay, quiet zone, visual-primary stay WARN.
            self._check_off_theme_hex(content, result, svg_path)
            self._check_photo_overlay(content, result)
            self._check_quiet_zone(content, result)
            self._check_visual_primary(content, result)
            self._check_text_overlap(content, result)
            self._check_safe_area(content, result)

            # Determine pass/fail (these signals are warnings, never block)
            result['passed'] = len(result['errors']) == 0

        except Exception as e:
            result['errors'].append(f"Failed to read file: {e}")
            result['passed'] = False

        # Update statistics
        self.summary['total'] += 1
        if result['passed']:
            if result['warnings']:
                self.summary['warnings'] += 1
            else:
                self.summary['passed'] += 1
        else:
            self.summary['errors'] += 1

        # Categorize issue types
        for error in result['errors']:
            self.issue_types[self._categorize_issue(error)] += 1

        self.results.append(result)
        return result

    def _check_viewbox(self, content: str, result: Dict, expected_format: str = None):
        """Check viewBox attribute"""
        viewbox_match = re.search(r'viewBox="([^"]+)"', content)

        if not viewbox_match:
            result['errors'].append("Missing viewBox attribute")
            return

        viewbox = viewbox_match.group(1)
        result['info']['viewbox'] = viewbox

        # Check format
        if not re.match(r'0 0 \d+ \d+', viewbox):
            result['warnings'].append(f"Unusual viewBox format: {viewbox}")

        # Check if it matches expected format
        if expected_format and expected_format in CANVAS_FORMATS:
            expected_viewbox = CANVAS_FORMATS[expected_format]['viewbox']
            if viewbox != expected_viewbox:
                result['errors'].append(
                    f"viewBox mismatch: expected '{expected_viewbox}', got '{viewbox}'"
                )

    def _check_forbidden_elements(self, content: str, result: Dict):
        """Check forbidden elements (blocklist)"""
        content_lower = content.lower()

        # ============================================================
        # Forbidden elements blocklist - PPT incompatible
        # ============================================================

        # Clipping / masking
        # clipPath is ONLY allowed on <image> elements (converter maps to DrawingML
        # picture geometry).  On shapes it is pointless (just draw the target shape)
        # and breaks the SVG PPTX rendering.
        if '<clippath' in content_lower:
            # clip-path on non-image elements → error
            clip_on_non_image = re.search(
                r'<(?!image\b)\w+[^>]*\bclip-path\s*=', content, re.IGNORECASE)
            if clip_on_non_image:
                result['errors'].append(
                    "clip-path is only allowed on <image> elements — "
                    "for shapes, draw the target shape directly instead of clipping")
            # Check that every clip-path reference has a matching <clipPath> def
            clip_refs = re.findall(r'clip-path\s*=\s*["\']url\(#([^)]+)\)', content)
            for ref_id in clip_refs:
                if f'id="{ref_id}"' not in content and f"id='{ref_id}'" not in content:
                    result['errors'].append(
                        f"clip-path references #{ref_id} but no matching "
                        f"<clipPath id=\"{ref_id}\"> definition found")
        if '<mask' in content_lower:
            result['errors'].append("Detected forbidden <mask> element (PPT does not support SVG masks)")

        # Style system
        if '<style' in content_lower:
            result['errors'].append("Detected forbidden <style> element (use inline attributes instead)")
        if re.search(r'\bclass\s*=', content):
            result['errors'].append("Detected forbidden class attribute (use inline styles instead)")
        # id attribute: only report error when <style> also exists (id is harmful only with CSS selectors)
        # id inside <defs> for linearGradient/filter etc. is required, Inkscape also auto-adds id to elements,
        # standalone id attributes have no impact on PPT export
        if '<style' in content_lower and re.search(r'\bid\s*=', content):
            result['errors'].append(
                "Detected id attribute used with <style> (CSS selectors forbidden, use inline styles instead)"
            )
        if re.search(r'<\?xml-stylesheet\b', content_lower):
            result['errors'].append("Detected forbidden xml-stylesheet (external CSS references forbidden)")
        if re.search(r'<link[^>]*rel\s*=\s*["\']stylesheet["\']', content_lower):
            result['errors'].append("Detected forbidden <link rel=\"stylesheet\"> (external CSS references forbidden)")
        if re.search(r'@import\s+', content_lower):
            result['errors'].append("Detected forbidden @import (external CSS references forbidden)")

        # Structure / nesting
        if '<foreignobject' in content_lower:
            result['errors'].append(
                "Detected forbidden <foreignObject> element (use <tspan> for manual line breaks)")
        has_symbol = '<symbol' in content_lower
        has_use = re.search(r'<use\b', content_lower) is not None
        if has_symbol and has_use:
            result['errors'].append("Detected forbidden <symbol> + <use> complex usage (use basic shapes or simple <use> instead)")
        # marker-start / marker-end are conditionally allowed (see shared-standards.md §1.1).
        # The converter maps qualifying <marker> defs to native DrawingML <a:headEnd>/<a:tailEnd>.
        # We only warn when a marker is used without an obvious <defs> definition in the same file.
        if re.search(r'\bmarker-(?:start|end)\s*=\s*["\']url\(#([^)]+)\)', content_lower):
            if '<marker' not in content_lower:
                result['errors'].append(
                    "Detected marker-start/marker-end referencing a marker id, "
                    "but no <marker> element found in the file")

        # Text / fonts
        if '<textpath' in content_lower:
            result['errors'].append("Detected forbidden <textPath> element (path text is incompatible with PPT)")
        if '@font-face' in content_lower:
            result['errors'].append("Detected forbidden @font-face (use system font stack)")

        # Animation / interaction
        if re.search(r'<animate', content_lower):
            result['errors'].append("Detected forbidden SMIL animation element <animate*> (SVG animations are not exported)")
        if re.search(r'<set\b', content_lower):
            result['errors'].append("Detected forbidden SMIL animation element <set> (SVG animations are not exported)")
        if '<script' in content_lower:
            result['errors'].append("Detected forbidden <script> element (scripts and event handlers forbidden)")
        if re.search(r'\bon\w+\s*=', content):  # onclick, onload etc.
            result['errors'].append("Detected forbidden event attributes (e.g., onclick, onload)")

        # Other discouraged elements
        if '<iframe' in content_lower:
            result['errors'].append("Detected <iframe> element (should not appear in SVG)")
        if re.search(r'rgba\s*\(', content_lower):
            result['errors'].append("Detected forbidden rgba() color (use fill-opacity/stroke-opacity instead)")
        if re.search(r'<g[^>]*\sopacity\s*=', content_lower):
            result['errors'].append("Detected forbidden <g opacity> (set opacity on each child element individually)")
        if re.search(r'<image[^>]*\sopacity\s*=', content_lower):
            result['errors'].append("Detected forbidden <image opacity> (use overlay mask approach)")

    def _check_fonts(self, content: str, result: Dict):
        """Check font usage"""
        # Find font-family values in both SVG attribute (`font-family="…"`) and
        # CSS (`font-family: "…"`) forms. Capture stops at the first inner quote,
        # which is enough to read the primary (leading) family.
        font_matches = re.findall(
            r'font-family\s*[:=]\s*["\']([^"\']+)', content, re.IGNORECASE)

        if font_matches:
            result['info']['fonts'] = list(set(font_matches))

            # Validate against the ACTIVE theme font chain, not a fixed system-UI
            # allow-list. None ⇒ theme unreadable ⇒ skip (no false warning).
            primary = _active_primary_font()
            if primary:
                for font_family in font_matches:
                    if primary.lower() not in font_family.lower():
                        result['warnings'].append(
                            f"font-family does not lead with the active theme font "
                            f"'{primary}': {font_family}"
                        )
                        break  # Only warn once

    def _check_dimensions(self, content: str, result: Dict):
        """Check width/height consistency with viewBox"""
        width_match = re.search(r'width="(\d+)"', content)
        height_match = re.search(r'height="(\d+)"', content)

        if width_match and height_match:
            width = width_match.group(1)
            height = height_match.group(1)
            result['info']['dimensions'] = f"{width}x{height}"

            # Check consistency with viewBox
            if 'viewbox' in result['info']:
                viewbox_parts = result['info']['viewbox'].split()
                if len(viewbox_parts) == 4:
                    vb_width, vb_height = viewbox_parts[2], viewbox_parts[3]
                    if width != vb_width or height != vb_height:
                        result['warnings'].append(
                            f"width/height ({width}x{height}) does not match viewBox "
                            f"({vb_width}x{vb_height})"
                        )

    def _check_text_elements(self, content: str, result: Dict):
        """Check text elements and wrapping methods"""
        # Count text and tspan elements
        text_count = content.count('<text')
        tspan_count = content.count('<tspan')

        result['info']['text_elements'] = text_count
        result['info']['tspan_elements'] = tspan_count

        # Check for overly long single-line text (may need wrapping)
        text_matches = re.findall(r'<text[^>]*>([^<]{100,})</text>', content)
        if text_matches:
            result['warnings'].append(
                f"Detected {len(text_matches)} potentially overly long single-line text(s) (consider using tspan for wrapping)"
            )

    def _check_image_references(self, content: str, svg_path: Path, result: Dict):
        """Check image file existence and resolution vs display size."""
        # Find all <image ...> elements (capture the full tag)
        img_tag_pattern = re.compile(r'<image\b([^>]*)/?>', re.IGNORECASE)

        svg_dir = svg_path.parent
        checked = set()

        for tag_match in img_tag_pattern.finditer(content):
            attrs = tag_match.group(1)

            # Extract href (prefer href over xlink:href)
            href_match = (
                re.search(r'\bhref="(?!data:)([^"]+)"', attrs) or
                re.search(r'\bxlink:href="(?!data:)([^"]+)"', attrs)
            )
            if not href_match:
                continue

            href = href_match.group(1)
            if href in checked:
                continue
            checked.add(href)

            # Resolve path relative to SVG file directory
            img_path = (svg_dir / href).resolve()

            if not img_path.exists():
                result['errors'].append(
                    f"Image file not found: {href} (resolved to {img_path})")
                continue

            # Check resolution vs display size
            w_match = re.search(r'\bwidth="([^"]+)"', attrs)
            h_match = re.search(r'\bheight="([^"]+)"', attrs)
            display_w_str = w_match.group(1) if w_match else None
            display_h_str = h_match.group(1) if h_match else None
            if not display_w_str or not display_h_str:
                continue

            try:
                display_w = float(display_w_str)
                display_h = float(display_h_str)
            except (ValueError, TypeError):
                continue

            try:
                from PIL import Image as PILImage
                with PILImage.open(img_path) as img:
                    actual_w, actual_h = img.size

                if actual_w < display_w or actual_h < display_h:
                    result['warnings'].append(
                        f"Image {href} is {actual_w}x{actual_h} but displayed at "
                        f"{int(display_w)}x{int(display_h)} — may appear blurry")
                elif actual_w > display_w * 4 and actual_h > display_h * 4:
                    result['warnings'].append(
                        f"Image {href} is {actual_w}x{actual_h} but displayed at "
                        f"{int(display_w)}x{int(display_h)} — consider downsizing "
                        f"to reduce file size")
            except ImportError:
                pass  # PIL not available, skip resolution check
            except Exception:
                pass  # Image unreadable, skip resolution check

    def _check_off_theme_hex(self, content: str, result: Dict, svg_path: Path = None):
        """Hex colors outside the active theme palette (hardcode audit).

        WARN by default; promoted to an error under --strict-theme so
        verify_deck can gate decks on palette compliance. A per-project
        `.theme-color-allow` file whitelists legitimate exceptions.
        """
        allowed = _active_theme_hexes()
        if not allowed:
            return  # theme unreadable — skip rather than flag everything
        if svg_path is not None:
            allowed = allowed | self._color_allowlist(svg_path)
        off = off_theme_hexes(content, allowed)
        if off:
            shown = ", ".join(sorted(off)[:5])
            more = "" if len(off) <= 5 else f" (+{len(off) - 5} more)"
            msg = (f"Off-theme hex (not in active palette): {shown}{more} "
                   f"— use theme tokens / single accent")
            if self.strict_theme:
                result['errors'].append(
                    msg + f" (or whitelist in <project>/{COLOR_ALLOW_FILENAME})")
            else:
                result['warnings'].append(msg)

    def _check_photo_overlay(self, content: str, result: Dict):
        """WARN: text overlaid on a photo (anti-slop Rule 23)."""
        n = texts_over_images(content)
        if n:
            result['warnings'].append(
                f"{n} text element(s) overlaid on an <image> — photos must stand "
                f"alone, caption outside the image (anti-slop Rule 23)")

    def _check_quiet_zone(self, content: str, result: Dict):
        """WARN: content intruding the top-right quiet zone (anti-slop Rule 22)."""
        n = quiet_zone_hits(content)
        if n:
            result['warnings'].append(
                f"{n} element(s) in the top-right quiet zone — keep the corner "
                f"clear for breathing room (anti-slop Rule 22)")

    def _check_text_overlap(self, content: str, result: Dict):
        """WARN: estimated text boxes overlapping past the share threshold —
        the same measurement the PPTX exporter uses, so a hit here means the
        exported deck will very likely show colliding text."""
        hits = text_box_overlaps(content)
        if hits:
            a, b, share = hits[0]
            more = "" if len(hits) == 1 else f" (+{len(hits) - 1} more pair(s))"
            result['warnings'].append(
                f'Text boxes overlap ~{share}%: "{a}" × "{b}"{more} '
                f"— increase spacing or shorten the longer run")

    def _check_safe_area(self, content: str, result: Dict):
        """WARN: foreground content escaping the slide safe area
        (x 56–1224 / y 40–680; GM line and bleed bands exempt)."""
        hits = safe_area_violations(content)
        if hits:
            shown = "; ".join(hits[:3])
            more = "" if len(hits) <= 3 else f" (+{len(hits) - 3} more)"
            result['warnings'].append(
                f"Safe-area violation ({len(hits)}): {shown}{more} "
                f"— keep content within x 56–1224, y 40–680")

    def _check_visual_primary(self, content: str, result: Dict):
        """WARN: a *text-led* body slide with no dominant evidence visual
        (anti-slop Rule 21 — one message + a visual carrying ≥ ~55%; Rule 19 — no
        card-only). Slides that already realize a chart / diagram / image / table /
        card primitive are not flagged. Cover / chapter / closing / hero slides
        (display & display-sm type ≥ 40px) are exempt.
        """
        if _max_font_size(content) >= 40:
            return
        # Body slide: record its realized primitive for the deck-diversity pass.
        prim = dominant_primitive(content)
        result['info']['primitive'] = prim
        if prim != "text":
            return  # already carried by a chart/diagram/image/table/card visual
        frac = visual_primary_fraction(content)
        result['info']['visual_primary'] = round(frac, 2)
        if frac < 0.55:
            result['warnings'].append(
                f"Text-led body slide, weak visual support ({int(frac * 100)}% "
                f"graphic coverage) — carry the message with a dominant evidence "
                f"visual (chart/diagram/image/table), not text alone "
                f"(anti-slop Rule 21 / Rule 19)")

    def _categorize_issue(self, error_msg: str) -> str:
        """Categorize issue type"""
        if 'viewBox' in error_msg:
            return 'viewBox issues'
        elif 'foreignObject' in error_msg:
            return 'foreignObject'
        elif 'font' in error_msg.lower():
            return 'Font issues'
        else:
            return 'Other'

    def check_directory(self, directory: str, expected_format: str = None) -> List[Dict]:
        """
        Check all SVG files in a directory

        Args:
            directory: Directory path
            expected_format: Expected canvas format

        Returns:
            List of check results
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            print(f"[ERROR] Directory does not exist: {directory}")
            return []

        # Find all SVG files
        if dir_path.is_file():
            svg_files = [dir_path]
        else:
            svg_output = dir_path / \
                'svg_output' if (
                    dir_path / 'svg_output').exists() else dir_path
            svg_files = sorted(svg_output.glob('*.svg'))

        if not svg_files:
            print(f"[WARN] No SVG files found")
            return []

        print(f"\n[SCAN] Checking {len(svg_files)} SVG file(s)...\n")

        for svg_file in svg_files:
            result = self.check_file(str(svg_file), expected_format)
            self._print_result(result)

        # Deck-level realized-primitive diversity (lead_type-diversity proxy).
        primitives = [r['info']['primitive'] for r in self.results
                      if 'primitive' in r.get('info', {})]
        deck_warn = low_primitive_diversity(primitives)
        if deck_warn:
            print(f"[WARN] deck: {deck_warn}\n")

        return self.results

    def _print_result(self, result: Dict):
        """Print check result for a single file"""
        if result['passed']:
            if result['warnings']:
                icon = "[WARN]"
                status = "Passed (with warnings)"
            else:
                icon = "[OK]"
                status = "Passed"
        else:
            icon = "[ERROR]"
            status = "Failed"

        print(f"{icon} {result['file']} - {status}")

        # Display basic info
        if result['info']:
            info_items = []
            if 'viewbox' in result['info']:
                info_items.append(f"viewBox: {result['info']['viewbox']}")
            if info_items:
                print(f"   {' | '.join(info_items)}")

        # Display errors
        if result['errors']:
            for error in result['errors']:
                print(f"   [ERROR] {error}")

        # Display warnings
        if result['warnings']:
            for warning in result['warnings'][:2]:  # Only show first 2 warnings
                print(f"   [WARN] {warning}")
            if len(result['warnings']) > 2:
                print(f"   ... and {len(result['warnings']) - 2} more warning(s)")

        print()

    def print_summary(self):
        """Print check summary"""
        print("=" * 80)
        print("[SUMMARY] Check Summary")
        print("=" * 80)

        print(f"\nTotal files: {self.summary['total']}")
        print(
            f"  [OK] Fully passed: {self.summary['passed']} ({self._percentage(self.summary['passed'])}%)")
        print(
            f"  [WARN] With warnings: {self.summary['warnings']} ({self._percentage(self.summary['warnings'])}%)")
        print(
            f"  [ERROR] With errors: {self.summary['errors']} ({self._percentage(self.summary['errors'])}%)")

        if self.issue_types:
            print(f"\nIssue categories:")
            for issue_type, count in sorted(self.issue_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {issue_type}: {count}")

        # Fix suggestions
        if self.summary['errors'] > 0 or self.summary['warnings'] > 0:
            print(f"\n[TIP] Common fixes:")
            print(f"  1. viewBox issues: Ensure consistency with canvas format (see references/canvas-formats.md)")
            print(f"  2. foreignObject: Use <text> + <tspan> for manual line breaks")
            print(f"  3. Font issues: Lead every font-family with the active theme font (references/theme-active.json)")

    def _percentage(self, count: int) -> int:
        """Calculate percentage"""
        if self.summary['total'] == 0:
            return 0
        return int(count / self.summary['total'] * 100)

    def export_report(self, output_file: str = 'svg_quality_report.txt'):
        """Export check report"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("PPT Master SVG Quality Check Report\n")
            f.write("=" * 80 + "\n\n")

            for result in self.results:
                status = "[OK] Passed" if result['passed'] else "[ERROR] Failed"
                f.write(f"{status} - {result['file']}\n")
                f.write(f"Path: {result.get('path', 'N/A')}\n")

                if result['info']:
                    f.write(f"Info: {result['info']}\n")

                if result['errors']:
                    f.write(f"\nErrors:\n")
                    for error in result['errors']:
                        f.write(f"  - {error}\n")

                if result['warnings']:
                    f.write(f"\nWarnings:\n")
                    for warning in result['warnings']:
                        f.write(f"  - {warning}\n")

                f.write("\n" + "-" * 80 + "\n\n")

            # Write summary
            f.write("\n" + "=" * 80 + "\n")
            f.write("Check Summary\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total files: {self.summary['total']}\n")
            f.write(f"Fully passed: {self.summary['passed']}\n")
            f.write(f"With warnings: {self.summary['warnings']}\n")
            f.write(f"With errors: {self.summary['errors']}\n")

        print(f"\n[REPORT] Check report exported: {output_file}")


def main() -> None:
    """Run the CLI entry point."""
    if len(sys.argv) < 2:
        print("PPT Master - SVG Quality Check Tool\n")
        print("Usage:")
        print("  python3 scripts/svg_quality_checker.py <svg_file>")
        print("  python3 scripts/svg_quality_checker.py <directory>")
        print("  python3 scripts/svg_quality_checker.py --all examples")
        print("\nOptions:")
        print("  --strict-theme   promote off-theme hex colors to errors (deck gate);")
        print(f"                   whitelist exceptions in <project>/{COLOR_ALLOW_FILENAME}")
        print("\nExamples:")
        print("  python3 scripts/svg_quality_checker.py examples/project/svg_output/slide_01.svg")
        print("  python3 scripts/svg_quality_checker.py examples/project/svg_output")
        print("  python3 scripts/svg_quality_checker.py examples/project")
        sys.exit(0)

    strict_theme = '--strict-theme' in sys.argv
    if strict_theme:
        sys.argv.remove('--strict-theme')

    checker = SVGQualityChecker(strict_theme=strict_theme)

    # Parse arguments
    target = sys.argv[1]
    expected_format = None

    if '--format' in sys.argv:
        idx = sys.argv.index('--format')
        if idx + 1 < len(sys.argv):
            expected_format = sys.argv[idx + 1]

    # Execute check
    if target == '--all':
        # Check all example projects
        base_dir = sys.argv[2] if len(sys.argv) > 2 else 'examples'
        from project_utils import find_all_projects
        projects = find_all_projects(base_dir)

        for project in projects:
            print(f"\n{'=' * 80}")
            print(f"Checking project: {project.name}")
            print('=' * 80)
            checker.check_directory(str(project))
    else:
        checker.check_directory(target, expected_format)

    # Print summary
    checker.print_summary()

    # Export report (if specified)
    if '--export' in sys.argv:
        output_file = 'svg_quality_report.txt'
        if '--output' in sys.argv:
            idx = sys.argv.index('--output')
            if idx + 1 < len(sys.argv):
                output_file = sys.argv[idx + 1]
        checker.export_report(output_file)

    # Return exit code
    if checker.summary['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
