from pymongo import MongoClient
import os
from datetime import datetime

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client.get_database("litm")
story_collection = db["stories"]
users_collection = db["users"]

def save_story(concert_session_id, username, media_id, timestamp=None):
    story_data = {
        "concert_session_id": concert_session_id,
        "username": username,
        "media_id": media_id,
        "timestamp": timestamp or datetime.utcnow()
    }
    story_collection.insert_one(story_data)

def get_stories_by_session(concert_session_id):
    return list(story_collection.find({"concert_session_id": concert_session_id}))

def delete_stories_by_session(concert_session_id):
    story_collection.delete_many({"concert_session_id": concert_session_id})

