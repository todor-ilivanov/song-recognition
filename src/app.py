import os
import uuid
import argparse

from flask import Flask, session, request, redirect
from flask_session import Session

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from spotify_api import *
from file_upload import *

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '../.flask_session/'
app.config['UPLOAD_FOLDER'] = '../uploads'
Session(app)

caches_folder = '../.spotify_caches/'
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
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    ## Upload photos
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file[]")
        upload_files(uploaded_files, app.config['UPLOAD_FOLDER'], session_cache_path())
            
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
        f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
        f'<a href="/playlists">my playlists</a> | ' \
        f'<a href="/currently_playing">currently playing</a> | ' \
        f'<a href="/current_user">me</a>' \
        '''
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
            <input type="file" multiple="" name="file[]" >
            <input type=submit value=Upload>
        </form>
        '''

@app.route('/playlists')
def get_playlists_route():
    return get_playlists(session_cache_path())

@app.route('/currently_playing')
def currently_playing_route():
    return currently_playing(session_cache_path())

@app.route('/current_user')
def current_user_route():
    return current_user(session_cache_path())

@app.route('/sign_out')
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    return redirect('/')


'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
	app.run(threaded=True, port=int(os.environ.get("PORT", 8080)))