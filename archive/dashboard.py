#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


def parse_checklist(file_path: Path) -> tuple[int, int, str | None]:
    """Parses a markdown checklist file and returns done, total, and optional title."""
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()

    all_tasks = re.findall(r"- \[( |x)\] ", content)
    total = len(all_tasks)
    done = sum(1 for t in all_tasks if t == "x")

    # Try to extract the first level-1 heading as the title
    title_match = re.search(r"^# (.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else None

    return done, total, title


def show_progress(
    done: int, total: int, title: str | None = None, bar_length: int = 40
) -> None:
    """Displays a progress bar in the terminal, optionally with a custom title."""
    percent = (done / total) * 100 if total else 0
    filled_length = int(bar_length * done // total) if total else 0
    bar = "█" * filled_length + "-" * (bar_length - filled_length)

    heading = f"📊 {title}" if title else "📊 Checklist Progress"
    print(f"{heading}")
    print(f"[{bar}] {done}/{total} tasks completed ({percent:.1f}%)\n")


def create_dashboard(config_file: Path) -> None:
    """
    Reads each line from `config_file` as a path to a .md checklist
    and displays the progress for each project.
    """
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        return

    with config_file.open("r", encoding="utf-8") as f:
        markdown_paths = [Path(line.strip()) for line in f if line.strip()]

    if not markdown_paths:
        print("❌ No markdown files found in the config file.")
        return

    print("\n===== Projects Dashboard =====\n")
    for md_path in markdown_paths:
        if not md_path.exists():
            print(f"⚠️  File not found: {md_path}")
            continue

        done, total, title = parse_checklist(md_path)
        show_progress(done, total, title)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Projects Dashboard from multiple Markdown checklists."
    )
    parser.add_argument(
        "config_file",
        type=str,
        help="Path to a file listing Markdown checklist file paths (one per line).",
    )
    args = parser.parse_args()

    config_path = Path(args.config_file)
    create_dashboard(config_path)


if __name__ == "__main__":
    main()
