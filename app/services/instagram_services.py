from instagrapi import Client
import os

# temp: in-memory session store (add db later)
user_sessions = {}

def login_user(username, password):
    cl = Client()
    try:
        cl.login(username, password)
    except Exception as e:
        raise Exception(f"Login failed: {str(e)}")
    
    user_sessions[username] = cl
    return {"status": "logged_in", "username": username}

def is_user_logged_in(username):
    return username in user_sessions

def upload_story(username, video_path, caption=""):
    if username not in user_sessions:
        raise Exception("User not logged in")

    cl = user_sessions[username]
    
    try:
        media = cl.video_upload_to_story(video_path, caption)
    except Exception as e:
        raise Exception(f"Story upload failed: {str(e)}")
    
    return {"status": "uploaded", "media_id": media.pk}


# for official ig api
# INSTAGRAM_CLIENT_ID = os.getenv("INSTAGRAM_CLIENT_ID")
# INSTAGRAM_CLIENT_SECRET = os.getenv("INSTAGRAM_CLIENT_SECRET")
# REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI")
# def get_auth_url():
#     return (
#         f"https://api.instagram.com/oauth/authorize"
#         f"?client_id={INSTAGRAM_CLIENT_ID}"
#         f"&redirect_uri={REDIRECT_URI}"
#         f"&scope=user_profile,user_media"
#         f"&response_type=code"
#     )

# def exchange_code_for_token(code):
#     url = "https://api.instagram.com/oauth/access_token"
#     data = {
#         "client_id": INSTAGRAM_CLIENT_ID,
#         "client_secret": INSTAGRAM_CLIENT_SECRET,
#         "grant_type": "authorization_code",
#         "redirect_uri": REDIRECT_URI,
#         "code": code,
#     }
#     response = requests.post(url, data=data)
#     response.raise_for_status()
#     token_info = response.json()
#     return token_info  # contains access_token, user_id

# def store_user_token(user_id, token):
#     user_tokens[user_id] = token

# def get_user_token(user_id):
#     return user_tokens.get(user_id)

# def upload_story(user_id, image_url, caption=""):
#     token = get_user_token(user_id)
#     if not token:
#         raise Exception("User not authenticated")

#     # Upload container
#     url = f"https://graph.facebook.com/v19.0/{user_id}/media"
#     params = {
#         "image_url": image_url,
#         "caption": caption,
#         "access_token": token
#     }
#     resp = requests.post(url, data=params)
#     resp.raise_for_status()
#     creation_id = resp.json()["id"]

#     # Publish container
#     publish_url = f"https://graph.facebook.com/v19.0/{user_id}/media_publish"
#     publish_params = {
#         "creation_id": creation_id,
#         "access_token": token
#     }
#     publish_resp = requests.post(publish_url, data=publish_params)
#     publish_resp.raise_for_status()
#     return publish_resp.json()
