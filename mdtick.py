#!/usr/bin/env python3
import argparse
import re
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)

console = Console()


def parse_checklist(file_path: Path) -> tuple[int, int, str | None]:
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()

    all_tasks = re.findall(r"- \[( |x)\] ", content)
    total = len(all_tasks)
    done = sum(1 for t in all_tasks if t == "x")

    title_match = re.search(r"^# (.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem

    return done, total, title


def create_animated_dashboard(markdown_paths: list[Path]) -> None:
    console.print()
    console.print("[bold cyan]📋 Projects Checklist Dashboard[/bold cyan]\n")

    with Progress(
        TextColumn("[bold blue]{task.fields[project]}"),
        BarColumn(bar_width=30),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    ) as progress:
        tasks = []
        for md_path in markdown_paths:
            if not md_path.exists():
                console.print(f"[yellow]⚠️ File not found:[/yellow] {md_path}")
                continue

            done, total, title = parse_checklist(md_path)
            task_id = progress.add_task(
                "", total=total, completed=0, project=title
            )
            tasks.append((task_id, done))

        for task_id, done in tasks:
            for _ in range(done):
                progress.advance(task_id)
                time.sleep(0.05)


def create_table_dashboard(markdown_paths: list[Path]) -> None:
    console.print()
    table = Table(title="📋 Projects Checklist Dashboard")

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


def create_dashboard(config_file: Path, view: str) -> None:
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

    if view == "table":
        create_table_dashboard(markdown_paths)
    else:
        create_animated_dashboard(markdown_paths)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mdtick",
        description="📋 mdtick — track progress across multiple Markdown checklists",
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
        version="mdtick 1.0.0",
        help="Show the version and exit.",
    )
    args = parser.parse_args()
    ...
    config_path = Path(args.config_file)
    create_dashboard(config_path, args.view)


if __name__ == "__main__":
    main()
