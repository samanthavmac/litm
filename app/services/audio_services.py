# from acrcloud.recognizer import ACRCloudRecognizer
from pydub import AudioSegment
from app.config import Config
from openai import OpenAI
import json

def recognize_song(audio_file_path):

    config = {
        'host': "identify-us-west-2.acrcloud.com",
        'access_key': Config.ARC_KEY,
        'access_secret': Config.ARC_ACCESS_SECRET,
        'timeout': 10
    }

    # audio = AudioSegment.from_file(audio_file_path)
    # window_duration = 15 * 1000  
    # step = 5 * 1000        

    # recognizer = ACRCloudRecognizer(config)

    # results = []
    # seen = set()

    # for start_ms in range(0, len(audio) - window_duration, step):
    #     segment = audio[start_ms:start_ms + window_duration]
    #     segment.export("temp.wav", format="wav")

    #     resp = recognizer.recognize_by_file("temp.wav", 0)
    #     data = json.loads(resp)

    #     if 'metadata' in data and 'music' in data['metadata']:
    #         top = data['metadata']['music'][0]
    #         title = top['title']
    #         artist = top['artists'][0]['name']
    #         timestamp = round(start_ms / 1000, 2)

    #         key = (title, artist)
    #         if key not in seen:
    #             seen.add(key)
    #             results.append({
    #                 "title": title,
    #                 "artist": artist,
    #                 "timestamp": timestamp
    #             })
    # return results

def find_popular(song_title, song_artist):
    client = OpenAI(
        api_key=Config.OPENAI_API_KEY
    )

    # completion = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "developer", "content": "You are a music expert that finds the most iconic part of a song based on lyrics."},
    #         {"role": "user", "content": 
    #          f"""
    #         Your task is to return only the most popular section of the song "{song_title}" by {song_artist}, with no extra explanation or introduction.

    #         This section must:
    #         - Be at max 10 words worth of lyrics, with no punctuation or extra words 
    #         - Be the most iconic, replayed, or recognizable part of the song

    #         DO NOT include any introduction, commentary, or phrases like "Sure", "Here you go", or "These are the lyrics". Just return the lyrics text — and nothing else.
    #          """}
    #     ]
    # )
    # return completion.choices[0].message.content