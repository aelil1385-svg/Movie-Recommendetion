import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
TMDB_API_BASE = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p/w500"

class TMDBError(Exception):
    pass

def _get(path, params=None):
    if not TMDB_API_KEY:
        raise TMDBError("TMDB_API_KEY is not set. Put it in your .env file.")

    # Detect key type
    is_v4 = len(TMDB_API_KEY) > 40
    headers = {"accept": "application/json"}
    if is_v4:
        headers["Authorization"] = f"Bearer {TMDB_API_KEY}"

    # Always prepare params
    params = params or {}
    if not is_v4:
        params["api_key"] = TMDB_API_KEY  # v3 key always in query

    url = f"{TMDB_API_BASE}{path}"

    # Retry session
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        r = session.get(url, params=params, headers=headers, timeout=20)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise TMDBError(f"TMDB request failed: {e}")

    return r.json()

def trending(period='day'):
    data = _get(f"/trending/movie/{period}")
    return data.get("results", [])

def search_movies(query, page=1):
    data = _get("/search/movie", params={"query": query, "page": page, "include_adult": False})
    return data.get("results", [])

def search_person(query):
    data = _get("/search/person", params={"query": query, "include_adult": False})
    return data.get("results", [])

def person_movie_credits(person_id):
    data = _get(f"/person/{person_id}/movie_credits")
    # Combine cast and crew, but prioritize cast
    movies = data.get("cast", []) + data.get("crew", [])
    # unique by id
    seen = set()
    uniq = []
    for m in movies:
        mid = m.get("id")
        if mid not in seen:
            seen.add(mid)
            uniq.append(m)
    return uniq

def genres():
    data = _get("/genre/movie/list")
    return data.get("genres", [])

def discover_by_genre(genre_id, page=1):
    data = _get("/discover/movie", params={"with_genres": genre_id, "sort_by": "popularity.desc", "page": page})
    return data.get("results", [])

def movie_details(movie_id):
    return _get(f"/movie/{movie_id}")

def movie_videos(movie_id):
    data = _get(f"/movie/{movie_id}/videos", params={"language": "en-US"})
    return data.get("results", [])

def poster_url(poster_path):
    if not poster_path:
        return None
    return f"{IMG_BASE}{poster_path}"
