import os
import requests
from dotenv import load_dotenv

load_dotenv()

class MediaEngine:
    """
    MZ&SZ Engine: Specialized in Deep Media Retrieval (Movies & TV Series).
    Features integrated caching and deep metadata extraction for writers and budgets.
    """
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        # Multi-layer Cache for Media Entities
        self.media_cache = {
            "movie": {},
            "tv": {}
        }

    def search_media(self, query, media_type="movie"):
        """
        Unified search for Movies (MZ) or TV Series (SZ) with deep detail extraction.
        """
        cache_key = query.lower().strip()
        if cache_key in self.media_cache[media_type]:
            return self.media_cache[media_type][cache_key]

        try:
            # 1. Primary Search
            params = {
                "api_key": self.api_key,
                "query": query,
                "include_adult": "false",
                "language": "en-US"
            }
            res = requests.get(f"{self.BASE_URL}/search/{media_type}", params=params).json()
            
            results = res.get('results', [])
            if not results:
                return None

            results.sort(key=lambda x: x.get('popularity', 0), reverse=True)
            main_entity = results[0]
            entity_id = main_entity['id']

            # 2. Deep Metadata Retrieval
            extra_path = "aggregate_credits" if media_type == "tv" else "credits"
            full_res = requests.get(
                f"{self.BASE_URL}/{media_type}/{entity_id}",
                params={"api_key": self.api_key, "append_to_response": f"{extra_path},external_ids"}
            ).json()

            # 3. Structural Data Mapping
            crew = full_res.get(extra_path, {}).get('crew', [])
            
            data = {
                "id": entity_id,
                "type": media_type,
                "title": full_res.get('title') or full_res.get('name'),
                "overview": full_res.get('overview'),
                "poster": f"{self.IMAGE_BASE_URL}{full_res.get('poster_path')}" if full_res.get('poster_path') else None,
                "release_date": full_res.get('release_date') or full_res.get('first_air_date'),
                "rating": round(full_res.get('vote_average', 0), 1),
                "genres": [g['name'] for g in full_res.get('genres', [])],
                "status": full_res.get('status', 'Unknown'),
                "runtime": full_res.get('runtime') if media_type == "movie" else (full_res.get('episode_run_time', [0])[0] if full_res.get('episode_run_time') else 0),
                
                # --- NEW DATA FIELDS ---
                "budget": full_res.get('budget', 0), # Budget for movies
                "writer": next((c['name'] for c in crew if c['job'] in ['Writer', 'Screenplay', 'Author']), 'N/A'),
                # -----------------------
                
                "imdb_url": f"https://www.imdb.com/title/{full_res.get('external_ids', {}).get('imdb_id')}/" 
                            if full_res.get('external_ids', {}).get('imdb_id') else "N/A"
            }

            if media_type == "tv":
                data["seasons_count"] = full_res.get('number_of_seasons', 0)
                data["episodes_count"] = full_res.get('number_of_episodes', 0)
                data["creator"] = full_res.get('created_by', [{}])[0].get('name', 'N/A')
            else:
                data["director"] = next((c['name'] for c in crew if c['job'] == 'Director'), 'N/A')

            # 4. Cache Optimization
            self.media_cache[media_type][cache_key] = data
            return data

        except Exception as e:
            return {"error": f"MZ&SZ Engine Failure: {str(e)}"}