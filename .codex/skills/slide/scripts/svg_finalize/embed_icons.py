#!/usr/bin/env python3
"""
SVG Icon Embedding Tool

Replaces icon placeholders in SVG files with actual icon code.

Placeholder syntax:
    <use data-icon="tabler-outline/home" x="100" y="200" width="48" height="48" fill="#0076A8"/>
    <use data-icon="tabler-filled/home" x="100" y="200" width="48" height="48" fill="#0076A8"/>

After replacement:
    <g transform="translate(100, 200) scale(3)" fill="#0076A8">
      <path d="..."/>
    </g>

Icon resolution (in priority order):
    1. ${REPO_ROOT}/assets/icons/<lib>/<name>.svg  — full library, used in Claude Code
    2. ${SKILL_DIR}/templates/icons/<lib>/<name>.svg  — bundled essentials, used in claude.ai mode
    3. None → caller emits `[WARN] Icon not found` and skips the placeholder.

Libraries:
    tabler-outline (default) — 5000+ stroke icons, 24x24 viewBox. Prefix: `tabler-outline/<name>`
    tabler-filled  (fallback) — 1000+ fill icons,  24x24 viewBox. Prefix: `tabler-filled/<name>`

Notes:
    - Library prefix is REQUIRED. Un-prefixed icon names are not resolved.
    - The legacy `chunk/` library is no longer shipped.

Usage:
    python3 scripts/svg_finalize/embed_icons.py <svg_file> [svg_file2] ...
    python3 scripts/svg_finalize/embed_icons.py svg_output/*.svg

Options:
    --icons-dir <path>    Override search roots with a single directory containing
                          `<lib>/<name>.svg`. When omitted, the default chain above is used.
    --dry-run             Only show what would be replaced, without modifying files
    --verbose             Show detailed information
"""

import re
import sys
import argparse
from pathlib import Path


# Search roots for icon SVGs, in priority order.
# 1) Repo-root assets/ (full library, kept outside the skill folder so the skill
#    bundle can be uploaded to claude.ai without violating the nested-zip rule).
# 2) Skill-local templates/icons/ (a small flat-SVG essentials subset bundled
#    inside the skill so claude.ai uploads still render the most common icons).
# Path layout: <repo>/.codex/skills/slide/scripts/svg_finalize/embed_icons.py
#   parents[0] = .../scripts/svg_finalize
#   parents[2] = .../slide          (skill root)
#   parents[5] = repo root
_SKILL_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_ICON_ROOTS: tuple[Path, ...] = (
    _REPO_ROOT / 'assets' / 'icons',
    _SKILL_ROOT / 'templates' / 'icons',
)

# Back-compat alias — some external callers may still import DEFAULT_ICONS_DIR.
DEFAULT_ICONS_DIR = DEFAULT_ICON_ROOTS[0]

# Icon base size per library
ICON_BASE_SIZES = {
    'tabler-filled': 24,
    'tabler-outline': 24,
}
DEFAULT_ICON_BASE_SIZE = 24


def _read_icon_svg(icon_name: str, override_dir: Path | None = None) -> str | None:
    """Read an icon SVG's raw text by its `lib/name` identifier.

    Tries the default search roots in priority order, or `override_dir` alone
    if provided. Returns None when the prefix is missing or the icon is not
    found in any root.
    """
    if '/' not in icon_name:
        # Un-prefixed names are not supported. The legacy `chunk/` library is
        # no longer shipped; callers must specify `tabler-outline/<name>` or
        # `tabler-filled/<name>`.
        return None
    lib, name = icon_name.split('/', 1)
    roots: tuple[Path, ...] = (override_dir,) if override_dir is not None else DEFAULT_ICON_ROOTS
    for root in roots:
        candidate = root / lib / f'{name}.svg'
        if candidate.exists():
            return candidate.read_text(encoding='utf-8')
    return None


def _get_viewbox_size(content: str) -> float:
    """Extract the width from viewBox attribute (assumed square). Returns 0 if not found."""
    m = re.search(r'viewBox=["\']0 0 ([\d.]+)', content)
    if m:
        return float(m.group(1))
    return 0


def _detect_icon_style(content: str) -> str:
    """Detect whether an icon is fill-based or stroke-based."""
    # stroke="currentColor" with fill="none" → stroke style
    if 'stroke="currentColor"' in content and 'fill="none"' in content:
        return 'stroke'
    return 'fill'


def _extract_shape_elements(content: str, color: str) -> list[str]:
    """
    Extract all drawable shape elements from an icon SVG, replacing
    fill/stroke color references (currentColor or #xxxxxx) with the target color.

    Supports: <path>, <circle>, <rect>, <line>, <polyline>, <polygon>, <ellipse>
    """
    shape_tags = ('path', 'circle', 'rect', 'line', 'polyline', 'polygon', 'ellipse')
    pattern = r'<(' + '|'.join(shape_tags) + r')(\s[^>]*)?(?:/>|></\1>)'
    matches = re.findall(pattern, content, re.DOTALL)

    elements = []
    for tag, attrs in matches:
        # Remove standalone fill/stroke color attrs so outer <g> controls color
        attrs_clean = re.sub(r'\s*fill="(?:currentColor|#[0-9a-fA-F]{3,6}|none)"', '', attrs)
        attrs_clean = re.sub(r'\s*stroke="(?:currentColor|#[0-9a-fA-F]{3,6}|none)"', '', attrs_clean)
        elements.append(f'<{tag}{attrs_clean}/>')

    return elements


def extract_paths_from_icon(icon_name: str, icons_dir: Path | None = None, target_color: str = '#000000') -> tuple[list[str], str, float]:
    """Extract drawable elements for `<lib>/<name>` from the resolved icon SVG.

    `icons_dir` overrides the default search chain when provided. Returns
    (elements, style, base_size). Empty `elements` list ⇒ icon not found.
    `style` is 'fill' or 'stroke'; `base_size` is the icon's natural viewBox width.
    """
    content = _read_icon_svg(icon_name, icons_dir)
    if content is None:
        return [], 'fill', ICON_BASE_SIZES.get(icon_name.split('/', 1)[0] if '/' in icon_name else '', DEFAULT_ICON_BASE_SIZE)

    style = _detect_icon_style(content)
    base_size = _get_viewbox_size(content) or ICON_BASE_SIZES.get(icon_name.split('/', 1)[0], DEFAULT_ICON_BASE_SIZE)
    elements = _extract_shape_elements(content, target_color)
    return elements, style, base_size


def parse_use_element(use_match: str) -> dict[str, str | float]:
    """
    Parse attributes of a use element.

    Args:
        use_match: Complete string of the use element

    Returns:
        Attribute dictionary
    """
    attrs: dict[str, str | float] = {}

    # Extract data-icon
    icon_match = re.search(r'data-icon="([^"]+)"', use_match)
    if icon_match:
        attrs['icon'] = icon_match.group(1)

    # Extract numeric attributes
    for attr in ['x', 'y', 'width', 'height']:
        match = re.search(rf'{attr}="([^"]+)"', use_match)
        if match:
            attrs[attr] = float(match.group(1))

    # Extract fill color
    fill_match = re.search(r'fill="([^"]+)"', use_match)
    if fill_match:
        attrs['fill'] = fill_match.group(1)

    return attrs


def generate_icon_group(attrs: dict[str, str | float], elements: list[str], style: str, base_size: float) -> str:
    """
    Generate the icon's <g> element.

    Args:
        attrs:     Attributes of the use element
        elements:  List of drawable SVG elements
        style:     'fill' or 'stroke'
        base_size: Icon's natural size (viewBox width)

    Returns:
        Complete <g> element string
    """
    x = attrs.get('x', 0)
    y = attrs.get('y', 0)
    width = attrs.get('width', base_size)
    height = attrs.get('height', base_size)
    color = attrs.get('fill', '#000000')
    icon_name = attrs.get('icon', 'unknown')

    scale_x = width / base_size
    scale_y = height / base_size

    if abs(scale_x - 1) < 1e-6 and abs(scale_y - 1) < 1e-6:
        transform = f'translate({x}, {y})'
    elif abs(scale_x - scale_y) < 1e-6:
        transform = f'translate({x}, {y}) scale({scale_x})'
    else:
        transform = f'translate({x}, {y}) scale({scale_x}, {scale_y})'

    elements_str = '\n    '.join(elements)

    if style == 'stroke':
        color_attrs = f'fill="none" stroke="{color}"'
    else:
        color_attrs = f'fill="{color}"'

    return f'''<!-- icon: {icon_name} -->
  <g transform="{transform}" {color_attrs}>
    {elements_str}
  </g>'''


def process_svg_file(svg_path: Path, icons_dir: Path | None = None, dry_run: bool = False, verbose: bool = False) -> int:
    """
    Process a single SVG file, replacing all icon placeholders.

    Args:
        svg_path: SVG file path
        icons_dir: Optional override directory containing `<lib>/<name>.svg`.
                   When None (default), the chain in DEFAULT_ICON_ROOTS is used.
        dry_run: Whether to only preview without modifying
        verbose: Whether to show detailed information

    Returns:
        Number of icons replaced
    """
    if not svg_path.exists():
        print(f"[ERROR] File not found: {svg_path}")
        return 0

    content = svg_path.read_text(encoding='utf-8')

    # Match <use data-icon="xxx" ... /> elements
    use_pattern = r'<use\s+[^>]*data-icon="[^"]*"[^>]*/>'
    matches = list(re.finditer(use_pattern, content))

    if not matches:
        if verbose:
            print(f"[SKIP] No icon placeholders: {svg_path}")
        return 0

    replaced_count = 0
    new_content = content

    # Replace from back to front to avoid position offset
    for match in reversed(matches):
        use_str = match.group(0)
        attrs = parse_use_element(use_str)

        icon_name = attrs.get('icon')
        if not icon_name:
            continue

        color = str(attrs.get('fill', '#000000'))
        elements, style, base_size = extract_paths_from_icon(str(icon_name), icons_dir, color)

        if not elements:
            print(f"[WARN] Icon not found: {icon_name} (in {svg_path.name})")
            continue

        replacement = generate_icon_group(attrs, elements, style, base_size)

        if verbose or dry_run:
            print(f"  [*] {icon_name}: x={attrs.get('x', 0)}, y={attrs.get('y', 0)}, "
                  f"size={attrs.get('width', base_size)}, fill={color}, style={style}")

        new_content = new_content[:match.start()] + replacement + new_content[match.end():]
        replaced_count += 1

    if not dry_run and replaced_count > 0:
        svg_path.write_text(new_content, encoding='utf-8')

    status = "[PREVIEW]" if dry_run else "[OK]"
    print(f"{status} {svg_path.name} ({replaced_count} icons)")

    return replaced_count


def main() -> None:
    """Run the CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Replace icon placeholders in SVG files with actual icon code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 scripts/svg_finalize/embed_icons.py svg_output/01_cover.svg
  python3 scripts/svg_finalize/embed_icons.py svg_output/*.svg
  python3 scripts/svg_finalize/embed_icons.py --dry-run svg_output/*.svg
  python3 scripts/svg_finalize/embed_icons.py --icons-dir my_icons/ output.svg
        '''
    )

    parser.add_argument('files', nargs='+', help='SVG files to process')
    parser.add_argument('--icons-dir', type=Path, default=None,
                        help='Override the default search chain with a single directory '
                             'containing `<lib>/<name>.svg`. When omitted, both '
                             f'{DEFAULT_ICON_ROOTS[0]} and {DEFAULT_ICON_ROOTS[1]} are tried in order.')
    parser.add_argument('--dry-run', action='store_true',
                        help='Only show what would be replaced, without modifying files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed information')

    args = parser.parse_args()

    # Report the search roots in effect — never abort on missing dirs because
    # the resolution chain falls through gracefully (missing icons just emit
    # a [WARN] and skip).
    if args.icons_dir is not None:
        print(f"[DIR] Icon override directory: {args.icons_dir}")
        if not args.icons_dir.exists():
            print(f"[WARN] Override directory does not exist: {args.icons_dir}")
    else:
        for root in DEFAULT_ICON_ROOTS:
            tag = "OK " if root.exists() else "-- "
            print(f"[DIR] {tag}{root}")
    if args.dry_run:
        print("[PREVIEW] Preview mode (no files will be modified)")
    print()

    total_replaced = 0
    total_files = 0

    for file_pattern in args.files:
        svg_path = Path(file_pattern)
        if svg_path.exists():
            count = process_svg_file(svg_path, args.icons_dir, args.dry_run, args.verbose)
            total_replaced += count
            if count > 0:
                total_files += 1

    print()
    print(f"[Summary] Total: {total_files} file(s), {total_replaced} icon(s)" +
          (" (preview)" if args.dry_run else " replaced"))


if __name__ == '__main__':
    main()
