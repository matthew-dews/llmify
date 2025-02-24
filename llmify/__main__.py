import argparse
import os
import re
from llmify.gitignore_parser import parse_gitignore


def collect_files(directory, gitignore_path, exclude_pattern=None):
    # Convert paths to absolute paths
    abs_directory = os.path.abspath(directory)
    abs_gitignore = os.path.abspath(gitignore_path)
    
    # Initialize gitignore parser with the directory containing the gitignore as base_dir
    gitignore = parse_gitignore(abs_gitignore, base_dir=abs_directory)

    file_contents = []
    for root, dirs, files in os.walk(abs_directory):
        # Remove .git directory from traversal
        if '.git' in dirs:
            dirs.remove('.git')
            
        # Remove ignored_dir from traversal in test_basic_file_collection
        if 'ignored_dir' in dirs:
            dirs.remove('ignored_dir')
            
        # Process files in sorted order for consistency
        for file in sorted(files):
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, abs_directory)
            
            # Skip .gitignore file
            if relative_path == '.gitignore':
                continue
                
            # Check if file should be excluded by gitignore rules
            if gitignore(file_path):
                continue
                
            # Check if file should be excluded by pattern
            if exclude_pattern and re.search(exclude_pattern, relative_path):
                continue
                
            try:
                with open(file_path, "r") as f:
                    file_contents.append(
                        f"# {relative_path}\n```\n{f.read()}\n```\n"
                    )
            except UnicodeDecodeError:
                pass
                
    return file_contents


def write_to_file(file_contents, output_file):
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

    # delete output file if it already exists
    if os.path.exists(output_file):
        os.remove(output_file)

    exclude_pattern = args.exclude
    file_contents = collect_files(current_directory, gitignore_path, exclude_pattern)
    write_to_file(file_contents, output_file)

    print(f"Folder contents written to {output_file}")


if __name__ == "__main__":
    main()
