
import os
from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import uuid
import pprint
import argparse

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

PLAYLIST_NAME = 'dev#01234'

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

    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
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

#TODO: does not need to be a route
@app.route('/search_track_id')
def search_track_id():
    if request.args.get('name'):
        track_name = request.args.get('name')

        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        first_result = sp.search(track_name)['tracks']['items'][0]
        pprint.pprint(first_result['id'])

        return first_result['id']
    else:
        # TODO: Handle error properly
        return "No track name specified."

@app.route('/create_playlist')
def create_playlist():
    playlist_names = get_playlist_names()
    #pprint.pprint(playlist_names)
    if PLAYLIST_NAME not in playlist_names:
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
        sp = spotipy.Spotify(auth_manager)
        user_id = sp.me()['id']
        sp.user_playlist_create(user=user_id, 
            name=PLAYLIST_NAME, 
            public=True, 
            description="Songs recognized from screenshots are added to this playlist."
        )

        return f'Playlist {PLAYLIST_NAME} created.'
    else:
        # TODO: Handle properly
        return "Playlist already exists."

def get_playlist_names():
    playlists = get_playlists()
    playlist_names = [pl['name'] for pl in playlists['items']]
    return playlist_names

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


'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
	app.run(threaded=True, port=int(os.environ.get("PORT", 8080)))