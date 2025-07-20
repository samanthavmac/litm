from flask import Blueprint, request, jsonify, Response
from app.services.audio_services import recognize_song, find_popular
from app.services.video_services import create_index, upload_local_video, extract_clip_from_local_video, extract_video_segments, get_client
from app.services.messaging_services import send_message, send_login_req_message
# from app.services.db_service import get_stories_by_session, get_user, create_user, verify_user
from twilio.twiml.messaging_response import MessagingResponse
from app.services.instagram_services import login_user, upload_story, create_highlight, add_to_highlight
from app.services.instagram_services import upload_all_to_highlight
import os
from app.config import Config
import time

bp = Blueprint('main', __name__)
user_song_options = {}
ig_user = ""
ig_pass = ""


@bp.route('/recognize_song', methods=['POST'])
def recognize_song_route():
    send_login_req_message()
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save video to temp_uploads
    video_filename = f"upload_{int(time.time())}_{file.filename}"
    video_path = os.path.join('temp_uploads', video_filename)
    os.makedirs('temp_uploads', exist_ok=True)
    file.save(video_path)

    try:
        # Recognize songs from the video
        results = recognize_song(video_path)
        
        # Create a new index for this video
        index_name = f"index_{int(time.time())}"
        index = create_index(index_name)
        
        # Upload video to the new index
        upload_task = upload_local_video(video_path, index.id)
        
        # Store everything in user_song_options
        phone_key = Config.NUMBER
        user_song_options[phone_key] = {
            'songs': results,
            'video_filename': video_filename,
            'index_id': index.id,  # Pass the dynamic index ID
            'upload_task_id': upload_task.id
        }
        
        send_message(results)
        return jsonify({
            "status": "message sent",
            "video_filename": video_filename,
            "index_id": index.id  # Return the dynamic index ID
        })
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(video_path):
            os.remove(video_path)
        return jsonify({"error": "Song recognition failed", "details": str(e)}), 500


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


# @bp.route('/list_indexes', methods=['GET'])
# def list_indexes_route():
#     """List all existing TwelveLabs indexes"""
#     try:
#         client = get_client()
#         indexes = client.index.list()
#         return jsonify({
#             "success": True,
#             "indexes": [
#                 {
#                     "id": index.id,
#                     "name": index.name
#                 } for index in indexes
#             ]
#         })
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": str(e)
#         }), 500

@bp.route('/debug_config', methods=['GET'])
def debug_config():
    """Debug route to check if API keys are loaded"""
    return jsonify({
        "twelvelabs_key_set": bool(Config.TWELVELABS_API_KEY),
        "twelvelabs_key_length": len(Config.TWELVELABS_API_KEY) if Config.TWELVELABS_API_KEY else 0
    })

# @bp.route('/check_video_upload', methods=['POST'])
# def check_video_upload():
#     """Check if a video was uploaded to an index"""
#     data = request.get_json()
#     video_filename = data.get('video_filename', 'sample.mp4')
#     index_id = data.get('index_id')
    
#     if not index_id:
#         return jsonify({"error": "Missing index_id"}), 400
    
#     try:
#         from app.services.video_services import get_client
#         client = get_client()
        
#         # Get tasks (uploads) for the index
#         tasks = client.task.list(index_id=index_id)
        
#         return jsonify({
#             "success": True,
#             "tasks": [
#                 {
#                     "id": task.id,
#                     "status": task.status,
#                     "created_at": str(task.created_at) if hasattr(task, 'created_at') else None
#                 } for task in tasks
#             ]
#         })
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": str(e)
#         }), 500

# @bp.route('/upload_video_only', methods=['POST'])
# def upload_video_only_route():
#     data = request.get_json()
#     video_filename = data.get('video_filename', 'sample.mp4')
#     index_id = data.get('index_id')
    
#     if not index_id:
#         return jsonify({"error": "Missing index_id"}), 400
    
#     video_path = os.path.join('app', 'static', 'video_clips', video_filename)
    
#     if not os.path.exists(video_path):
#         return jsonify({"error": f"Video file {video_filename} not found"}), 404
    
#     try:
#         from app.services.video_services import upload_local_video
#         upload_task = upload_local_video(video_path, index_id)
        
#         return jsonify({
#             "success": True,
#             "task_id": upload_task.id,
#             "status": upload_task.status
#         })
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": str(e)
#         }), 500

# @bp.route('/extract_video_segments', methods=['POST'])
# def extract_video_segments_route():
#     """Extract video segments as separate MP4 files"""
#     data = request.get_json()
#     video_filename = data.get('video_filename')
#     index_id = data.get('index_id')
#     lyrics = data.get('lyrics')
    
#     if not all([video_filename, index_id, lyrics]):
#         return jsonify({"error": "Missing video_filename, index_id, or lyrics"}), 400
    
#     video_path = os.path.join('app', 'static', 'video_clips', video_filename)
    
#     if not os.path.exists(video_path):
#         return jsonify({"error": f"Video file {video_filename} not found"}), 404
    
#     try:
        
#         # First, get the timestamps
#         clip_result = extract_clip_from_local_video(video_path, lyrics, index_id)
        
#         if not clip_result or not clip_result.get('best_match'):
#             return jsonify({
#                 "success": False,
#                 "message": "No matching clips found"
#             })
        
#         # Extract the video segment (only the best match)
#         extracted_files = extract_video_segments(video_path, [clip_result['best_match']])
        
#         return jsonify({
#             "success": True,
#             "search_results": clip_result,
#             "extracted_files": extracted_files
#         })
        
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": str(e)
#         }), 500

def ensure_instagram_login():
    """Ensure Instagram is logged in, using fallback credentials if needed"""
    global ig_user, ig_pass
    
    print("=== INSTAGRAM LOGIN FALLBACK DEBUG ===")
    
    # Check if we have valid credentials set via SMS
    if ig_user and ig_pass and ig_user != "litmyay":
        print(f"Using SMS-provided credentials for: {ig_user}")
        try:
            login_user(ig_user, ig_pass)
            print("SMS credentials login successful")
            return True
        except Exception as e:
            print(f"SMS credentials failed: {str(e)}")
            # Fall through to fallback credentials
    
    # Use fallback credentials
    print("Using fallback credentials")
    try:
        login_user("litmyay", "litm123")
        print("Fallback credentials login successful")
        return True
    except Exception as e:
        print(f"Fallback credentials also failed: {str(e)}")
        return False
    
@bp.route("/sms", methods=['POST'])
def sms_reply():
    from_number = request.form.get('From')
    body_text = request.form.get('Body')

    phone_key = from_number.lstrip('+')
    resp = MessagingResponse()

    global ig_user, ig_pass 
    
    is_number = False
    try:
        song_number = int(body_text)
        is_number = True
    except (ValueError, TypeError):
        song_number = None

    if phone_key in user_song_options and song_number is not None:
        user_data = user_song_options[phone_key]
        songs = user_data['songs']
        
        if 1 <= song_number <= len(songs):
            song = songs[song_number-1]
            popular_part = find_popular(song['title'], song['artist'])
            
            # Use the stored video and index info
            clip_result = extract_and_post_clip(
                song['title'], 
                popular_part,
                user_data['video_filename'],
                user_data['index_id']
            )
            
            if clip_result['success']:
                resp.message(f"Perfect! We've posted '{song['title']}' by {song['artist']} to Instagram! \nThe clip features: \"{popular_part}\"")
            else:
                resp.message(f"An error occurred :(")
        else:
            resp.message("Sorry, that number is out of range. Please reply with a valid number.")
    
    elif not is_number:
        if body_text.strip() == "!!!": # reset credentials request
            ig_user = ""
            ig_pass = ""
            resp.message("Instagram credentials have been reset. Please send your username.")
        elif ig_user == "": # set user
            ig_user = body_text.strip()
            resp.message("Thanks! Now please send your Instagram password.")
        elif ig_pass == "": # set pass
            ig_pass = body_text.strip()

            try: # attempt login
                login_user(ig_user, ig_pass)
                resp.message(f"Thank you! Your Instagram credentials for {ig_user} have been saved. You can now upload a video to recognize songs.")
            except Exception as e:
                ig_user = ""
                ig_pass = ""
                resp.message(f"Login failed: {str(e)}. Please send your Instagram username again.")
        else:
            resp.message(f"do you want to reset credentials? Respond with !!! to reset")

    else:
        resp.message("Sorry, we couldn't find your songs list or your reply was invalid.")

    return Response(str(resp), mimetype="application/xml")
@bp.route('/instagram/login', methods=['POST'])
def instagram_login():
    data = request.get_json()
    try:
        result = login_user(data['username'], data['password'], data.get('verification_code'))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/instagram/upload_story', methods=['POST'])
def instagram_upload():
    data = request.get_json()
    username = data.get('username')
    video_path = data.get('video_path')
    caption = data.get('caption', "")

    # mention = data.get('mention')
    # link = data.get('link')
    # hashtag = data.get('hashtag')
    # media = data.get('media')

    try:
        result = upload_story(
            username=username,
            video_path=video_path,
            caption=caption
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/instagram/create_highlight', methods=['POST'])
def instagram_create_highlight():
    data = request.get_json()
    return jsonify(create_highlight(
        data['username'],
        data['title'],
        data['story_media_ids'],
        data.get('cover_story_id')
    ))

@bp.route('/instagram/add_to_highlight', methods=['POST'])
def instagram_add_to_highlight():
    data = request.get_json()
    return jsonify(add_to_highlight(
        data['username'],
        data['highlight_id'],
        data['story_media_ids']
    ))

# @bp.route('/instagram/create_concert_highlight', methods=['POST'])
# def create_concert_highlight():
#     data = request.get_json()
#     username = data.get('username')
#     concert_session_id = data.get('concert_session_id')
#     title = data.get('title')

#     try:
#         # stories = get_stories_by_session(concert_session_id)
#         # media_ids = [story['media_id'] for story in stories]
#         media_ids = []  # Placeholder since db_service is commented out

#         if not media_ids:
#             return jsonify({"error": "No stories found for this session."}), 400

#         highlight = create_highlight(username, title, media_ids)
#         return jsonify({"status": "highlight_created", "highlight_id": highlight.pk})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
    
# @bp.route('/user/register', methods=['POST'])
# def register_user():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')
#     phone_number = data.get('phone_number')

#     if not all([username, password, phone_number]):
#         return jsonify({"error": "Missing required fields"}), 400

#     if get_user(username):
#         return jsonify({"error": "User already exists"}), 400

#     create_user(username, password, phone_number)
#     return jsonify({"status": "User registered successfully"})

# @bp.route('/user/login', methods=['POST'])
# def user_login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     user = verify_user(username, password)
#     if not user:
#         return jsonify({"error": "Invalid username or password"}), 401

#     access_token = create_access_token(identity=username)
#     return jsonify({"access_token": access_token})

# @bp.route('/user/logout', methods=['POST'])
# @jwt_required()
# def user_logout():
#     username = get_jwt_identity()
#     if username in user_sessions:
#         del user_sessions[username]
#     return jsonify({"status": "logged_out", "username": username})

def extract_and_post_clip(song_title, lyrics, video_filename, index_id):
    """Extract video clip and post to Instagram"""
    print(f"=== EXTRACT AND POST DEBUG ===")
    print(f"Song title: {song_title}")
    print(f"Lyrics: {lyrics}")
    print(f"Video filename: {video_filename}")
    print(f"Index ID: {index_id}")
    
    try:
        video_path = os.path.join('temp_uploads', video_filename)
        print(f"Video path: {video_path}")
        print(f"Video exists: {os.path.exists(video_path)}")
        
        # Get timestamps
        print("Extracting clip timestamps...")
        clip_result = extract_clip_from_local_video(video_path, lyrics, index_id)
        print(f"Clip result: {clip_result}")
        
        # If no matching clip found, create a random 5-second segment
        if not clip_result or not clip_result.get('best_match'):
            print("No matching clip found, creating random 5-second segment")
            
            import subprocess
            import re

            cmd = [
                'ffmpeg', '-i', video_path, 
                '-f', 'null', '-'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})', result.stderr)
            if duration_match:
                hours, minutes, seconds = map(int, duration_match.groups())
                total_duration = hours * 3600 + minutes * 60 + seconds
                
                # Create a random 5-second segment (avoiding the very end)
                import random
                max_start_time = max(0, total_duration - 5)
                start_time = random.uniform(0, max_start_time)
                
                fallback_match = {
                    'start_time': start_time,
                    'end_time': start_time + 5,
                    'duration': 5,
                    'match_number': 1,
                    'score': 0.0,
                    'confidence': 0.0
                }
                
                clip_result = {
                    'best_match': fallback_match,
                    'search_query': lyrics,
                    'video_path': video_path,
                    'total_matches_found': 0,
                    'is_fallback': True
                }
            else:
                return {"success": False, "error": "Could not determine video duration"}
        
        # Extract video
        print("Extracting video segment...")
        extracted_files = extract_video_segments(video_path, [clip_result['best_match']])
        print(f"Extracted files: {extracted_files}")
        
        if not extracted_files:
            return {"success": False, "error": "Failed to extract video"}
        
        # Post to Instagram with fallback login
        video_clip_path = extracted_files[0]['output_path']
        print(f"Video clip path: {video_clip_path}")
        
        # Use the fallback login system
        if not ensure_instagram_login():
            return {"success": False, "error": "Instagram login failed with all credentials"}
        
        print("Uploading to Instagram story...")
        # Always use the fallback username for upload since that's what we logged in with
        upload_story("litmyay", video_clip_path, f"{song_title}")
        print("Instagram upload successful")

        # Clean up the original video after successful extraction
        if os.path.exists(video_path):
            os.remove(video_path)
            print("Cleaned up original video file")
        
        print("=== END EXTRACT AND POST DEBUG ===")
        return {"success": True, "clip_path": video_clip_path}
        
    except Exception as e:
        print(f"ERROR in extract_and_post_clip: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}