from flask import Blueprint, request, jsonify
from app.services.audio_services import recognize_song, find_popular
from app.services.video_services import extract_clip_from_local_video
import os
from app.config import Config
from app.services import instagram_services as ig_service
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
        print("testing song now")
        results = recognize_song(save_path)
        print(results)
    finally:
        os.remove(save_path)

    return jsonify({"results": results})

@bp.route('/extract_lyrics_clip', methods=['POST'])
def extract_lyrics_clip_route():
    """Extract a clip from local video based on specific lyrics"""
    
    data = request.get_json()
    if not data or 'lyrics' not in data:
        return jsonify({"error": "Missing lyrics parameter"}), 400
    
    lyrics = data['lyrics']
    video_filename = data.get('video_filename', 'sample.mp4')
    
    # Path to your video file
    video_path = os.path.join('app', 'static', 'video_clips', video_filename)
    
    if not os.path.exists(video_path):
        return jsonify({"error": f"Video file {video_filename} not found"}), 404
    
    try:
        index_id = data.get('index_id')

        if not index_id:
            return jsonify({"error": "Missing index_id parameter"}), 400
        
        clip_result = extract_clip_from_local_video(video_path, lyrics, index_id)
        
        if clip_result:
            return jsonify({
                "success": True,
                "clip": clip_result
            })
        else:
            return jsonify({
                "success": False,
                "message": "No matching clip found for the given lyrics"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/create_index', methods=['POST'])
def create_index_route():
    """Create a new TwelveLabs index"""
    data = request.get_json()
    name = data.get('name', 'my_video_index')
    
    try:
        from app.services.video_services import create_index
        index = create_index(name)
        return jsonify({
            "success": True,
            "index_id": index.id,
            "index_name": index.name
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/list_indexes', methods=['GET'])
def list_indexes_route():
    """List all existing TwelveLabs indexes"""
    try:
        from app.services.video_services import get_client
        client = get_client()
        indexes = client.index.list()
        return jsonify({
            "success": True,
            "indexes": [
                {
                    "id": index.id,
                    "name": index.name
                } for index in indexes
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/debug_config', methods=['GET'])
def debug_config():
    """Debug route to check if API keys are loaded"""
    return jsonify({
        "twelvelabs_key_set": bool(Config.TWELVELABS_API_KEY),
        "twelvelabs_key_length": len(Config.TWELVELABS_API_KEY) if Config.TWELVELABS_API_KEY else 0
    })

@bp.route('/check_video_upload', methods=['POST'])
def check_video_upload():
    """Check if a video was uploaded to an index"""
    data = request.get_json()
    video_filename = data.get('video_filename', 'sample.mp4')
    index_id = data.get('index_id')
    
    if not index_id:
        return jsonify({"error": "Missing index_id"}), 400
    
    try:
        from app.services.video_services import get_client
        client = get_client()
        
        # Get tasks (uploads) for the index
        tasks = client.task.list(index_id=index_id)
        
        return jsonify({
            "success": True,
            "tasks": [
                {
                    "id": task.id,
                    "status": task.status,
                    "created_at": str(task.created_at) if hasattr(task, 'created_at') else None
                } for task in tasks
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/upload_video_only', methods=['POST'])
def upload_video_only_route():
    """Upload a video to an index without searching"""
    data = request.get_json()
    video_filename = data.get('video_filename', 'sample.mp4')
    index_id = data.get('index_id')
    
    if not index_id:
        return jsonify({"error": "Missing index_id"}), 400
    
    video_path = os.path.join('app', 'static', 'video_clips', video_filename)
    
    if not os.path.exists(video_path):
        return jsonify({"error": f"Video file {video_filename} not found"}), 404
    
    try:
        from app.services.video_services import upload_local_video
        upload_task = upload_local_video(video_path, index_id)
        
        return jsonify({
            "success": True,
            "task_id": upload_task.id,
            "status": upload_task.status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/extract_video_segments', methods=['POST'])
def extract_video_segments_route():
    """Extract video segments as separate MP4 files"""
    data = request.get_json()
    video_filename = data.get('video_filename')
    index_id = data.get('index_id')
    lyrics = data.get('lyrics')
    
    if not all([video_filename, index_id, lyrics]):
        return jsonify({"error": "Missing video_filename, index_id, or lyrics"}), 400
    
    video_path = os.path.join('app', 'static', 'video_clips', video_filename)
    
    if not os.path.exists(video_path):
        return jsonify({"error": f"Video file {video_filename} not found"}), 404
    
    try:
        from app.services.video_services import extract_clip_from_local_video, extract_video_segments
        
        # First, get the timestamps
        clip_result = extract_clip_from_local_video(video_path, lyrics, index_id)
        
        if not clip_result or not clip_result.get('best_match'):
            return jsonify({
                "success": False,
                "message": "No matching clips found"
            })
        
        # Extract the video segment (only the best match)
        extracted_files = extract_video_segments(video_path, [clip_result['best_match']])
        
        return jsonify({
            "success": True,
            "search_results": clip_result,
            "extracted_files": extracted_files
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

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
