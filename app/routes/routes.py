from flask import Blueprint, request, jsonify, Response
from app.services.audio_services import recognize_song, find_popular
from app.services.messaging_services import send_message
from twilio.twiml.messaging_response import MessagingResponse

import os

bp = Blueprint('main', __name__)
user_song_options = {}

@bp.route('/recognize_song', methods=['POST'])
def recognize_song_route():

    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    save_path = os.path.join('temp_uploads', file.filename)
    os.makedirs('temp_uploads', exist_ok=True)
    file.save(save_path)

    try:
        results = recognize_song(save_path)
    finally:
        os.remove(save_path)

    try:

        print("sending message")
        phone_key = '16474795038'
        user_song_options[phone_key] = results
        send_message(results)
        return jsonify({"status": "message sent"})
    except Exception as e:
        return jsonify({"error": "Song recognition failed", "details": str(e)}), 500
    
@bp.route("/sms", methods=['POST'])
def sms_reply():
    from_number = request.form.get('From')
    song_number_str = request.form.get('Body')

    phone_key = from_number.lstrip('+')

    try:
        song_number = int(song_number_str)
    except (ValueError, TypeError):
        song_number = None

    resp = MessagingResponse()

    if phone_key in user_song_options and song_number is not None:
        songs = user_song_options[phone_key]
        if 1 <= song_number <= len(songs):
            song = songs[song_number-1]
            popular_part = find_popular(song['title'], song['artist'])
            resp.message(f"Sounds good! We'll be posting a video of '{song['title']}' by {song['artist']} soon! \nThe story will include the snippet with \"{popular_part}\"")
        else:
            resp.message("Sorry, that number is out of range. Please reply with a valid number.")
    else:
        resp.message("Sorry, we couldn't find your songs list or your reply was invalid.")

    return Response(str(resp), mimetype="application/xml")
