import hashlib
import os
import argparse
from collections import defaultdict
from typing import List, Dict, Tuple

def get_file_hash(filepath: str, block_size: int = 65536) -> str:
    """Calculate the MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                hasher.update(block)
        return hasher.hexdigest()
    except OSError:
        return ""

def find_duplicates(directory: str, min_size: int = 0) -> Dict[str, List[str]]:
    """
    Find duplicate files in a directory recursively.
    Returns a dictionary where key is hash and value is list of file paths.
    """
    size_groups: Dict[int, List[str]] = defaultdict(list)
    
    print(f"Scanning {directory}...")
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                size = os.path.getsize(filepath)
                if size >= min_size:
                    size_groups[size].append(filepath)
            except OSError:
                continue

    duplicates: Dict[str, List[str]] = defaultdict(list)
    potential_duplicates = {s: p for s, p in size_groups.items() if len(p) > 1}
    
    total_groups = len(potential_duplicates)
    
    if total_groups > 0:
        print(f"Found {total_groups} groups of files with same size. Checking hashes...")
    
    for _, paths in potential_duplicates.items():
        for path in paths:
            file_hash = get_file_hash(path)
            if file_hash:
                duplicates[file_hash].append(path)
                
    return {h: p for h, p in duplicates.items() if len(p) > 1}

def format_size(size: int) -> str:
    """Format size in bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def main():
    parser = argparse.ArgumentParser(description="Find duplicate files in a directory.")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--min-size", type=int, default=1, help="Minimum file size in bytes (default: 1)")
    parser.add_argument("--delete", action="store_true", help="Interactive delete mode")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory.")
        return

    duplicates = find_duplicates(args.directory, args.min_size)
    
    if not duplicates:
        print("
No duplicate files found.")
        return

    print(f"
Found {len(duplicates)} groups of duplicate files:")
    total_wasted = 0
    
    for file_hash, paths in duplicates.items():
        size = os.path.getsize(paths[0])
        wasted = size * (len(paths) - 1)
        total_wasted += wasted
        
        print(f"
Group {file_hash[:8]} ({format_size(size)} each):")
        for i, path in enumerate(paths):
            print(f"  {i+1}. {path}")
            
        if args.delete:
            keep = input("Enter number to keep (0 to skip group, 'a' to keep all): ")
            if keep.isdigit():
                idx = int(keep)
                if 1 <= idx <= len(paths):
                    keep_path = paths[idx-1]
                    print(f"Keeping {keep_path}")
                    for p in paths:
                        if p != keep_path:
                            try:
                                os.remove(p)
                                print(f"Deleted {p}")
                            except OSError as e:
                                print(f"Error deleting {p}: {e}")

    print(f"
Total wasted space found: {format_size(total_wasted)}")

if __name__ == "__main__":
    main()
