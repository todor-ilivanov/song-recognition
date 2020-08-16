import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from vision import extract_song_name

PLAYLIST_NAME = 'discoveries v0.1'

def get_playlists(cache_path):
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=cache_path)
    if not auth_manager.get_cached_token():
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


def currently_playing(cache_path):
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=cache_path)
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


def current_user(cache_path):
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=cache_path)
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()


def create_playlist(cache_path):
    playlist_names = get_playlist_names(cache_path)

    if PLAYLIST_NAME not in playlist_names:
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=cache_path)

        if not auth_manager.get_cached_token():
            return redirect('/')

        spotify = spotipy.Spotify(auth_manager=auth_manager)
        user_id = spotify.me()['id']
        response = spotify.user_playlist_create(
            user=user_id, 
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
        return get_playlist_id(cache_path, PLAYLIST_NAME)


def get_playlist_id(cache_path, name):
    playlists = get_playlists(cache_path)
    playlist = [pl for pl in playlists['items'] if pl['name'] == name][0]
    pprint.pprint(playlist)
    return playlist['id']

def get_playlist_names(cache_path):
    playlists = get_playlists(cache_path)
    playlist_names = [pl['name'] for pl in playlists['items']]
    return playlist_names


def search_track_id(track_name):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    first_result = sp.search(track_name)['tracks']['items'][0]
    #pprint.pprint(first_result['id'])
    return first_result['id']


def add_track(cache_path, screenshot_path):
    track_name = extract_song_name(screenshot_path)
    track_id = search_track_id(track_name)
    playlist_id = create_playlist(cache_path)

    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=cache_path)
    if not auth_manager.get_cached_token():
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager)
    sp.playlist_add_items(playlist_id, [track_id])
    pprint.pprint("Track added to playlist.")

