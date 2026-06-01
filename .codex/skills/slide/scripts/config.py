#!/usr/bin/env python3
"""
PPT Master - Unified Configuration Management Module

Centrally manages all project configuration items to ensure consistency and maintainability.

Usage:
    from config import Config, CANVAS_FORMATS

    # Get canvas format
    ppt169 = Config.get_canvas_format('ppt169')
"""

from pathlib import Path
from typing import Dict, Optional
import json


# ============================================================
# Path Configuration
# ============================================================

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Core directories
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'
REFERENCES_DIR = PROJECT_ROOT / 'references'
TEMPLATES_DIR = PROJECT_ROOT / 'templates'
WORKFLOWS_DIR = PROJECT_ROOT / 'workflows'

# Repository root directory
REPO_ROOT = PROJECT_ROOT.parent.parent
EXAMPLES_DIR = REPO_ROOT / 'examples'
PROJECTS_DIR = REPO_ROOT / 'projects'

# Template subdirectories
CHART_TEMPLATES_DIR = TEMPLATES_DIR / 'charts'


# ============================================================
# Canvas Format Configuration
# ============================================================

CANVAS_FORMATS = {
    'ppt169': {
        'name': 'PPT 16:9',
        'dimensions': '1280×720',
        'viewbox': '0 0 1280 720',
        'width': 1280,
        'height': 720,
        'aspect_ratio': '16:9',
        'use_case': 'Modern projectors, online presentations'
    },
    'ppt43': {
        'name': 'PPT 4:3',
        'dimensions': '1024×768',
        'viewbox': '0 0 1024 768',
        'width': 1024,
        'height': 768,
        'aspect_ratio': '4:3',
        'use_case': 'Traditional projectors'
    },
    'wechat': {
        'name': 'WeChat Article Header',
        'dimensions': '900×383',
        'viewbox': '0 0 900 383',
        'width': 900,
        'height': 383,
        'aspect_ratio': '2.35:1',
        'use_case': 'WeChat article cover images'
    },
    'xiaohongshu': {
        'name': '小红书',
        'dimensions': '1242×1660',
        'viewbox': '0 0 1242 1660',
        'width': 1242,
        'height': 1660,
        'aspect_ratio': '3:4',
        'use_case': 'Knowledge sharing, product reviews'
    },
    'moments': {
        'name': 'Moments/Instagram',
        'dimensions': '1080×1080',
        'viewbox': '0 0 1080 1080',
        'width': 1080,
        'height': 1080,
        'aspect_ratio': '1:1',
        'use_case': 'Social media square images'
    },
    'story': {
        'name': 'Story/Vertical',
        'dimensions': '1080×1920',
        'viewbox': '0 0 1080 1920',
        'width': 1080,
        'height': 1920,
        'aspect_ratio': '9:16',
        'use_case': 'Short video covers, stories'
    },
    'banner': {
        'name': 'Horizontal Banner',
        'dimensions': '1920×1080',
        'viewbox': '0 0 1920 1080',
        'width': 1920,
        'height': 1080,
        'aspect_ratio': '16:9',
        'use_case': 'Web banners, large screen displays'
    },
    'a4': {
        'name': 'A4 Print',
        'dimensions': '1240×1754',
        'viewbox': '0 0 1240 1754',
        'width': 1240,
        'height': 1754,
        'aspect_ratio': '√2:1',
        'use_case': 'Print documents, PDF export'
    }
}


# ============================================================
# Font Configuration
# ============================================================

FONTS = {
    'system_ui': "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    'sans_serif': "'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif",
    'monospace': "'SF Mono', Monaco, Consolas, 'Liberation Mono', monospace"
}

FONT_SIZES = {
    'title_large': 48,
    'title': 36,
    'title_small': 28,
    'heading': 24,
    'subheading': 20,
    'body': 18,
    'body_small': 16,
    'caption': 14,
    'footnote': 12
}


# ============================================================
# Layout Configuration
# ============================================================

LAYOUT_MARGINS = {
    'ppt169': {
        'top': 60,
        'right': 60,
        'bottom': 60,
        'left': 60,
        'content_width': 1160,
        'content_height': 600
    },
    'ppt43': {
        'top': 50,
        'right': 50,
        'bottom': 50,
        'left': 50,
        'content_width': 924,
        'content_height': 608
    },
    'xiaohongshu': {
        'top': 80,
        'right': 60,
        'bottom': 80,
        'left': 60,
        'content_width': 1122,
        'content_height': 1500
    },
    'moments': {
        'top': 60,
        'right': 60,
        'bottom': 60,
        'left': 60,
        'content_width': 960,
        'content_height': 960
    },
    'story': {
        'top': 120,
        'right': 60,
        'bottom': 180,
        'left': 60,
        'content_width': 960,
        'content_height': 1620
    },
    'wechat': {
        'top': 40,
        'right': 40,
        'bottom': 40,
        'left': 40,
        'content_width': 820,
        'content_height': 303
    },
}


# ============================================================
# SVG Technical Specifications
# ============================================================

SVG_CONSTRAINTS = {
    # Forbidden elements - PPT incompatible
    'forbidden_elements': [
        # Clipping / Masking
        'clipPath',
        'mask',
        # Style system
        'style',
        # Structure / Nesting
        'foreignObject',
        # Text / Fonts
        'textPath',
        # Animation / Interaction
        'animate',
        'animateMotion',
        'animateTransform',
        'animateColor',
        'set',
        'script',
        # Others
        'iframe',
    ],
    # Forbidden attributes
    # Note: marker-start / marker-end are NOT banned — they are conditionally
    # allowed (see references/shared-standards.md §1.1). The svg_to_pptx
    # converter maps qualifying <marker> defs to native DrawingML
    # <a:headEnd>/<a:tailEnd>.
    'forbidden_attributes': [
        'class',
        'id',
        'onclick', 'onload', 'onmouseover', 'onmouseout',
        'onfocus', 'onblur', 'onchange',
    ],
    # Forbidden patterns (regex matching)
    'forbidden_patterns': [
        r'@font-face',  # Web fonts
        r'rgba\s*\(',   # rgba colors (PPT incompatible)
        r'<\?xml-stylesheet\b',  # External CSS
        r'<link[^>]*rel\s*=\s*["\']stylesheet["\']',
        r'@import\s+',  # External CSS
        r'<g[^>]*\sopacity\s*=',  # Group opacity
        r'<image[^>]*\sopacity\s*=',  # Image opacity
        r'\bon\w+\s*=',  # Event attributes
        r'(?s)(?=.*<symbol)(?=.*<use\b)',  # <symbol> + <use> complex usage (order-independent)
    ],
    'recommended_fonts': [
        'system-ui',
        '-apple-system',
        'BlinkMacSystemFont',
        'Segoe UI'
    ]
}


# ============================================================
# Configuration Manager Class
# ============================================================

class Config:
    """Configuration manager."""

    @staticmethod
    def get_canvas_format(format_key: str) -> Optional[Dict]:
        """
        Get canvas format configuration.

        Args:
            format_key: Format key name (e.g. 'ppt169', 'xiaohongshu')

        Returns:
            Format configuration dict, or None if not found
        """
        return CANVAS_FORMATS.get(format_key)

    @staticmethod
    def get_all_canvas_formats() -> Dict:
        """Get all canvas formats."""
        return CANVAS_FORMATS.copy()

    @staticmethod
    def get_layout_margins(format_key: str) -> Optional[Dict]:
        """
        Get layout margin configuration.

        Args:
            format_key: Format key name

        Returns:
            Margin configuration dict
        """
        return LAYOUT_MARGINS.get(format_key)

    @staticmethod
    def get_font(font_type: str = 'system_ui') -> str:
        """
        Get font declaration.

        Args:
            font_type: Font type ('system_ui', 'sans_serif', 'monospace')

        Returns:
            Font declaration string
        """
        return FONTS.get(font_type, FONTS['system_ui'])

    @staticmethod
    def get_font_size(size_name: str) -> int:
        """
        Get font size.

        Args:
            size_name: Size name (e.g. 'title', 'body', 'caption')

        Returns:
            Font size (pixels)
        """
        return FONT_SIZES.get(size_name, FONT_SIZES['body'])

    @staticmethod
    def validate_svg_element(element_name: str) -> bool:
        """
        Validate whether an SVG element is allowed.

        Args:
            element_name: Element name

        Returns:
            Whether the element is allowed
        """
        return element_name.lower() not in [e.lower() for e in SVG_CONSTRAINTS['forbidden_elements']]

    @staticmethod
    def get_project_path(subdir: str = '') -> Path:
        """
        Get project path.

        Args:
            subdir: Subdirectory name

        Returns:
            Full path
        """
        if subdir:
            return PROJECT_ROOT / subdir
        return PROJECT_ROOT

    @staticmethod
    def export_config(output_file: str = 'config_export.json'):
        """
        Export configuration to a JSON file.

        Args:
            output_file: Output file path
        """
        config_data = {
            'canvas_formats': CANVAS_FORMATS,
            'fonts': FONTS,
            'font_sizes': FONT_SIZES,
            'svg_constraints': SVG_CONSTRAINTS
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

        print(f"Configuration exported to: {output_file}")


# ============================================================
# Command Line Interface
# ============================================================

def main() -> None:
    """Command line entry point."""
    import sys

    if len(sys.argv) < 2:
        print("PPT Master - Configuration Management Tool\n")
        print("Usage:")
        print("  python3 scripts/config.py list-formats     # List all canvas formats")
        print("  python3 scripts/config.py export           # Export configuration to JSON")
        print("  python3 scripts/config.py format <key>     # View a specific canvas format")
        return

    command = sys.argv[1]

    if command == 'list-formats':
        print("\nCanvas Format List:\n")
        for key, info in CANVAS_FORMATS.items():
            print(
                f"  {key:15} | {info['name']:15} | {info['dimensions']:12} | {info['use_case']}")

    elif command == 'export':
        output_file = sys.argv[2] if len(
            sys.argv) > 2 else 'config_export.json'
        Config.export_config(output_file)

    elif command == 'format' and len(sys.argv) > 2:
        format_key = sys.argv[2]
        info = Config.get_canvas_format(format_key)
        if info:
            print(f"\nCanvas Format: {format_key}\n")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print(f"[ERROR] Format not found: {format_key}")
            print(f"   Available formats: {', '.join(CANVAS_FORMATS.keys())}")

    else:
        print(f"[ERROR] Unknown command: {command}")


if __name__ == '__main__':
    main()
