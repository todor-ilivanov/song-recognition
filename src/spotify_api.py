import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from vision import VisionAPI

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

    def get_playlists(self):
        return self.client.current_user_playlists()

    def currently_playing(self):
        track = self.client.current_user_playing_track()
        if not track is None:
            return track
        return "No track currently playing."


    def current_user(self):
        return self.client.current_user()

    def create_playlist(self, name):
        playlist_names = self.get_playlist_names()

        if self.PLAYLIST_NAME not in playlist_names:
            user_id = self.client.me()['id']
            response = self.client.user_playlist_create(
                user=user_id, 
                name=name, 
                public=True, 
                description="Songs recognized from screenshots are added to this playlist."
            )
            print(f'Playlist {name} created.')
            # TODO: handle errors
            return response['id']
        else:
            # TODO: Handle properly
            print("Playlist already exists.")
            return self.get_playlist_id(self.PLAYLIST_NAME)


    def get_playlist_id(self, name):
        playlists = self.get_playlists()
        playlist = [pl for pl in playlists['items'] if pl['name'] == name][0]
        pprint.pprint(playlist)
        return playlist['id']

    def get_playlist_names(self):
        playlists = self.get_playlists()
        playlist_names = [pl['name'] for pl in playlists['items']]
        return playlist_names

    def search_track_id(self, track_name):
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        first_result = sp.search(track_name)['tracks']['items'][0]
        # TODO TRY
        # first_result = self.client.search(track_name)['tracks']['items'][0]
        #pprint.pprint(first_result['id'])
        return first_result['id']

    def add_track(self, screenshot_path):
        vision_api = VisionAPI()
        vision_response = vision_api.request(screenshot_path)
        track_name = vision_api.extract_track_name(vision_response)
        if track_name is None:
            raise Exception("No song found in the image.")

        track_id = self.search_track_id(track_name)
        playlist_id = self.create_playlist(self.PLAYLIST_NAME)

        self.client.playlist_add_items(playlist_id, [track_id])
        pprint.pprint("Track added to playlist.")

