import argparse
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional


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


def get_git_tracked_files(directory: str) -> List[str]:
    """Get list of non-ignored files in a git repository."""
    try:
        # Get both tracked and untracked files that aren't ignored
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return [
            os.path.join(directory, file)
            for file in result.stdout.splitlines()
            if file.strip()
        ]
    except subprocess.SubprocessError:
        return []


def get_all_files(directory: str) -> List[str]:
    """Get all files in a directory, excluding .git directories."""
    files = []
    for root, _, filenames in os.walk(directory):
        if ".git" in Path(root).parts:
            continue
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files


def collect_files(directory: str, exclude_pattern: Optional[str] = None) -> List[str]:
    """
    Collect files recursively, respecting git ignore rules when in a git repository.
    For non-git directories, include all files except those in .git directories.
    """
    directory = os.path.abspath(directory)
    file_contents = []
    
    # If git is not available, collect all files
    if not is_git_available():
        files = get_all_files(directory)
    else:
        files = []
        # Start from the current directory
        dirs_to_process = [directory]
        
        while dirs_to_process:
            current_dir = dirs_to_process.pop()
            
            # Check if current directory is in a git repository
            if is_git_repository(current_dir):
                # Get files tracked by git in this repository
                files.extend(get_git_tracked_files(current_dir))
                
                # Find subdirectories that might be separate git repositories
                for root, dirs, _ in os.walk(current_dir):
                    if ".git" in Path(root).parts:
                        continue
                    for d in dirs:
                        subdir = os.path.join(root, d)
                        if os.path.exists(os.path.join(subdir, ".git")):
                            dirs_to_process.append(subdir)
                    break  # Only process top-level directories
            else:
                # For non-git directories, include all files
                files.extend(get_all_files(current_dir))

    # Process collected files
    for file_path in sorted(set(files)):  # Remove duplicates and sort
        if exclude_pattern and re.search(exclude_pattern, file_path):
            continue
        
        try:
            relative_path = os.path.relpath(file_path, directory)
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
    output_file = "llmify-output.md"

    # Delete output file if it already exists
    if os.path.exists(output_file):
        os.remove(output_file)

    file_contents = collect_files(current_directory, args.exclude)
    write_to_file(file_contents, output_file)

    print(f"Folder contents written to {output_file}")


if __name__ == "__main__":
    main()
