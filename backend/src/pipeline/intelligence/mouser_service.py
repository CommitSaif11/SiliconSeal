import requests
from core.config import settings

def fetch_ic(part_name: str):
    """
    Fetch IC info from Mouser Search API (keyword lookup).
    Returns the first part dict or None if not found.
    """
    api_key = settings.MOUSER_API_KEY
    if not api_key:
        raise RuntimeError("MOUSER_API_KEY is not set in environment (.env)")

    url = "https://api.mouser.com/api/v1/search/keyword"
    params = {"apiKey": api_key}
    payload = {
        "SearchByKeywordRequest": {
            "keyword": part_name,
            "records": 1,
            "startingRecord": 0
        }
    }

    r = requests.post(url, params=params, json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()

    parts = data.get("SearchResults", {}).get("Parts", [])
    return parts[0] if parts else None