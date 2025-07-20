from pymongo import MongoClient
import os
from datetime import datetime
from bson import ObjectId
from passlib.hash import bcrypt
import boto3
import os

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client.get_database("litm")
story_collection = db["stories"]
users_collection = db["users"]
videos_collection = db["videos"]

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

def upload_file_to_s3(file_path, s3_key):
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    s3.upload_file(file_path, bucket_name, s3_key)
    s3_url = f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_key}"
    return s3_url

# Story Services
def save_story(concert_session_id, username, media_id, timestamp=None):
    story_data = {
        "concert_session_id": concert_session_id,
        "username": username,
        "media_id": media_id,
        "timestamp": timestamp or datetime()
    }
    story_collection.insert_one(story_data)

def get_stories_by_session(concert_session_id):
    return list(story_collection.find({"concert_session_id": concert_session_id}))

def delete_stories_by_session(concert_session_id):
    story_collection.delete_many({"concert_session_id": concert_session_id})


# User Services 
def create_user(username, app_password, ig_username, ig_password, phone_number, instagram_session=None):
    hashed_app_password = bcrypt.hash(app_password)
    
    user_data = {
        "app_username": username,
        "app_password_hash": hashed_app_password,
        "username": ig_username,
        "ig_password": ig_password,
        "phone_number": phone_number,
        "sessions": [],
        "current_session_id": None,
        "uploaded_video_ids": [],
        "instagram_session": instagram_session or {}
    }
    users_collection.insert_one(user_data)

def verify_user(app_username, app_password):
    user = get_user_by_app_username(app_username)
    if not user:
        return None
    if bcrypt.verify(app_password, user["app_password_hash"]):
        return user
    return None

def get_user(username):
    return users_collection.find_one({"username": username})

def get_user_by_app_username(app_username):
    return users_collection.find_one({"app_username": app_username})

def get_user_by_phone(phone_number):
    return users_collection.find_one({"phone_number": phone_number})

def update_user_session(username, session_id):
    users_collection.update_one(
        {"username": username},
        {"$set": {"current_session_id": session_id}, "$addToSet": {"sessions": session_id}}
    )

def add_uploaded_video_to_user(username, video_id):
    users_collection.update_one(
        {"username": username},
        {"$addToSet": {"uploaded_video_ids": video_id}}
    )

def update_instagram_session(username, instagram_session_data):
    users_collection.update_one(
        {"username": username},
        {"$set": {"instagram_session": instagram_session_data}}
    )

#  Video Services 
def save_video(uploader_username, concert_session_id, s3_raw_url, processing_status="pending", s3_processed_url=None):
    video_data = {
        "uploader_username": uploader_username,
        "concert_session_id": concert_session_id,
        "s3_raw_url": s3_raw_url,
        "s3_processed_url": s3_processed_url,
        "processing_status": processing_status,
        "timestamp_uploaded": datetime(),
        "timestamp_processed": None
    }
    result = videos_collection.insert_one(video_data)
    add_uploaded_video_to_user(uploader_username, str(result.inserted_id))
    return str(result.inserted_id)

def update_video_processing_status(video_id, new_status, s3_processed_url=None):
    update_fields = {"processing_status": new_status}
    if s3_processed_url:
        update_fields["s3_processed_url"] = s3_processed_url
        update_fields["timestamp_processed"] = datetime()

    videos_collection.update_one(
        {"_id": ObjectId(video_id)},
        {"$set": update_fields}
    )

def get_videos_by_user(username):
    return list(videos_collection.find({"uploader_username": username}))

def get_videos_by_session(concert_session_id):
    return list(videos_collection.find({"concert_session_id": concert_session_id}))