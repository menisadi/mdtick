#!/usr/bin/env python3
import argparse
import re
import time
from pathlib import Path
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)

console = Console()


def parse_checklist(file_path: Path) -> tuple[int, int, str | None]:
    """Parses a markdown checklist file and returns done, total, and optional title."""
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()

    all_tasks = re.findall(r"- \[( |x)\] ", content)
    total = len(all_tasks)
    done = sum(1 for t in all_tasks if t == "x")

    title_match = re.search(r"^# (.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem

    return done, total, title


def create_dashboard(config_file: Path) -> None:
    """Displays an animated dashboard using rich progress bars for multiple markdown files."""
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

    console.print("[bold cyan]\n📋 Projects Checklist Dashboard[/bold cyan]\n")

    with Progress(
        TextColumn("[bold blue]{task.fields[project]}"),
        BarColumn(bar_width=30),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,  # ← This keeps the bars visible
    ) as progress:
        tasks = []
        for md_path in markdown_paths:
            if not md_path.exists():
                console.print(f"[yellow]⚠️ File not found:[/yellow] {md_path}")
                continue

            done, total, title = parse_checklist(md_path)
            percent = (done / total) if total else 0

            task_id = progress.add_task(
                "", total=total, completed=0, project=title
            )
            tasks.append((task_id, done))

        for task_id, done in tasks:
            for _ in range(done):
                progress.advance(task_id)
                time.sleep(0.05)  # Animate the bar (adjust to taste)


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
