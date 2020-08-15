import os
import uuid
import pprint
import argparse

from flask import Flask, session, request, redirect, send_from_directory, flash
from flask_session import Session
from werkzeug.utils import secure_filename

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from vision import extract_song_name

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = './uploads'
PLAYLIST_NAME = 'dev#01234'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private playlist-modify-public',
                                                cache_path=session_cache_path(), 
                                                show_dialog=True)

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
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a> | ' \
           f'<a href="/currently_playing">currently playing</a> | ' \
		   f'<a href="/current_user">me</a>' \


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pprint.pprint("file uploaded")
            
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/playlists')
def get_playlists():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


@app.route('/currently_playing')
def currently_playing():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/current_user')
def current_user():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()


@app.route('/sign_out')
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/create_playlist')
def create_playlist():
    playlist_names = get_playlist_names()

    if PLAYLIST_NAME not in playlist_names:
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
        if not auth_manager.get_cached_token():
            return redirect('/')
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        user_id = spotify.me()['id']
        response = spotify.user_playlist_create(user=user_id, 
            name=PLAYLIST_NAME, 
            public=True, 
            description="Songs recognized from screenshots are added to this playlist."
        )
        print(f'Playlist {PLAYLIST_NAME} created.')
        # TODO: handle errors
        return response['id']
    else:
        # TODO: Handle properly
        print("Playlist already exists.")
        return get_playlist_id(PLAYLIST_NAME)


def get_playlist_id(name):
    playlists = get_playlists()
    playlist = [pl for pl in playlists['items'] if pl['name'] == name][0]
    pprint.pprint(playlist)
    return playlist['id']

def get_playlist_names():
    playlists = get_playlists()
    playlist_names = [pl['name'] for pl in playlists['items']]
    return playlist_names

def search_track_id(track_name):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    first_result = sp.search(track_name)['tracks']['items'][0]
    pprint.pprint(first_result['id'])
    return first_result['id']


@app.route('/add_track')
def add_track():
    if request.args.get('name'):
        track_name = request.args.get('name')
        #track_name = extract_song_name('./song1.png')
        track_id = search_track_id(track_name)
        playlist_id = create_playlist()

        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
        if not auth_manager.get_cached_token():
            return redirect('/')

        sp = spotipy.Spotify(auth_manager=auth_manager)
        sp.playlist_add_items(playlist_id, [track_id])

        return "Song added."
    else:
        # TODO: Handle error properly
        return "No track name specified."

'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
	app.run(threaded=True, port=int(os.environ.get("PORT", 8080)))