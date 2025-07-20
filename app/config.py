import os

class Config:
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    IG_USER_ID = os.environ.get('IG_USER_ID')
    IG_ACCESS_TOKEN = os.environ.get('IG_ACCESS_TOKEN')
    ARC_KEY = os.environ.get('ARC_KEY')
    ARC_ACCESS_SECRET = os.environ.get('ARC_ACCESS_SECRET')
    TWELVELABS_API_KEY = os.environ.get('TWELVELABS_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')
    NUMBER = os.environ.get('NUMBER')