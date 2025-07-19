from flask import Blueprint, request, jsonify
from app.services.audio_services import recognize_song, find_popular
from app.services import instagram_services as ig_service
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

@bp.route('/instagram/login', methods=['POST'])
def instagram_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        result = ig_service.login_user(username, password)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/instagram/upload_story', methods=['POST'])
def instagram_upload_story():
    data = request.get_json()
    username = data.get('username')
    video_path = data.get('video_path')
    caption = data.get('caption', '')

    if not username or not video_path:
        return jsonify({"error": "Username and video_path required"}), 400

    try:
        result = ig_service.upload_story(username, video_path, caption)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
