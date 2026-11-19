"""Drop the white full-slide background <rect> before PPTX export.

A plain white rect over the whole 1280x720 page adds nothing — the slide is
already white — but svg_to_pptx turns it into a full-slide shape that swallows
every click in PowerPoint. Only the background slot is touched: the first
drawing element after <svg> (comments / <title> / <desc> / <defs> may precede
it). A coloured page, a narrative band, or a framed (stroked) page is kept.
"""
from __future__ import annotations

import re

_LEAD_RE = re.compile(
    r"(<svg\b[^>]*>(?:\s|<!--.*?-->|<title\b.*?</title>|<desc\b.*?</desc>|<defs\b.*?</defs>)*?)"
    r"[ \t]*<rect\b([^>]*?)/>[ \t]*\r?\n?",
    re.S,
)
_ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
_WHITE = {"#ffffff", "#fff", "white"}
_DISQUALIFY = {"opacity", "fill-opacity", "transform", "filter", "rx", "ry", "style"}


def strip_white_canvas(svg: str) -> tuple[str, int]:
    """Return (svg, removed_count) — removed_count is 0 or 1."""
    m = _LEAD_RE.search(svg)
    if not m:
        return svg, 0
    a = dict(_ATTR_RE.findall(m.group(2)))
    full_page = (a.get("x", "0") == "0" and a.get("y", "0") == "0"
                 and a.get("width") in ("1280", "100%") and a.get("height") in ("720", "100%"))
    plain_white = (a.get("fill", "").strip().lower() in _WHITE
                   and a.get("stroke", "none") == "none" and not _DISQUALIFY & a.keys())
    if not (full_page and plain_white):
        return svg, 0
    return svg[:m.start()] + m.group(1) + svg[m.end():], 1
