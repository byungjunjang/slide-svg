"""Connector routes bound to shapes (a:stCxn / a:endCxn).

A ``<line>``, ``<polyline>`` or straight-segment ``<path>`` names the shapes it
joins with ``data-pptx-start`` / ``data-pptx-end`` (SVG ids on the same page);
``data-pptx-start-site`` / ``data-pptx-end-site`` pin a connection site,
otherwise the site nearest the route's end is used. The route exports as a
``p:cxnSp`` — ``straightConnector1``, or ``bentConnector2/3`` for an orthogonal
route with one or two bends — so in PowerPoint the line follows its shapes when
they move. Targets: ``rect`` (rounded → ``roundRect``), ``circle``, ``ellipse``.

A route can come before its shapes in the document, so it leaves a token in
the slide XML; ``resolve_connectors`` fills the tokens in once every shape has
its id. Route geometry and frames follow slide-master's connectors module.
"""

from __future__ import annotations

import math
import re
from xml.etree import ElementTree as ET

from .drawingml_context import ConvertContext, ShapeResult
from .drawingml_styles import build_stroke_xml, get_stroke_opacity
from .drawingml_utils import EMU_PER_PX, _f, ctx_x, ctx_y, px_to_emu

START, END = 'data-pptx-start', 'data-pptx-end'
ROUTE_TAGS = ('line', 'polyline', 'path')
TARGET_TAGS = ('rect', 'circle', 'ellipse')
_TOL = 0.5  # px: points this close are one; drift this small is still straight
_U_TURN_RUN_PX = 4 / 3  # 1 pt, the run PowerPoint writes for a U-shaped elbow
_TOKEN = '<!--pptx-connector-{}-->'
_NUM_RE = re.compile(r'-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
_PATH_TOKEN_RE = re.compile(r'[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
_CNVPR_RE = re.compile(r'<p:cNvPr id="(\d+)"')
_XFRM_RE = re.compile(r'<a:off x="(-?\d+)" y="(-?\d+)"/>\s*<a:ext cx="(\d+)" cy="(\d+)"/>')
_PRST_RE = re.compile(r'<a:prstGeom prst="(\w+)"')


def is_bound_route(elem: ET.Element, tag: str) -> bool:
    return tag in ROUTE_TAGS and bool(elem.get(START) or elem.get(END))


def _route_points(elem: ET.Element, tag: str) -> list[tuple[float, float]]:
    """A route's points in its own SVG user space."""
    if tag == 'line':
        return [(_f(elem.get('x1')), _f(elem.get('y1'))),
                (_f(elem.get('x2')), _f(elem.get('y2')))]
    if tag == 'polyline':
        nums = [float(n) for n in _NUM_RE.findall(elem.get('points', ''))]
        return list(zip(nums[0::2], nums[1::2]))
    points: list[tuple[float, float]] = []
    x = y = 0.0
    cmd = None
    tokens = _PATH_TOKEN_RE.findall(elem.get('d', ''))
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.isalpha():
            if tok not in 'MmLlHhVv':
                raise ValueError('a bound route must be straight segments (M/L/H/V)')
            if tok in 'Mm' and points:
                raise ValueError('a bound route must be one open run')
            cmd, i = tok, i + 1
            continue
        if cmd in ('M', 'm', 'L', 'l'):
            nx, ny = float(tokens[i]), float(tokens[i + 1])
            i += 2
            x, y = (x + nx, y + ny) if cmd.islower() else (nx, ny)
            cmd = {'M': 'L', 'm': 'l'}.get(cmd, cmd)
        elif cmd in ('H', 'h'):
            x = x + float(tokens[i]) if cmd == 'h' else float(tokens[i])
            i += 1
        elif cmd in ('V', 'v'):
            y = y + float(tokens[i]) if cmd == 'v' else float(tokens[i])
            i += 1
        else:
            raise ValueError('a bound route must start with M')
        points.append((x, y))
    return points


def classify_route(points: list[tuple[float, float]]) -> tuple[str, list[tuple[float, float]]]:
    """The connector preset and corner points of a slide-space route: one
    segment is straightConnector1; an orthogonal route with one or two bends
    is bentConnector2 / bentConnector3."""
    corners = [points[0]]
    axes: list[str] = []
    for point in points[1:]:
        last = corners[-1]
        dx, dy = point[0] - last[0], point[1] - last[1]
        if math.hypot(dx, dy) <= _TOL:
            continue
        axis = 'h' if abs(dy) <= _TOL else 'v' if abs(dx) <= _TOL else 'd'
        if axes and axis == axes[-1] != 'd':
            k = 0 if axis == 'h' else 1
            if (point[k] - last[k]) * (last[k] - corners[-2][k]) < 0:
                raise ValueError('the route doubles back on itself')
            corners[-1] = point
            continue
        corners.append(point)
        axes.append(axis)
    if not axes:
        raise ValueError('the route needs two distinct points')
    if len(axes) == 1:
        return 'straightConnector1', corners
    if 'd' in axes:
        raise ValueError('an elbow route may use only horizontal and vertical segments')
    if len(axes) > 3:
        raise ValueError('an elbow route may bend at most twice')
    return ('bentConnector2', 'bentConnector3')[len(axes) - 2], corners


def connector_frame(preset: str, corners: list[tuple[float, float]]):
    """`(x, y, w, h, rot, flipH, flipV, adj1)` in px. The connector box spans
    start to end; a vertical first segment rotates the preset 90 degrees."""
    (sx, sy), (ex, ey) = corners[0], corners[-1]
    vertical_first = preset != 'straightConnector1' and abs(corners[1][0] - sx) <= _TOL
    if preset == 'bentConnector3':
        if vertical_first and abs(ey - sy) <= _TOL:
            ey = sy + math.copysign(_U_TURN_RUN_PX, corners[1][1] - sy)
        elif not vertical_first and abs(ex - sx) <= _TOL:
            ex = sx + math.copysign(_U_TURN_RUN_PX, corners[1][0] - sx)
    if vertical_first:
        rotation, width, height = 5400000, abs(ey - sy), abs(ex - sx)
        flip_h, flip_v = ey < sy, ex > sx
        start, end, bend = sy, ey, corners[1][1]
    else:
        rotation, width, height = 0, abs(ex - sx), abs(ey - sy)
        flip_h, flip_v = ex < sx, ey < sy
        start, end, bend = sx, ex, corners[1][0]
    adj1 = round((bend - start) / (end - start) * 100000) if preset == 'bentConnector3' else None
    cx, cy = (sx + ex) / 2, (sy + ey) / 2
    return cx - width / 2, cy - height / 2, width, height, rotation, flip_h, flip_v, adj1


def _sites(kind: str, x: float, y: float, w: float, h: float) -> list[tuple[float, float]]:
    """Preset connection sites: rect / roundRect 0 top, 1 left, 2 bottom,
    3 right; ellipse 0 top, then counter-clockwise in 45° steps."""
    cx, cy = x + w / 2, y + h / 2
    if kind == 'ellipse':
        dx, dy = w / 2 * math.cos(math.pi / 4), h / 2 * math.sin(math.pi / 4)
        return [(cx, y), (cx - dx, cy - dy), (x, cy), (cx - dx, cy + dy),
                (cx, y + h), (cx + dx, cy + dy), (x + w, cy), (cx + dx, cy - dy)]
    return [(cx, y), (x, cy), (cx, y + h), (x + w, cy)]


def record_target(svg_id: str, shape_xml: str, ctx: ConvertContext) -> None:
    """Remember a converted shape's id, preset and box for the routes."""
    sid, frame, prst = _CNVPR_RE.search(shape_xml), _XFRM_RE.search(shape_xml), _PRST_RE.search(shape_xml)
    if sid and frame and prst and prst.group(1) in ('rect', 'roundRect', 'ellipse'):
        box = tuple(int(v) / EMU_PER_PX for v in frame.groups())
        ctx.targets[svg_id] = (sid.group(1), 'ellipse' if prst.group(1) == 'ellipse' else 'rect', box)


def defer_connector(elem: ET.Element, tag: str, ctx: ConvertContext) -> ShapeResult:
    """Convert a bound route up to its ends; the ends are bound in
    resolve_connectors. Raises ValueError for a route a connector cannot draw."""
    points = [(ctx_x(px, ctx), ctx_y(py, ctx)) for px, py in _route_points(elem, tag)]
    preset, corners = classify_route(points)
    shape_id = ctx.next_id()
    token = _TOKEN.format(shape_id)
    ctx.connectors[token] = {
        'id': shape_id, 'preset': preset, 'frame': connector_frame(preset, corners),
        'stroke': build_stroke_xml(elem, ctx, get_stroke_opacity(elem, ctx)),
        'ends': [('stCxn', elem.get(START), elem.get(f'{START}-site'), corners[0]),
                 ('endCxn', elem.get(END), elem.get(f'{END}-site'), corners[-1])],
    }
    xs, ys = [p[0] for p in corners], [p[1] for p in corners]
    return ShapeResult(xml=token, bounds_emu=(px_to_emu(min(xs)), px_to_emu(min(ys)),
                                              px_to_emu(max(xs)), px_to_emu(max(ys))))


def resolve_connectors(slide_xml: str, ctx: ConvertContext) -> str:
    """Replace each route token with its p:cxnSp, binding the ends whose
    target shape exists on the page."""
    for token, c in ctx.connectors.items():
        refs = ''
        for tag, target, site, point in c['ends']:
            hit = ctx.targets.get(target) if target else None
            if hit is None:
                continue
            target_id, kind, box = hit
            sites = _sites(kind, *box)
            if site is not None and site.isdigit() and int(site) < len(sites):
                idx = int(site)
            else:
                idx = min(range(len(sites)), key=lambda i: math.dist(sites[i], point))
            refs += f'<a:{tag} id="{target_id}" idx="{idx}"/>'
        x, y, w, h, rot, flip_h, flip_v, adj = c['frame']
        attrs = ((f' rot="{rot}"' if rot else '') + (' flipH="1"' if flip_h else '')
                 + (' flipV="1"' if flip_v else ''))
        av = f'<a:gd name="adj1" fmla="val {adj}"/>' if adj is not None else ''
        sid = c['id']
        slide_xml = slide_xml.replace(token, (
            f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{sid}" name="Connector {sid}"/>'
            f'<p:cNvCxnSpPr>{refs}</p:cNvCxnSpPr><p:nvPr/></p:nvCxnSpPr>'
            f'<p:spPr><a:xfrm{attrs}><a:off x="{px_to_emu(x)}" y="{px_to_emu(y)}"/>'
            f'<a:ext cx="{max(px_to_emu(w), 1)}" cy="{max(px_to_emu(h), 1)}"/></a:xfrm>'
            f'<a:prstGeom prst="{c["preset"]}"><a:avLst>{av}</a:avLst></a:prstGeom>'
            f'{c["stroke"]}</p:spPr></p:cxnSp>'))
    return slide_xml
