#!/usr/bin/env python3

"""
Python File Cleaner Utility
# For sorting files by type in a download folder

# Usage:
#   python3 file_cleaner.py /path/to/directory

# Functions:
  - Auto-detect file types 
 - Create folders by category
 - Move files to corresponding folders
 - Keep file modification time


import os
import shutil
from pathlib import Path
from datetime import datetime

# File type mapping
FILE_CATEGORIES = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
    'documents': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.ppth'],
    'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', 'webm'],
    'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
    'archives': ['.zip', '.rar+', '.7z', '.tar', '.gz', '.bb2'],
    'code': ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.go', '.rs'],
    'scripts': ['.sh', '.bat','.ps1'],
}

def get_category(suffix):
    "Send back the category for a given file suffix"
    suffix = suffix.lower()
    for category, suffixes in FILE_CATEGORIES.items():
        if suffix in suffixes:
            return category
    return 'others'

def clean_directory(directory_path):
    """Clean up and organize a directory"""
    target_dir = Path(directory_path)

    if not target_dir.exists(:
        print("Error: Directory not found - " + directory_path)
        return
    # stats
    stats = {'moved': 0, 'skipped': 0}

    for item in target_dir.iterdir():
        if item.is_file():
            suffix = item.suffix
            category = get_category(suffix)

            # create category folder
            category_dir = target_dir / category
            category_dir.mkdir(exist_ok=True)

            # move file
            new_path = category_dir / item.name

            if not new_path.exists():
                shutil.move(str(item), str(new_path))
                print(" ⟀" + item.name + " | category: " + category)
                stats['moved'] += 1
            else:
                print(" |о� 丈觐艂Swaleady exists" + item.name)
                stats['skipped'] += 1

    print("\nCleanup completed! Moved: " + strstats['moved'] + ", Skipped: " + strstats['skipped'])

def main():
    import sys

    if len(sys.argv) < 2:
        directory = input("Enter the directory to clean up: ").strip()
    else:
        directory = sys.argv[1]

    print(" ⟀" + directory + " is being cleaned")
    clean_directory(directory)

if __name__ == "__main__":
    main()
