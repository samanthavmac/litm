"""
Twelve Labs API client following the proper workflow:
1. Create index → tells TwelveLabs which model(s) & modalities to use
2. Upload videos → SDK calls the indexer, which generates and stores all embeddings automatically  
3. Search → you pass your plain-English string to search.query(...); the SDK embeds your query and retrieves the best matching timecodes from your indexed videos
"""
import requests
import json
import time
from typing import Dict, Union
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class TwelveLabsClient:
    
    def __init__(self):
    
        self.api_key = os.getenv('TWELVELABS_API_KEY')
        self.base_url = "https://api.twelvelabs.io/v1.3"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        return self
    
    def create_index(self, 
                    name: str,
                    model: str = "marengo2.7"):
        
        index = self.client.index.create(name=name, models=[{"name": model, "options": ["visual", "audio"]}])
                
        return index
    
    def upload_video(self, 
                    video_path: Union[str, Path],
                    index_id: str):
        
        task = self.client.task.create(index_id=index_id, url=video_path)
        print(f"Created task: id={task.id}")

        task.wait_for_done(sleep_interval=5, callback=lambda t: print(f"  Status={t.status}"))

        if task.status != "ready":
            raise RuntimeError(f"Indexing failed with status {task.status}")
        
        return task
    
    
    def search_video(self,  
                    query: str,
                    index_id: str):

        print(f"🔍 Searching for: '{query}'")
        
        search_results = self.client.search.query(index_id=index_id, query_text=query, options=["visual", "audio"])

        for clip in search_results.data:
            print(f" video_id={clip.video_id} score={clip.score} start={clip.start} end={clip.end} confidence={clip.confidence}")
        
        return search_results
    

    def get_video_clip(self, video_id: str) -> Dict:
        
        return self.client.video.get(video_id)
    
    
    