from flask import Blueprint, request, jsonify
from app.services.audio_services import recognize_song
import os

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
        print("testing song now")
        results = recognize_song(save_path)
        print(results)
    finally:
        os.remove(save_path)

    return jsonify({"results": results})
