"""
Beatmap download module.
Downloads .osz files from mirror servers with fallback support.
Prioritizes "no video" downloads.
"""

import re
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
)

from utils import format_size

# Browser-like User-Agent required by some mirrors (catboy.best rejects custom UAs)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

# Mirror chain — tried in order, "no video" is always prioritized
MIRRORS = [
    {
        'name': 'Nerinyan',
        'url': 'https://api.nerinyan.moe/d/{id}?noVideo=1',
    },
    {
        'name': 'catboy.best',
        'url': 'https://catboy.best/d/{id}?noVideo',
    },
]

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2       # seconds, exponential backoff
CHUNK_SIZE = 16384          # 16KB chunks
REQUEST_TIMEOUT = 120       # 2 minutes per download
DELAY_BETWEEN_BATCHES = 0.5 # delay between batch submissions


def _get_filename_from_response(response, beatmapset_id: int) -> str:
    """
    Extract filename from Content-Disposition header.
    Falls back to {beatmapset_id}.osz
    """
    content_disp = response.headers.get('content-disposition', '')
    if 'filename' in content_disp:
        # Try filename*= (RFC 5987) first, then filename=
        match = re.search(
            r"filename\*=(?:UTF-8''|utf-8'')(.+?)(?:;|$)", 
            content_disp, 
            re.IGNORECASE
        )
        if not match:
            match = re.search(
                r'filename=["\']?([^"\';\n\r]+)', 
                content_disp
            )
        if match:
            fn = requests.utils.unquote(match.group(1).strip())
            if fn:
                # Sanitize for Windows
                fn = re.sub(r'[<>:"/\\|?*]', '_', fn)
                # Ensure .osz extension
                if not fn.lower().endswith('.osz'):
                    fn += '.osz'
                return fn

    return f"{beatmapset_id}.osz"


def download_single(
    beatmapset_id: int,
    output_dir: Path,
    progress: Progress,
    overall_task_id,
) -> dict:
    """
    Download a single beatmapset, trying each mirror in sequence.
    
    Returns:
        dict with 'id', 'status' ('success'|'skipped'|'failed'), and extra info.
    """
    # Check if already exists (by ID prefix pattern)
    existing = list(output_dir.glob(f"{beatmapset_id}*.*"))
    for f in existing:
        if f.suffix.lower() == '.osz' and f.stat().st_size > 0:
            progress.update(overall_task_id, advance=1)
            return {
                'id': beatmapset_id,
                'status': 'skipped',
                'message': 'Sudah ada',
                'filename': f.name,
            }

    last_error = "Unknown error"

    for mirror in MIRRORS:
        url = mirror['url'].format(id=beatmapset_id)
        mirror_name = mirror['name']

        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    url,
                    stream=True,
                    timeout=REQUEST_TIMEOUT,
                    headers={'User-Agent': USER_AGENT},
                    allow_redirects=True,
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get(
                        'Retry-After', 
                        RETRY_BASE_DELAY * (2 ** attempt)
                    ))
                    time.sleep(retry_after)
                    continue

                # Non-200 → try next mirror
                if response.status_code != 200:
                    last_error = f"HTTP {response.status_code} from {mirror_name}"
                    break

                # Determine filename
                filename = _get_filename_from_response(response, beatmapset_id)
                filepath = output_dir / filename
                temp_filepath = output_dir / f".{beatmapset_id}.osz.tmp"

                # Download to temp file first
                downloaded = 0
                with open(temp_filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                # Validate download
                if downloaded > 1024:  # Minimum valid .osz size
                    # Rename temp to final
                    if filepath.exists():
                        filepath.unlink()
                    temp_filepath.rename(filepath)

                    progress.update(overall_task_id, advance=1)
                    return {
                        'id': beatmapset_id,
                        'status': 'success',
                        'mirror': mirror_name,
                        'size': downloaded,
                        'filename': filename,
                    }
                else:
                    temp_filepath.unlink(missing_ok=True)
                    last_error = f"File terlalu kecil ({downloaded}B) dari {mirror_name}"
                    break  # Try next mirror

            except requests.exceptions.Timeout:
                last_error = f"Timeout dari {mirror_name} (percobaan {attempt + 1})"
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue

            except requests.exceptions.ConnectionError:
                last_error = f"Koneksi gagal ke {mirror_name}"
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue

            except Exception as e:
                last_error = f"{mirror_name}: {str(e)[:80]}"
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY)
                continue

    # All mirrors exhausted
    progress.update(overall_task_id, advance=1)
    return {
        'id': beatmapset_id,
        'status': 'failed',
        'message': last_error,
    }


def download_beatmaps(
    beatmapset_ids: list,
    output_dir: Path,
    max_concurrent: int = 3,
) -> dict:
    """
    Download multiple beatmapsets with concurrent workers and progress display.
    
    Args:
        beatmapset_ids: List of beatmapset IDs to download.
        output_dir: Directory to save .osz files.
        max_concurrent: Number of parallel downloads (1-5).
        
    Returns:
        dict with 'success', 'skipped', 'failed' lists and 'total_size'.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        'success': [],
        'skipped': [],
        'failed': [],
        'total_size': 0,
    }

    total = len(beatmapset_ids)

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40, complete_style="green", finished_style="bright_green"),
        TextColumn("[bold]{task.percentage:>5.1f}%"),
        TextColumn("│"),
        TextColumn("[green]{task.completed}[/]/[cyan]{task.total}"),
        TextColumn("│"),
        TimeElapsedColumn(),
        TextColumn("│"),
        TimeRemainingColumn(),
        expand=False,
    ) as progress:

        overall = progress.add_task(
            f"Downloading {total} beatmapsets",
            total=total,
        )

        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = {}
            
            for i, bs_id in enumerate(beatmapset_ids):
                future = executor.submit(
                    download_single,
                    bs_id,
                    output_dir,
                    progress,
                    overall,
                )
                futures[future] = bs_id

                # Small stagger to avoid thundering herd
                if (i + 1) % max_concurrent == 0:
                    time.sleep(DELAY_BETWEEN_BATCHES)

            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    bs_id = futures[future]
                    result = {
                        'id': bs_id,
                        'status': 'failed',
                        'message': str(e),
                    }

                if result['status'] == 'success':
                    results['success'].append(result)
                    results['total_size'] += result.get('size', 0)
                elif result['status'] == 'skipped':
                    results['skipped'].append(result)
                else:
                    results['failed'].append(result)

    return results
