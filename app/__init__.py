from flask import Flask
from flask_cors import CORS
from app.routes.routes import bp as main_bp
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    load_dotenv()
    CORS(app)
    # add this if we want to do oauth later?
    # app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') 
    # JWTManager(app)

    app.register_blueprint(main_bp)

    return app
