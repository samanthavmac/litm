import requests
import json
import time
from typing import Dict, Union
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

client = TwelveLabs
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


def search_video(self, query: str, index_id: str):
    return client.search.query(
        index_id=index_id,
        query_text=query,
        options=["visual", "audio"]
    )


def get_video_clip(self, video_id: str) -> Dict:
    
    return self.client.video.get(video_id)


