from instagrapi import Client
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag
from app.services.db_service import get_user, update_instagram_session, save_story
import os
import boto3

# temp: in-memory session store (add db later)
user_sessions = {}

# Initialize S3 client
s3 = boto3.client('s3')

def login_user(username, password, verification_code=None):
    cl = Client()
    if os.path.exists(f'sessions/{username}.json'):
        cl.load_settings(f'sessions/{username}.json')
        cl.login(username, password)  # uses session, avoids 2FA
    else:
        cl.login(username, password, verification_code=verification_code)
    os.makedirs('sessions', exist_ok=True)
    cl.dump_settings(f'sessions/{username}.json')

# def load_or_login_user(username):
#     user = get_user(username)
#     if not user:
#         raise Exception("User not registered")

#     cl = Client()

#     if user.get('instagram_session'):
#         try:
#             cl.set_settings(user['instagram_session'])
#             cl.login(user['instagram_username'], user['ig_password'])
#             user_sessions[username] = cl
#             return cl
#         except Exception:
#             pass  # Fall back to fresh login

#     # Fresh login with IG credentials
#     cl.login(user['instagram_username'], user['ig_password'])
#     user_sessions[username] = cl
#     # Save session to DB for reuse
#     update_instagram_session(username, cl.get_settings())
#     return cl

def is_user_logged_in(username):
    return username in user_sessions

# no video extra sorry :'(
def upload_story(username, video_path, caption=""):
    if username not in user_sessions:
        raise Exception("User not logged in")

    cl = user_sessions[username]

    full_path = os.path.abspath(video_path)
    if not os.path.exists(full_path):
        raise Exception(f"Video file not found: {full_path}")

    try:
        media = cl.video_upload_to_story(full_path, caption)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(f"Story upload failed: {str(e)}")

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

# def create_highlight(username, title, story_media_ids, cover_story_id=None):
#     cl = user_sessions.get(username) or load_or_login_user(username)
#     try:
#         highlight = cl.highlight_create(
#             title=title,
#             story_ids=story_media_ids,
#             cover_story_id=cover_story_id or story_media_ids[0]
#         )
#         return {"highlight_id": highlight.pk, "title": highlight.title}
#     except Exception as e:
#         raise Exception(f"Highlight creation failed: {str(e)}")

# def add_to_highlight(username, highlight_id, story_media_ids):
#     cl = user_sessions.get(username) or load_or_login_user(username)
#     try:
#         highlight = cl.highlight_add_stories(highlight_id, story_media_ids)
#         return {"highlight_id": highlight.pk, "media_count": len(highlight.media_ids)}
#     except Exception as e:
#         raise Exception(f"Add to highlight failed: {str(e)}")