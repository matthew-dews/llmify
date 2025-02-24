import argparse
import os
import re
from typing import List, Optional
from llmify.gitignore_parser import parse_gitignore


def collect_files(
    directory: str, gitignore_path: str, exclude_pattern: Optional[str] = None
) -> List[str]:
    gitignore = parse_gitignore(os.path.abspath(gitignore_path))

    file_contents = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if ".git" in file_path.split(os.sep):
                # Special case: don't traverse anything in a .git directory
                continue
            if not gitignore(file_path):
                if exclude_pattern and re.search(exclude_pattern, file_path):
                    continue
                relative_path = os.path.relpath(file_path, directory)
                try:
                    with open(file_path, "r") as f:
                        file_contents.append(
                            f"# {relative_path}\n```\n{f.read()}\n```\n"
                        )
                except UnicodeDecodeError:
                    pass
    return file_contents


def write_to_file(file_contents: List[str], output_file: str) -> None:
    with open(output_file, "w") as file:
        file.write("\n".join(file_contents))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect files and write their contents to a file."
    )
    parser.add_argument("--exclude", type=str, help="Regex pattern to exclude files")
    args = parser.parse_args()

    current_directory = "."
    gitignore_path = ".gitignore"
    output_file = "llmify-output.md"

    # delete output file if it already exists
    if os.path.exists(output_file):
        os.remove(output_file)

    exclude_pattern = args.exclude
    file_contents = collect_files(current_directory, gitignore_path, exclude_pattern)
    write_to_file(file_contents, output_file)

    print(f"Folder contents written to {output_file}")


if __name__ == "__main__":
    main()
