from flask import Flask, request, jsonify
from flask_cors import CORS 
from engine import ACTX
from MZ_SZ import MediaEngine # Ensure the file is named MZ_SZ.py

app = Flask(__name__)
CORS(app) 

# Initializing global engine instances for caching
engine = ACTX()
media_engine = MediaEngine()

@app.route('/api/search', methods=['GET'])
def web_search():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Missing name parameter"}), 400
    
    result = engine.search_actor(name)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Not found"}), 404

@app.route('/api/search/media', methods=['GET'])
def web_media_search():
    query = request.args.get('query')
    media_type = request.args.get('type') # 'movie' or 'tv'
    
    if not query or not media_type:
        return jsonify({"error": "Missing parameters"}), 400
    
    result = media_engine.search_media(query, media_type)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Media not found"}), 404

@app.route('/api/search/universal', methods=['GET'])
def universal_search():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing query"}), 400

    # Execute search across all engines
    results = {
        "person": engine.search_actor(query),
        "movie": media_engine.search_media(query, "movie"),
        "tv": media_engine.search_media(query, "tv")
    }
    return jsonify(results), 200

@app.route('/api/movie/<int:movie_id>', methods=['GET'])
def get_movie_info(movie_id):
    details = engine.get_movie_details(movie_id)
    return jsonify(details), 200

# CRITICAL: This block must be at the very end
if __name__ == "__main__":
    app.run(debug=True, port=5000)