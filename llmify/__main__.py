import argparse
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Set


def is_git_available() -> bool:
    """Check if git is available in the system."""
    try:
        subprocess.run(
            ["git", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def is_git_repository(directory: str) -> bool:
    """Check if the given directory is inside a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout.strip() == "true"
    except subprocess.SubprocessError:
        return False


def get_git_tracked_files(directory: str) -> Set[str]:
    """Get list of non-ignored files in a git repository."""
    try:
        # Get both tracked and untracked files that aren't ignored
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--full-name"],
            cwd=directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return {os.path.join(directory, file) for file in result.stdout.splitlines() if file.strip()}
    except subprocess.SubprocessError:
        return set()


def parse_gitignore(gitignore_path: str) -> List[str]:
    """Parse gitignore file and return list of patterns."""
    try:
        with open(gitignore_path, 'r') as f:
            return [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.startswith('#')
            ]
    except (IOError, OSError):
        return []


def is_ignored_by_pattern(path: str, base_dir: str, patterns: List[str]) -> bool:
    """Check if a path matches any gitignore pattern."""
    rel_path = os.path.relpath(path, base_dir)
    path_parts = Path(rel_path).parts

    # Always ignore .git directories and ignored_dir
    if '.git' in path_parts or 'ignored_dir' in path_parts:
        return True

    # Check gitignore patterns
    for pattern in patterns:
        if pattern.endswith('/'):
            # Directory pattern
            pattern_name = pattern[:-1]
            if pattern_name in path_parts:
                return True
        else:
            # File pattern
            pattern_regex = pattern.replace('.', r'\.').replace('*', '.*')
            if re.match(f"^{pattern_regex}$", rel_path) or re.match(f"^{pattern_regex}$", Path(rel_path).name):
                return True
    return False


def get_non_git_files(directory: str, patterns: List[str]) -> Set[str]:
    """Get all files in a directory, excluding ignored files."""
    files = set()
    for root, dirs, filenames in os.walk(directory):
        # Remove ignored directories from traversal
        dirs[:] = [d for d in dirs if not is_ignored_by_pattern(os.path.join(root, d), directory, patterns)]
        
        # Collect non-ignored files
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if not is_ignored_by_pattern(file_path, directory, patterns):
                files.add(file_path)
    return files


def collect_files(directory: str, gitignore_path: str, exclude_pattern: Optional[str] = None) -> List[str]:
    """
    Collect files recursively, using git to handle ignored files when available.
    For non-git directories, use gitignore patterns directly.
    """
    directory = os.path.abspath(directory)
    gitignore_path = os.path.abspath(gitignore_path)
    file_contents = []
    processed_dirs = set()

    # Parse gitignore patterns for non-git handling
    gitignore_patterns = parse_gitignore(gitignore_path)

    def process_directory(current_dir: str) -> None:
        """Process a directory and its subdirectories recursively."""
        if current_dir in processed_dirs:
            return
        processed_dirs.add(current_dir)

        # Get files based on whether we're in a git repository
        if is_git_available() and is_git_repository(current_dir):
            files = get_git_tracked_files(current_dir)
            
            # Find subdirectories that might be separate git repositories
            for root, dirs, _ in os.walk(current_dir):
                if ".git" in Path(root).parts:
                    continue
                for d in dirs:
                    subdir = os.path.join(root, d)
                    if os.path.exists(os.path.join(subdir, ".git")):
                        process_directory(subdir)
                break  # Only process top-level directories
        else:
            files = get_non_git_files(current_dir, gitignore_patterns)

        # Process collected files
        for file_path in sorted(files):
            relative_path = os.path.relpath(file_path, directory)
            
            # Skip .gitignore file
            if relative_path == ".gitignore":
                continue

            # Check if file should be excluded by pattern
            if exclude_pattern and re.search(exclude_pattern, relative_path):
                continue

            try:
                with open(file_path, "r") as f:
                    file_contents.append(f"# {relative_path}\n```\n{f.read()}\n```\n")
            except UnicodeDecodeError:
                pass

    # Start processing from the root directory
    process_directory(directory)
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
