import os

class Config:
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    IG_USER_ID = os.environ.get('IG_USER_ID')
    IG_ACCESS_TOKEN = os.environ.get('IG_ACCESS_TOKEN')