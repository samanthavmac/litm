from flask import Blueprint, request, jsonify
from app.services.audio_services import recognize_song, find_popular
import os
import json

bp = Blueprint('main', __name__)

@bp.route('/recognize_song', methods=['POST'])
def recognize_song_route():

    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    save_path = os.path.join('temp_uploads', file.filename)
    os.makedirs('temp_uploads', exist_ok=True)
    file.save(save_path)

    try:
        results_raw = recognize_song(save_path)
        results = json.loads(results_raw)
    finally:
        os.remove(save_path)

    try:
        song_data = results[0]
        title = song_data['title']
        artists = song_data.get('artists', [])
        artist_name = artists[0]['name'] if artists else 'Unknown'

        popular_part = find_popular(title, artist_name)

        return jsonify({
            "title": title,
            "artist": artist_name,
            "popular_part": popular_part
        })  
    except Exception as e:
        return jsonify({"error": "Song recognition failed", "details": str(e)}), 500
    