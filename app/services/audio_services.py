from acrcloud.recognizer import ACRCloudRecognizer
from pydub import AudioSegment
from app.config import Config
import os

def recognize_song(audio_file_path):

    config = {
        'host': "identify-us-west-2.acrcloud.com",
        'access_key': Config.ARC_KEY,
        'access_secret': Config.ARC_ACCESS_SECRET,
    }

    recognizer = ACRCloudRecognizer(config)

    # Convert to WAV
    audio = AudioSegment.from_file(audio_file_path)
    wav_path = 'temp.wav'
    audio.export(wav_path, format="wav")

    result = recognizer.recognize_by_file(wav_path, 0)

    os.remove(wav_path)

    return result


def find_popular(song):
    # TODO: Implement popular song finding logic
    pass