import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ACTX:
    """
    Core Architecture for ACTX with Integrated Caching.
    Supports high-speed retrieval by storing previous queries in memory.
    """
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        if not self.api_key:
            raise ValueError("[-] System Configuration Error: TMDB_API_KEY missing in .env")
        
        self.person_cache = {} 
        self.movie_detail_cache = {} 

    def get_movie_details(self, movie_id):
        if movie_id in self.movie_detail_cache:
            return self.movie_detail_cache[movie_id]

        try:
            res = requests.get(
                f"{self.BASE_URL}/movie/{movie_id}",
                params={"api_key": self.api_key, "append_to_response": "credits"}
            ).json()
            
            crew = res.get('credits', {}).get('crew', [])
            director = next((m['name'] for m in crew if m['job'] == 'Director'), 'N/A')
            writer = next((m['name'] for m in crew if m['job'] in ['Writer', 'Screenplay', 'Story']), 'N/A')
            
            details = {
                "runtime": res.get('runtime', 0),
                "director": director,
                "writer": writer,
                "rating": round(res.get('vote_average', 0), 1)
            }

            self.movie_detail_cache[movie_id] = details
            return details
        except:
            return {"runtime": 0, "director": "N/A", "writer": "N/A", "rating": 0}

    def search_actor(self, name):
        cache_key = name.lower().strip()
        if cache_key in self.person_cache:
            return self.person_cache[cache_key]

        try:
            search_params = {"api_key": self.api_key, "query": name, "include_adult": "false"}
            search_res = requests.get(f"{self.BASE_URL}/search/person", params=search_params).json()
            
            results = search_res.get('results', [])
            if not results: return None
            
            results.sort(key=lambda x: x.get('popularity', 0), reverse=True)
            person_id = results[0]['id']

            ext_res = requests.get(f"{self.BASE_URL}/person/{person_id}/external_ids", params={"api_key": self.api_key}).json()
            full_data = requests.get(f"{self.BASE_URL}/person/{person_id}", params={"api_key": self.api_key, "append_to_response": "movie_credits"}).json()

            cast = full_data.get('movie_credits', {}).get('cast', [])
            crew = full_data.get('movie_credits', {}).get('crew', [])

            # Smart merging of Cast and Crew to avoid duplicates
            combined_works = {}
            
            for m in cast:
                m_id = m.get('id')
                if m_id:
                    combined_works[m_id] = {
                        "id": m_id,
                        "title": m.get('title') or m.get('name'),
                        "character": m.get('character', 'Actor'),
                        "release": m.get('release_date', 'N/A'),
                        "poster": f"{self.IMAGE_BASE_URL}{m.get('poster_path')}" if m.get('poster_path') else None,
                        "popularity": m.get('popularity', 0)
                    }

            target_jobs = ['Director', 'Writer', 'Screenplay', 'Story', 'Author']
            for m in crew:
                if m.get('job') in target_jobs:
                    m_id = m.get('id')
                    if m_id:
                        if m_id in combined_works:
                            combined_works[m_id]["character"] += f" / {m.get('job')}"
                        else:
                            combined_works[m_id] = {
                                "id": m_id,
                                "title": m.get('title') or m.get('name'),
                                "character": m.get('job'),
                                "release": m.get('release_date', 'N/A'),
                                "poster": f"{self.IMAGE_BASE_URL}{m.get('poster_path')}" if m.get('poster_path') else None,
                                "popularity": m.get('popularity', 0)
                            }

            works_list = list(combined_works.values())
            works_list.sort(key=lambda x: x.get('popularity', 0), reverse=True)

            # Returning top 50 works to show a comprehensive list without lagging the UI
            works = works_list[:50]

            data = {
                "name": full_data.get('name'),
                "imdb_url": f"https://www.imdb.com/name/{ext_res.get('imdb_id')}/" if ext_res.get('imdb_id') else "N/A",
                "birthday": full_data.get('birthday', 'N/A'),
                "place": full_data.get('place_of_birth', 'N/A'),
                "image": f"{self.IMAGE_BASE_URL}{full_data.get('profile_path')}" if full_data.get('profile_path') else None,
                "works": works
            }

            self.person_cache[cache_key] = data
            return data
        except Exception as e:
            return {"error": str(e)}