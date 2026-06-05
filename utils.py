"""
Utility functions for osu! Beatmap Downloader.
"""

import re
import os
from pathlib import Path


def parse_collection_url(url: str):
    """
    Extract collection ID from an osu!Collector URL.
    
    Supports formats:
      - https://osucollector.com/collections/21770
      - https://osucollector.com/collections/21770/CARBONE'S-AIM-COLLECTION
      - 21770 (just the ID)
    
    Returns:
        int or None: The collection ID, or None if parsing fails.
    """
    url = url.strip()

    # Match URL pattern
    match = re.search(r'collections/(\d+)', url)
    if match:
        return int(match.group(1))

    # Accept raw numeric ID
    if url.isdigit():
        return int(url)

    return None


def find_osu_songs_dir():
    """
    Auto-detect the osu! Songs folder on Windows.
    
    Returns:
        Path or None: Path to the Songs folder, or None if not found.
    """
    possible_paths = []

    # Standard osu! stable location
    local_appdata = os.environ.get('LOCALAPPDATA', '')
    if local_appdata:
        possible_paths.append(Path(local_appdata) / 'osu!' / 'Songs')

    # Fallback paths
    possible_paths.extend([
        Path.home() / 'AppData' / 'Local' / 'osu!' / 'Songs',
        Path('C:/osu!/Songs'),
        Path('D:/osu!/Songs'),
        Path('E:/osu!/Songs'),
    ])

    # Check osu! lazer paths too
    roaming = os.environ.get('APPDATA', '')
    if roaming:
        possible_paths.append(Path(roaming) / 'osu' / 'Songs')

    for p in possible_paths:
        if p.exists() and p.is_dir():
            return p

    return None


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size string."""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.1f} {units[i]}"


def format_duration(seconds: float) -> str:
    """Format seconds to human-readable duration."""
    if seconds < 60:
        return f"{seconds:.1f} detik"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h {mins}m {secs}s"


def sanitize_filename(filename: str) -> str:
    """Remove/replace invalid characters from filename."""
    # Replace characters not allowed in Windows filenames
    return re.sub(r'[<>:"/\\|?*]', '_', filename)
