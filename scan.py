#!/usr/bin/env python3

import os
import argparse
import re
from tqdm import tqdm


def file_contains_tasklist(file_path):
    pattern = re.compile(r"^(\s*[\-\*\+]\s*\[[xX ]\])")

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if pattern.search(line):
                    return True
    except Exception as e:
        tqdm.write(f"Error reading file: {file_path} ({e})")
    return False


def find_markdown_files(folder):
    md_files = []
    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.lower().endswith(".md"):
                md_files.append(os.path.join(root, filename))
    return md_files


def main():
    parser = argparse.ArgumentParser(description="Find Markdown files with task lists.")
    parser.add_argument("folder", help="Folder to scan")
    parser.add_argument("output_file", help="File to write matching paths")
    args = parser.parse_args()

    print("📁 Scanning folder for Markdown files...")
    md_files = find_markdown_files(args.folder)

    print(f"🔍 Found {len(md_files)} markdown files. Scanning for task lists...\n")

    matching_files = []

    for file_path in tqdm(md_files, desc="Scanning files", unit="file"):
        if file_contains_tasklist(file_path):
            matching_files.append(file_path)

    with open(args.output_file, "w", encoding="utf-8") as out_f:
        for path in matching_files:
            out_f.write(path + "\n")

    print(
        f"\n✅ Done! Found {len(matching_files)} Markdown files containing task lists."
    )
    print(f"📄 Results written to: {args.output_file}")


if __name__ == "__main__":
    main()
