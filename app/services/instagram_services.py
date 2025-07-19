from instagrapi import Client
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag
import os

# temp: in-memory session store (add db later)
user_sessions = {}

def login_user(username, password, verification_code=None):
    cl = Client()
    if os.path.exists(f'sessions/{username}.json'):
        cl.load_settings(f'sessions/{username}.json')
        cl.login(username, password)  # uses session, avoids 2FA
    else:
        cl.login(username, password, verification_code=verification_code)
    os.makedirs('sessions', exist_ok=True)
    cl.dump_settings(f'sessions/{username}.json')
    user_sessions[username] = cl
    return {"status": "logged_in", "username": username}

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

# def upload_story(username, video_path, caption="", mention=None, link=None, hashtag=None, media=None):
#     if username not in user_sessions:
#         raise Exception("User not logged in")
#     cl = user_sessions[username]

#     full_path = os.path.abspath(video_path)
#     if not os.path.exists(full_path):
#         raise Exception(f"Video file not found: {full_path}")

#     story_mention = None
#     if mention:
#         user_info = cl.user_info_by_username(mention['username'])
#         story_mention = StoryMention(
#             user=user_info,
#             x=mention['x'],
#             y=mention['y'],
#             width=mention['width'],
#             height=mention['height']
#         )

#     story_link = None
#     if link:
#         story_link = StoryLink(**link)

#     story_hashtag = None
#     if hashtag:
#         ht_info = cl.hashtag_info(hashtag['name'])
#         story_hashtag = StoryHashtag(
#             hashtag=ht_info,
#             x=hashtag['x'],
#             y=hashtag['y'],
#             width=hashtag['width'],
#             height=hashtag['height']
#         )

#     story_media = None
#     if media:
#         story_media = StoryMedia(
#             media_pk=media['media_pk'],
#             x=media['x'],
#             y=media['y'],
#             width=media['width'],
#             height=media['height']
#         )

#     try:
#         media_obj = cl.video_upload_to_story(
#             full_path,
#             caption,
#             mentions=[story_mention] if story_mention else None,
#             links=[story_link] if story_link else None,
#             hashtags=[story_hashtag] if story_hashtag else None,
#             medias=[story_media] if story_media else None
#         )
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         raise Exception(f"Story upload failed: {str(e)}")

#     return {"status": "uploaded", "media_id": media_obj.pk}

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
