import requests
import json
import time
from typing import Dict, Union, List
from pathlib import Path
import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs
from app.config import Config
import subprocess

load_dotenv()

def get_client():
    """Get TwelveLabs client with API key"""
    if not Config.TWELVELABS_API_KEY:
        raise ValueError("TWELVELABS_API_KEY environment variable not set")
    return TwelveLabs(api_key=Config.TWELVELABS_API_KEY)

def create_index(name: str, model: str = "marengo2.7"):
    client = get_client()
    index = client.index.create(name=name, models=[{"name": model, "options": ["audio"]}])
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
            
            # Get only the top 1 match (best match)
            best_match = search_results.data[0]  # Get the first (best) match
            match_info = {
                'match_number': 1,
                'start_time': best_match.start,
                'end_time': best_match.end,
                'duration': best_match.end - best_match.start,
                'confidence': best_match.confidence,
                'score': best_match.score
            }
            print(f"Best Match: {best_match.start}s - {best_match.end}s (score: {best_match.score})")
            
            clip_info = {
                'best_match': match_info,
                'search_query': search_text,
                'video_path': video_path,
                'total_matches_found': len(search_results.data)
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

def extract_video_segments(video_path: str, matches: list):
    """Extract video segments as separate MP4 files"""
    extracted_files = []
    
    for match in matches:
        start_time = match['start_time']
        duration = match['duration']
        match_number = match['match_number']
        
        # Create output filename
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_filename = f"{base_name}_clip_{match_number}_{start_time}s_to_{start_time + duration}s.mp4"
        output_path = os.path.join('app', 'static', 'extracted_clips', output_filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            # Use ffmpeg to extract the segment
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-c', 'copy',  # Copy without re-encoding (faster)
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                extracted_files.append({
                    'match_number': match_number,
                    'start_time': start_time,
                    'end_time': start_time + duration,
                    'duration': duration,
                    'score': match['score'],
                    'confidence': match['confidence'],
                    'output_file': output_filename,
                    'output_path': output_path
                })
                print(f"Successfully extracted: {output_filename}")
            else:
                print(f"Failed to extract clip {match_number}: {result.stderr}")
                
        except Exception as e:
            print(f"Error extracting clip {match_number}: {e}")
    
    return extracted_files


