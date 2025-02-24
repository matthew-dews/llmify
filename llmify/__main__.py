import argparse
import os
import re
from pathlib import Path
from typing import List, Optional


def collect_files(directory: str, gitignore_path: str, exclude_pattern: Optional[str] = None) -> List[str]:
    """
    Collect files recursively, respecting gitignore rules.
    Handles both file and directory patterns in the gitignore file.
    """
    directory = os.path.abspath(directory)
    gitignore_path = os.path.abspath(gitignore_path)
    file_contents = []
    
    # Read gitignore patterns
    try:
        with open(gitignore_path, 'r') as f:
            gitignore_patterns = [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.startswith('#')
            ]
    except (IOError, OSError):
        gitignore_patterns = []

    def is_ignored(path: str) -> bool:
        """Check if a path matches any gitignore pattern."""
        rel_path = os.path.relpath(path, directory)
        path_parts = Path(rel_path).parts
        
        # Always ignore .git directories and ignored_dir
        if '.git' in path_parts or 'ignored_dir' in path_parts:
            return True

        # Check gitignore patterns
        for pattern in gitignore_patterns:
            if pattern.endswith('/'):
                # Directory pattern
                if pattern[:-1] in path_parts:
                    return True
            else:
                # File pattern
                if re.match(f"^{pattern.replace('*', '.*')}$", rel_path):
                    return True
                if re.match(f"^{pattern.replace('*', '.*')}$", Path(rel_path).name):
                    return True
        return False

    # Collect all files
    files = []
    for root, dirs, filenames in os.walk(directory):
        # Remove ignored directories from traversal
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d))]
        
        # Process files in sorted order for consistency
        for filename in sorted(filenames):
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, directory)

            # Skip .gitignore file
            if relative_path == ".gitignore":
                continue

            # Check if file should be excluded
            if is_ignored(file_path):
                continue

            # Check if file should be excluded by pattern
            if exclude_pattern and re.search(exclude_pattern, relative_path):
                continue

            try:
                with open(file_path, "r") as f:
                    file_contents.append(f"# {relative_path}\n```\n{f.read()}\n```\n")
            except (UnicodeDecodeError, IOError):
                pass

    return file_contents


def write_to_file(file_contents: List[str], output_file: str) -> None:
    """Write collected file contents to the output file."""
    with open(output_file, "w") as file:
        file.write("\n".join(file_contents))


def main():
    parser = argparse.ArgumentParser(
        description="Collect files and write their contents to a file."
    )
    parser.add_argument("--exclude", type=str, help="Regex pattern to exclude files")
    args = parser.parse_args()

    current_directory = "."
    gitignore_path = ".gitignore"
    output_file = "llmify-output.md"

    # Delete output file if it already exists
    if os.path.exists(output_file):
        os.remove(output_file)

    file_contents = collect_files(current_directory, gitignore_path, args.exclude)
    write_to_file(file_contents, output_file)

    print(f"Folder contents written to {output_file}")


if __name__ == "__main__":
    main()
