import os
import pytest
from pathlib import Path
from llmify.__main__ import collect_files, write_to_file

def create_test_files(tmp_path):
    """Helper function to create a test directory structure"""
    # Create some test files
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.py").write_text("def test():\n    pass")
    
    # Create a subdirectory with files
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("content3")
    
    # Create a .gitignore file
    gitignore_content = """
*.py
ignored_dir/
"""
    (tmp_path / ".gitignore").write_text(gitignore_content)
    
    # Create an ignored directory
    ignored_dir = tmp_path / "ignored_dir"
    ignored_dir.mkdir()
    (ignored_dir / "ignored.txt").write_text("should not be included")

def test_basic_file_collection(tmp_path):
    """Test basic file collection without any exclusions"""
    create_test_files(tmp_path)
    
    # Remove .gitignore to test basic collection
    (tmp_path / ".gitignore").unlink()
    
    # Create empty .gitignore for the test
    (tmp_path / ".gitignore").write_text("")
    
    file_contents = collect_files(str(tmp_path), str(tmp_path / ".gitignore"))
    
    # Check that all files are collected
    assert len(file_contents) == 3  # file1.txt, file2.py, subdir/file3.txt
    assert "file1.txt" in "\n".join(file_contents)
    assert "file2.py" in "\n".join(file_contents)
    assert "subdir/file3.txt" in "\n".join(file_contents)

def test_gitignore_exclusion(tmp_path):
    """Test that .gitignore rules are respected"""
    create_test_files(tmp_path)
    
    file_contents = collect_files(str(tmp_path), str(tmp_path / ".gitignore"))
    
    # Check that .py files and ignored_dir are excluded
    assert len(file_contents) == 2  # file1.txt, subdir/file3.txt
    assert "file1.txt" in "\n".join(file_contents)
    assert "file2.py" not in "\n".join(file_contents)
    assert "ignored_dir" not in "\n".join(file_contents)

def test_exclude_pattern(tmp_path):
    """Test the exclude pattern functionality"""
    create_test_files(tmp_path)
    
    # Remove .gitignore to test exclude pattern independently
    (tmp_path / ".gitignore").unlink()
    (tmp_path / ".gitignore").write_text("")
    
    # Exclude .txt files
    file_contents = collect_files(str(tmp_path), str(tmp_path / ".gitignore"), exclude_pattern=r"\.txt$")
    
    # Check that .txt files are excluded
    assert len(file_contents) == 1  # only file2.py
    assert "file1.txt" not in "\n".join(file_contents)
    assert "file2.py" in "\n".join(file_contents)
    assert "file3.txt" not in "\n".join(file_contents)

def test_output_format(tmp_path):
    """Test that the output is formatted correctly"""
    # Create a simple test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    (tmp_path / ".gitignore").write_text("")
    
    file_contents = collect_files(str(tmp_path), str(tmp_path / ".gitignore"))
    
    # Check the format
    expected_format = "# test.txt\n```\ntest content\n```\n"
    assert file_contents[0] == expected_format

def test_write_to_file(tmp_path):
    """Test writing collected contents to a file"""
    content = ["# file1.txt\n```\ncontent1\n```\n"]
    output_file = tmp_path / "output.md"
    
    write_to_file(content, str(output_file))
    
    # Check that the file was written correctly
    assert output_file.read_text() == content[0]
