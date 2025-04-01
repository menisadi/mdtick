#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn

console = Console()


def parse_checklist(file_path: Path) -> tuple[int, int, str | None]:
    """Parses a markdown checklist file and returns done, total, and optional title."""
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()

    all_tasks = re.findall(r"- \[( |x)\] ", content)
    total = len(all_tasks)
    done = sum(1 for t in all_tasks if t == "x")

    # Try to extract the first level-1 heading as the title
    title_match = re.search(r"^# (.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem

    return done, total, title


def create_dashboard(config_file: Path) -> None:
    """Displays a dashboard table using rich for multiple markdown checklist files."""
    if not config_file.exists():
        console.print(
            f"[bold red]❌ Config file not found:[/bold red] {config_file}"
        )
        return

    with config_file.open("r", encoding="utf-8") as f:
        markdown_paths = [Path(line.strip()) for line in f if line.strip()]

    if not markdown_paths:
        console.print(
            "[bold red]❌ No markdown files found in the config file.[/bold red]"
        )
        return

    table = Table(title="\n📋 Projects Checklist Dashboard")

    table.add_column("Project", style="bold cyan")
    table.add_column("Done", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Progress", justify="left")
    table.add_column("Percent", justify="right")

    for md_path in markdown_paths:
        if not md_path.exists():
            table.add_row(f"[red]⚠️ {md_path.name}[/red]", "-", "-", "-", "-")
            continue

        done, total, title = parse_checklist(md_path)
        percent = (done / total) * 100 if total else 0
        bar = "█" * int(percent // 5) + "-" * (20 - int(percent // 5))
        table.add_row(
            title, str(done), str(total), f"[{bar}]", f"{percent:.1f}%"
        )

    console.print(table)


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
