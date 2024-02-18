import os
import shutil
import glob
import click
from pathlib import Path

@click.command()
@click.argument('src_dir', type=click.Path(exists=True))
@click.argument('dest_dir', type=click.Path())
@click.argument('patterns', nargs=-1, required=True)
def copy_files(src_dir, dest_dir, patterns):
    """
    Copies files from SRC_DIR to DEST_DIR based on matching PATTERNS.

    SRC_DIR is the source directory to copy files from.

    DEST_DIR is the destination directory where files are copied to.

    PATTERNS is a list of filename patterns to match (supports wildcards), e.g., *.txt.
    """
    # Ensure the source directory exists
    if not os.path.exists(src_dir):
        click.echo(f"Source directory '{src_dir}' does not exist.")
        return

    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Compile a list of all files in the source directory matching the patterns
    matching_files = []
    for root, _, files in os.walk(src_dir):
        for pattern in patterns:
            for filename in glob.fnmatch.filter(files, pattern):
                matching_files.append(os.path.join(root, filename))

    # Copy each matching file to the destination directory
    for file_path in matching_files:
        # Compute the destination path
        rel_path = os.path.relpath(file_path, src_dir)
        dest_path = os.path.join(dest_dir, rel_path)

        # Create any necessary directories in the destination path
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Copy the file
        shutil.copy(file_path, dest_path)
        click.echo(f"Copied: {file_path} to {dest_path}")

if __name__ == "__main__":
    copy_files()
