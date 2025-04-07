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

ASCII_LOGO = r"""
 __  __ _____  _______ _ _      
|  \/  |  __ \|__   __(_) |     
| \  / | |  | |  | |   _| | ___ 
| |\/| | |  | |  | |  | | |/ _ \
| |  | | |__| |  | |  | | |  __/
|_|  |_|_____/   |_|  |_|_|\___|  v{version}

Markdown checklist progress tracker
"""

__version__ = "0.1.0"


def print_banner():
    console.print()
    console.print(f"[bold green]{ASCII_LOGO.format(version=__version__)}[/bold green]")


def parse_checklist(file_path: Path) -> tuple[int, int, str]:
    """
    Reads a Markdown file, extracts the number of tasks done and total tasks,
    and tries to read a title from the first H1. Fallback is the file stem.
    """
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()

    all_tasks = re.findall(r"- \[( |x)\] ", content)
    total = len(all_tasks)
    done = sum(1 for t in all_tasks if t == "x")

    title_match = re.search(r"^# (.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem

    return done, total, title


def create_animated_dashboard(markdown_paths: list[Path]) -> None:
    """
    Displays the Rich animated progress bars in the console.
    """
    print_banner()
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

        for task_id, done in tasks:
            for _ in range(done):
                progress.advance(task_id)
                time.sleep(0.05)


def create_table_dashboard(markdown_paths: list[Path]) -> None:
    """
    Displays a Rich Table in the console (no animation).
    """
    print_banner()
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
        bar_len = int(percent // 5)
        bar = "█" * bar_len + "-" * (20 - bar_len)
        table.add_row(title, str(done), str(total), f"[{bar}]", f"{percent:.1f}%")

    console.print(table)


def create_html_dashboard(
    markdown_paths: list[Path], template_file: Path, css_file: Path, output_file: Path
) -> None:
    """
    Creates a standalone HTML file containing a responsive table of the progress.
    """
    # --- 1) Gather data ---
    rows_html = []
    for md_path in markdown_paths:
        if not md_path.exists():
            # Show some error info in the table
            rows_html.append(
                f"""
            <tr>
              <td>⚠️ {md_path.name}</td>
              <td>-</td>
              <td>-</td>
              <td>—</td>
              <td>-</td>
            </tr>
            """
            )
            continue

        done, total, title = parse_checklist(md_path)
        percent = (done / total) * 100 if total else 0
        bar_len = int(percent // 5)
        bar_str = "█" * bar_len + "-" * (20 - bar_len)
        rows_html.append(
            f"""
            <tr>
              <td>{title}</td>
              <td>{done}</td>
              <td>{total}</td>
              <td class="progress-bar">{bar_str}</td>
              <td>{percent:.1f}%</td>
            </tr>
        """
        )

    # Join all rows into one string
    table_rows = "\n".join(rows_html)

    # --- 2) Load the template and the CSS ---
    template_content = template_file.read_text(encoding="utf-8")
    css_content = css_file.read_text(encoding="utf-8")

    # --- 3) Insert the CSS and TABLE_ROWS into the template ---
    final_html = template_content.replace("{{ CSS }}", css_content).replace(
        "{{ TABLE_ROWS }}", table_rows
    )

    # --- 4) Write the HTML file ---
    with output_file.open("w", encoding="utf-8") as f:
        f.write(final_html)

    console.print(f"[bold green]HTML Dashboard created at: {output_file}[/bold green]")


def load_markdown_paths(config_file: Path) -> list[Path]:
    """
    Reads the config file, returns a list of valid paths.
    """
    if not config_file.exists():
        console.print(f"[bold red]❌ Config file not found:[/bold red] {config_file}")
        return []

    with config_file.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    return [Path(line) for line in lines]


def create_dashboard(
    config_file: Path,
    view: str,
    html_output: Path | None,
    template_file: Path | None,
    css_file: Path | None,
) -> None:
    markdown_paths = load_markdown_paths(config_file)
    if not markdown_paths:
        console.print(
            "[bold red]❌ No markdown files found in the config file.[/bold red]"
        )
        return

    # If user requested HTML export:
    if html_output:
        if not template_file or not css_file:
            console.print(
                "[bold red]❌ Must provide --template-file and --css-file when using --html-output[/bold red]"
            )
            return

        create_html_dashboard(
            markdown_paths=markdown_paths,
            template_file=template_file,
            css_file=css_file,
            output_file=html_output,
        )
        return

    # Otherwise, proceed with console-based animation or table
    if view == "table":
        create_table_dashboard(markdown_paths)
    else:
        create_animated_dashboard(markdown_paths)
