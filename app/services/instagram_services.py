import json
from instagrapi import Client
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag
import os

# temp: in-memory session store (add db later)
user_sessions = {}
user_story_media_ids = {}

def login_user(username, password, verification_code=None):
    cl = Client()
    try:
        if os.path.exists(f'sessions/{username}.json'):
            cl.load_settings(f'sessions/{username}.json')
            # Try to use existing session without password
            cl.get_timeline_feed()  # Test if session is valid
        else:
            cl.login(username, password, verification_code=verification_code)
    except Exception:
        # Session invalid, do fresh login
        cl.login(username, password, verification_code=verification_code)
    
    os.makedirs('sessions', exist_ok=True)
    cl.dump_settings(f'sessions/{username}.json')
    
    user_sessions[username] = cl  # Store client in memory

    # Initialize media IDs tracking if not exists
    if username not in user_story_media_ids:
        user_story_media_ids[username] = []

    return {"status": "logged_in", "username": username}

def is_user_logged_in(username):
    return username in user_sessions

# no video extra sorry :'(
def upload_story(username, video_path, caption=""):
    print(f"Upload story called for user: {username}")
    print(f"Available sessions: {list(user_sessions.keys())}")
    
    if username not in user_sessions:
        raise Exception(f"User {username} not logged in. Available users: {list(user_sessions.keys())}")

    cl = user_sessions[username]

    full_path = os.path.abspath(video_path)
    if not os.path.exists(full_path):
        raise Exception(f"Video file not found: {full_path}")
    print("cl", cl)
    print("full_path", full_path)
    try:
        media = cl.video_upload_to_story(full_path, caption)

        # Store media ID in memory
        if username not in user_story_media_ids:
            user_story_media_ids[username] = []
        
        user_story_media_ids[username].append(media.pk)
        print(f"Added media ID {media.pk} to {username}'s story media IDs")
        print(f"Current media IDs for {username}: {user_story_media_ids[username]}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(f"Story upload failed: {str(e)}")
    print("media", media)
    return {"status": "uploaded", "media_id": media.pk}

# def upload_story(username, s3_key, caption=""):
#     cl = user_sessions.get(username) or load_or_login_user(username)

#     # Download the video from S3
#     bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
#     local_video_path = os.path.join('temp_uploads', os.path.basename(s3_key))
#     os.makedirs('temp_uploads', exist_ok=True)

#     try:
#         s3.download_file(bucket_name, s3_key, local_video_path)
#     except Exception as e:
#         raise Exception(f"Failed to download video from S3: {str(e)}")

#     try:
#         media = cl.video_upload_to_story(local_video_path, caption)
#         # Save the media_id in the database
#         save_story(concert_session_id=None, username=username, media_id=media.pk)
#     except Exception as e:
#         raise Exception(f"Story upload failed: {str(e)}")
#     finally:
#         # Clean up the local file
#         if os.path.exists(local_video_path):
#             os.remove(local_video_path)

#     return {"status": "uploaded", "media_id": media.pk}

def create_highlight(username, title, story_media_ids, cover_story_id=None):
    if username not in user_sessions:
        raise Exception("Not logged in")
    cl = user_sessions[username]
    highlight = cl.highlight_create(
        title=title,
        story_ids=story_media_ids,
        cover_story_id=cover_story_id or story_media_ids[0]
    )
    return {"highlight_id": highlight.pk, "title": highlight.title}

def add_to_highlight(username, highlight_id, story_media_ids):
    if username not in user_sessions:
        raise Exception("Not logged in")
    cl = user_sessions[username]
    highlight = cl.highlight_add_stories(highlight_id, story_media_ids)
    return {"highlight_id": highlight.pk, "media_count": len(highlight.media_ids)}

def upload_all_to_highlight(username, title):
    """Create a highlight with all uploaded stories for this user"""
    if username not in user_sessions:
        raise Exception(f"User {username} not logged in")
    
    # Check if we have any media IDs stored for this user
    if username not in user_story_media_ids or not user_story_media_ids[username]:
        raise Exception(f"No stories found for user {username}")
    
    media_ids = user_story_media_ids[username]
    print(f"Creating highlight for {username} with media IDs: {media_ids}")
    
    # Create the highlight
    return create_highlight(username, title, media_ids)

def clear_story_media_ids(username):
    """Clear the stored media IDs for a user"""
    if username in user_story_media_ids:
        user_story_media_ids[username] = []
        return {"status": "cleared", "username": username}
    return {"status": "not_found", "username": username}