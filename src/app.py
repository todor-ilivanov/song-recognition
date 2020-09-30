import os
import uuid
import argparse
import json

from flask import Flask, session, request, redirect, render_template
from flask_session import Session

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from src.spotify_api import SpotifyAPI, SpotifyApiError
from src.file_upload import FileUploader

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope='user-read-currently-playing playlist-modify-private playlist-modify-public', 
        cache_path=session_cache_path(),
        show_dialog=True
    )

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.get_cached_token():
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 4. Signed in, display data
    session["spotify"] = SpotifyAPI(auth_manager)
    current_user = session["spotify"].current_user()["display_name"]
                
    return render_template('index.html', user=current_user)

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():

    upload_folder = './uploads'
    unsuccessful_folder = './unsuccessful_images'

    if request.method == 'POST': #TODO Handle exceptions
        uploaded_files = request.files.getlist("file[]")
        file_uploader = FileUploader(upload_folder, unsuccessful_folder)
        file_uploader.upload_files(uploaded_files)
        session["spotify"].add_all_from_dir(upload_folder)
        return redirect('/')

    return render_template('file_upload.html')

@app.route('/playlists')
def get_playlists_route():
    return session["spotify"].get_playlists()

@app.route('/currently_playing')
def currently_playing_route():
    return session["spotify"].currently_playing()

@app.route('/current_user')
def current_user_route():
    return session["spotify"].current_user()

@app.route('/sign_out')
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    return redirect('/')

@app.errorhandler(SpotifyApiError)
def handle_spotify_error(e):
    return e.message


'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
	app.run(threaded=True, port=int(os.environ.get("PORT", 8080)))