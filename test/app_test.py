import os
import shutil
import unittest
 
from src.app import app
from src.spotify_api import SpotifyAPI
import spotipy

class BasicTests(unittest.TestCase):
 
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # TODO init mocked spotify api object
        # mock_auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path='some/cache/path')
        # self.spotify_api = SpotifyAPI(mock_auth_manager)

    def tearDown(self):
        shutil.rmtree('.flask_session')
        shutil.rmtree('.spotify_caches')
 
    def test_main_page(self):
        tester = app.test_client()
        response = self.app.get('/', follow_redirects=True)
        assert response.status_code == 200

    # def test_upload_page(self):
    #     response = self.app.get('/upload', follow_redirects=True)
    #     assert response.status_code == 200

    # def test_upload_page(self):

    #     with self.app as c:
    #         with c.session_transaction() as sess:
    #             sess['spotify'] = self.spotify_api

    #         response = c.get('/playlists', follow_redirects=True)
    #         assert response.status_code == 200

        
 