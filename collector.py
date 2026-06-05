"""
osu!Collector API interaction module.
Fetches collection data from osucollector.com.
"""

import requests

API_BASE = "https://osucollector.com/api/collections"


def fetch_collection(collection_id: int) -> dict:
    """
    Fetch collection data from osu!Collector API.
    
    Args:
        collection_id: The numeric ID of the collection.
        
    Returns:
        dict with keys:
            - id (int)
            - name (str)
            - uploader (str)
            - beatmap_count (int): Total individual beatmaps
            - beatmapset_count (int): Total beatmapsets (downloadable units)
            - beatmapsets (list[int]): List of beatmapset IDs
            - favourites (int)
            
    Raises:
        requests.HTTPError: If the API request fails.
        ValueError: If the response is malformed.
    """
    url = f"{API_BASE}/{collection_id}"

    response = requests.get(
        url,
        timeout=30,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/131.0.0.0 Safari/537.36'
            ),
            'Accept': 'application/json',
        }
    )
    response.raise_for_status()

    data = response.json()

    # Extract beatmapset IDs
    beatmapsets_raw = data.get('beatmapsets', [])
    beatmapset_ids = []
    for bs in beatmapsets_raw:
        bs_id = bs.get('id')
        if bs_id is not None:
            beatmapset_ids.append(bs_id)

    # Count total individual beatmaps
    total_beatmaps = data.get('beatmapCount', 0)
    if total_beatmaps == 0:
        total_beatmaps = sum(len(bs.get('beatmaps', [])) for bs in beatmapsets_raw)

    return {
        'id': data.get('id', collection_id),
        'name': data.get('name', 'Unknown Collection'),
        'uploader': data.get('uploader', {}).get('username', 'Unknown'),
        'beatmap_count': total_beatmaps,
        'beatmapset_count': len(beatmapset_ids),
        'beatmapsets': beatmapset_ids,
        'favourites': data.get('favourites', 0),
    }
