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

__version__ = "0.2.0"

ASCII_LOGO = r"""
 __  __ _____  _______ _ _      
|  \/  |  __ \|__   __(_) |     
| \  / | |  | |  | |   _| | ___ 
| |\/| | |  | |  | |  | | |/ _ \
| |  | | |__| |  | |  | | |  __/
|_|  |_|_____/   |_|  |_|_|\___|  v{version}

Markdown checklist progress tracker
"""


def print_banner(console: Console):
    console.print()
    console.print(f"[bold green]{ASCII_LOGO.format(version=__version__)}[/bold green]")


def parse_checklist(file_path: Path) -> tuple[int, int, str]:
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()

    all_tasks = re.findall(r"- \[( |x)\] ", content)
    total = len(all_tasks)
    done = sum(1 for t in all_tasks if t == "x")

    title_match = re.search(r"^# (.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem

    return done, total, title


def create_animated_dashboard(console: Console, markdown_paths: list[Path]) -> None:
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
            task_id = progress.add_task("", total=total, completed=0, project=title)
            tasks.append((task_id, done))

        # Advance the bars
        for task_id, done in tasks:
            for _ in range(done):
                progress.advance(task_id)
                time.sleep(0.05)


def create_table_dashboard(console: Console, markdown_paths: list[Path]) -> None:
    table = Table(title="Dashboard")

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
        table.add_row(title, str(done), str(total), f"{bar}", f"{percent:.1f}%")

    console.print(table)


def create_dashboard(
    console: Console, config_file: Path, view: str, banner: bool
) -> None:
    if not config_file.exists():
        console.print(f"[bold red]❌ Config file not found:[/bold red] {config_file}")
        return

    with config_file.open("r", encoding="utf-8") as f:
        markdown_paths = [Path(line.strip()) for line in f if line.strip()]

    if not markdown_paths:
        console.print(
            "[bold red]❌ No markdown files found in the config file.[/bold red]"
        )
        return

    if banner:
        print_banner(console)
    if view == "table":
        create_table_dashboard(console, markdown_paths)
    else:
        create_animated_dashboard(console, markdown_paths)


def main() -> None:
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
        "--banner",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Do not show the MDTICK banner.",
    )
    parser.add_argument(
        "--export-html",
        type=str,
        default=None,
        help="Path to an output HTML file if you want to export the dashboard.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"mdtick {__version__}",
        help="Show the version and exit.",
    )
    args = parser.parse_args()

    # If exporting HTML, override the animated view to table
    if args.export_html and args.view == "animated":
        print(
            "Warning: The animated view causes a very large HTML with each step. "
            "Switching to table view for HTML export."
        )
        args.view = "table"

    # Create a console that records only if we're exporting
    console = Console(record=bool(args.export_html))

    config_path = Path(args.config_file)
    create_dashboard(console, config_path, args.view, args.banner)

    # If requested, export to HTML
    if args.export_html:
        html_content = console.export_html(inline_styles=True)
        with open(args.export_html, "w", encoding="utf-8") as f:
            f.write(html_content)
        console.print(f"\n[green]HTML exported to:[/green] {args.export_html}")


if __name__ == "__main__":
    main()
