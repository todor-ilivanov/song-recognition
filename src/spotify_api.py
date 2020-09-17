import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import redirect

from . import vision

class SpotifyAPI:

    auth_manager = None
    client = None
    PLAYLIST_NAME = 'discoveries v0.1-test'
        
    def __init__(self, cache_path):
        self.auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=cache_path)
        self.has_auth_token(self.auth_manager)
        self.client = spotipy.Spotify(auth_manager=self.auth_manager)

    def has_auth_token(self, auth_manager):
        if not self.auth_manager.get_cached_token():
            return redirect('/')
    
    def currently_playing(self):
        track = self.client.current_user_playing_track()
        if track is None:
            return "No track currently playing."
        return track

    def current_user(self):
        try:
            return self.client.current_user()
        except:
            raise Exception("Error getting current user.")

    def get_playlists(self):
        try:
            return self.client.current_user_playlists()
        except:
            raise Exception("Error finding playlist.")

    def get_playlist_names(self):
        playlists = self.get_playlists()
        playlist_names = [pl['name'] for pl in playlists['items']]
        return playlist_names

    def get_playlist_id(self, name):
        playlists = self.get_playlists()
        playlist = [pl for pl in playlists['items'] if pl['name'] == name][0]
        # pprint.pprint(playlist)
        return playlist['id']

    def create_playlist(self, name):
        playlist_names = self.get_playlist_names()

        if name not in playlist_names:
            try:
                user_id = self.client.me()['id']
                response = self.client.user_playlist_create(
                    user=user_id, 
                    name=name, 
                    public=True, 
                    description="Songs recognized from screenshots are added to this playlist."
                )
                print(f'Playlist {name} created.')
                return response['id']
            except:
                raise Exception("Error creating playlist.")
        else:
            print("Playlist already exists.")
            return self.get_playlist_id(name)

    def search_track_id(self, track_name):
        try:
            first_result = self.client.search(track_name)['tracks']['items'][0]
            return first_result['id']
        except:
            raise Exception("Error looking up track name.")

    def add_track(self, screenshot_path):
        track_name = self.make_vision_request(screenshot_path)
        print(track_name)
        if track_name is None:
            raise Exception("No song found in the image.")

        track_id = self.search_track_id(track_name)
        playlist_id = self.create_playlist(self.PLAYLIST_NAME)

        try:
            self.client.playlist_add_items(playlist_id, [track_id])
            pprint.pprint(f'{track_name} added to playlist.')
            return f'{track_name} added to playlist.'
        except:
            pprint.pprint("Error adding track to playlist.")
            raise Exception("Error adding track to playlist.")

    def make_vision_request(self, screenshot_path):
        vision_api = vision.VisionAPI()
        vision_response = vision_api.request(screenshot_path)
        return vision_api.extract_track_name(vision_response)