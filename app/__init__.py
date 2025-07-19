from flask import Flask
from flask_cors import CORS
from app.routes.routes import bp as main_bp

from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    load_dotenv()
    CORS(app)

    app.register_blueprint(main_bp)

    return app
