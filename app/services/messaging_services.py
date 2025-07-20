from twilio.rest import Client
from app.config import Config

def send_message(song_options):
    account_sid = Config.TWILIO_ACCOUNT_SID
    auth_token = Config.TWILIO_AUTH_TOKEN

    client = Client(account_sid, auth_token)

    formatted_string = format_string(song_options)

    client.messages.create(
        to="16474795038",
        from_=Config.TWILIO_NUMBER,
        body=f"""Here are the songs we have detected: \n{formatted_string}\nPlease REPLY with the NUMBER corresponding to the song you'd like to post!"""
    )

def send_login_req_message():
    account_sid = Config.TWILIO_ACCOUNT_SID
    auth_token = Config.TWILIO_AUTH_TOKEN

    client = Client(account_sid, auth_token)

    client.messages.create(
        to="16474795038",
        from_=Config.TWILIO_NUMBER,
        body=f"""Welcome to LIT(m)!!! Please REPLY with your instagram username to login"""
    )

def format_string(song_options):
    formatted_songs = ""
    for index, song in enumerate(song_options):
        formatted_songs += f"\n{index+1}. {song['title']} by {song['artist']} ({index+1})"
    return formatted_songs
