#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from md_dashboard.dashboard import (
    __version__,
    create_dashboard,
)


def main():
    # Figure out where this file is located so we can find templates relative to it.
    # (Alternatively, pick any logic you want for locating your default templates.)
    current_dir = Path(__file__).parent.resolve()
    default_template = current_dir / "templates" / "dashboard.html"
    default_css = current_dir / "templates" / "style.css"

    parser = argparse.ArgumentParser(
        prog="mdtick",
        description="mdtick — track progress across multiple Markdown checklists",
    )
    parser.add_argument(
        "config_file",
        type=str,
        help="Path to a file listing Markdown checklist file paths (one per line).",
    )
    parser.add_argument(
        "--view",
        choices=["animated", "table"],
        default="animated",
        help="Choose display mode: animated (default) or table view.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"mdtick {__version__}",
        help="Show the version and exit.",
    )
    parser.add_argument(
        "--html-output",
        type=str,
        default=None,
        help="If provided, outputs the dashboard as a standalone HTML file.",
    )
    parser.add_argument(
        "--template-file",
        type=str,
        default=str(default_template),  # <-- default value here
        help="Path to the HTML template file (used with --html-output).",
    )
    parser.add_argument(
        "--css-file",
        type=str,
        default=str(default_css),  # <-- default value here
        help="Path to the CSS file to inline (used with --html-output).",
    )

    args = parser.parse_args()

    config_path = Path(args.config_file)
    html_output = Path(args.html_output) if args.html_output else None
    template_path = Path(args.template_file) if args.template_file else None
    css_path = Path(args.css_file) if args.css_file else None

    create_dashboard(
        config_file=config_path,
        view=args.view,
        html_output=html_output,
        template_file=template_path,
        css_file=css_path,
    )


if __name__ == "__main__":
    main()
