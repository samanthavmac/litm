from flask import Flask
from flask_cors import CORS

from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)

    # Enable CORS if needed
    CORS(app)


def create_app():
    load_dotenv()

    # Register services
    # app.register_blueprint(audio_bp, url_prefix='/audio')

    return app
