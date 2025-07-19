import requests
import json
import time
from typing import Dict, Union, List
from pathlib import Path
import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs
from app.config import Config

load_dotenv()

def get_client():
    """Get TwelveLabs client with API key"""
    if not Config.TWELVELABS_API_KEY:
        raise ValueError("TWELVELABS_API_KEY environment variable not set")
    return TwelveLabs(api_key=Config.TWELVELABS_API_KEY)

def create_index(name: str, model: str = "marengo2.7"):
    client = get_client()
    index = client.index.create(name=name, models=[{"name": model, "options": ["visual", "audio"]}])
    return index

def upload_video(video_url: str, index_id: str):
    client = get_client()
    task = client.task.create(index_id=index_id, url=video_url)
    print(f"Created task: id={task.id}")

    task.wait_for_done(sleep_interval=5, callback=lambda t: print(f"  Status={t.status}"))

    if task.status != "ready":
        raise RuntimeError(f"Indexing failed with status {task.status}")
    
    return task

def search_video_by_text(query: str, index_id: str):
    try:
        client = get_client()
        print(f"Searching with query: {query}")
        print(f"Index ID: {index_id}")
        
        search_results = client.search.query(
            index_id=index_id,
            query_text=query,
            options=["visual", "audio"]
        )
        print(f"Raw search results: {search_results}")
        return search_results
    except Exception as e:
        print(f"Error searching video: {e}")
        import traceback
        traceback.print_exc()
        return None

def upload_local_video(video_path: str, index_id: str):
    """Upload a local video file to an index"""
    try:
        client = get_client()
        print(f"Attempting to upload: {video_path}")
        print(f"File exists: {os.path.exists(video_path)}")
        
        # Try with 'file' parameter instead of 'file_path'
        task = client.task.create(index_id=index_id, file=video_path)
        print(f"Created task: id={task.id}")

        task.wait_for_done(sleep_interval=5, callback=lambda t: print(f"  Status={t.status}"))

        if task.status != "ready":
            raise RuntimeError(f"Indexing failed with status {task.status}")
        
        return task
    except Exception as e:
        print(f"Direct file upload failed: {e}")
        raise e

def extract_clip_from_local_video(video_path: str, search_text: str, index_id: str):
    """Extract a specific clip from a local video based on search text"""
    try:
        # Skip upload since video is already uploaded
        print(f"Video already uploaded, searching for: {search_text}")
        print(f"Index ID: {index_id}")
        
        # Search for the specific text
        search_results = search_video_by_text(search_text, index_id)
        print(f"Search results: {search_results}")
        
        if search_results and hasattr(search_results, 'data') and search_results.data:
            print(f"Found {len(search_results.data)} matches")
            
            # Return ALL matches instead of just the first one
            all_matches = []
            for i, match in enumerate(search_results.data[:10]):  # First 10 matches
                match_info = {
                    'match_number': i + 1,
                    'start_time': match.start,
                    'end_time': match.end,
                    'duration': match.end - match.start,
                    'confidence': match.confidence,
                    'score': match.score
                }
                all_matches.append(match_info)
                print(f"Match {i+1}: {match.start}s - {match.end}s (score: {match.score})")
            
            clip_info = {
                'all_matches': all_matches,
                'search_query': search_text,
                'video_path': video_path,
                'total_matches': len(search_results.data)
            }
            
            return clip_info
        else:
            print("No search results found")
            return None
            
    except Exception as e:
        print(f"Error extracting clip: {e}")
        import traceback
        traceback.print_exc()
        return None


