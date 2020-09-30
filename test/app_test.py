import os
import io
import shutil
import pytest
import unittest
import json
from unittest.mock import MagicMock, Mock, patch
import flask_testing.utils 

from src.app import app
from src.spotify_api import SpotifyAPI, SpotifyApiError
import spotipy

class FlaskAppTests(unittest.TestCase):

    FLASK_SESSION_TEST_PATH = '.flask_session'
    SPOTIFY_CACHE_TEST_PATH = '.spotify_caches'
    MOCK_PLAYLIST_RESPONSE = { 'items': [{'name': 'pl1', 'id': 123}, {'name': 'pl2', 'id': 234}] }
 
    def setUp(self):    
        mock_auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path='some/cache/path')
        self.spotify_api = SpotifyAPI(mock_auth_manager)
        self.spotify_api.client.current_user = MagicMock(return_value='Current user')
        self.spotify_api.client.current_user_playing_track = MagicMock(return_value='Song currently playing')
        self.spotify_api.client.current_user_playlists = MagicMock(return_value=self.MOCK_PLAYLIST_RESPONSE)
        self.spotify_api.make_vision_request = MagicMock(return_value="Random Song by Random Band")
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        if os.path.exists(self.FLASK_SESSION_TEST_PATH):
            shutil.rmtree(self.FLASK_SESSION_TEST_PATH)

        if os.path.exists(self.SPOTIFY_CACHE_TEST_PATH):
            shutil.rmtree(self.SPOTIFY_CACHE_TEST_PATH)
 
    def test_index(self):
        tester = app.test_client()
        response = self.app.get('/', follow_redirects=True)
        assert response.status_code == 200

    def test_get_upload_page(self):
        response = self.app.get('/upload', follow_redirects=True)
        assert response.status_code == 200

    # def test_post_upload_page(self):
    #     with patch('src.app.session', dict()) as session:
    #         session['spotify'] = self.spotify_api
    #         data = dict(files=[(io.BytesIO(b'abc'), 'test1.dasda'), (io.BytesIO(b'def'), 'test.dsad')])
    #         response = self.app.post(
    #             '/upload', data=data, follow_redirects=True,
    #             content_type='multipart/form-data'
    #         )

    #         assert response.status_code == 2100
            #assertRedirects

    def test_get_playlists_page(self):
        with patch('src.app.session', dict()) as session:
            session['spotify'] = self.spotify_api
            response = self.app.get('/playlists', follow_redirects=True)
            
            assert response.status_code == 200
            assert json.loads(response.data) == self.MOCK_PLAYLIST_RESPONSE

    def test_get_playlists_error(self):
        with patch('src.app.session', dict()) as session:
            self.spotify_api.client.current_user_playlists = Mock(side_effect=SpotifyApiError)        
            session['spotify'] = self.spotify_api

            response = self.app.get('/playlists', follow_redirects=True)
            
            assert response.data.decode('utf-8') == 'Error finding playlist.'
    
    def test_get_currently_playing(self):
        with patch('src.app.session', dict()) as session:
            session['spotify'] = self.spotify_api
            response = self.app.get('/currently_playing', follow_redirects=True)
            
            assert response.status_code == 200
            assert response.data.decode('utf-8') == 'Song currently playing'

    def test_get_currently_playing_none(self):
        with patch('src.app.session', dict()) as session:
            self.spotify_api.client.current_user_playing_track = MagicMock(return_value=None)
            session['spotify'] = self.spotify_api
            response = self.app.get('/currently_playing', follow_redirects=True)
            
            assert response.status_code == 200
            assert response.data.decode('utf-8') == 'No track currently playing.'

    def test_get_current_user(self):
        with patch('src.app.session', dict()) as session:
            session['spotify'] = self.spotify_api
            response = self.app.get('/current_user', follow_redirects=True)
            
            assert response.status_code == 200
            assert response.data.decode('utf-8') == 'Current user'
            
    def test_get_current_user_error(self):
        with patch('src.app.session', dict()) as session:
            self.spotify_api.client.current_user = Mock(side_effect=SpotifyApiError)        
            session['spotify'] = self.spotify_api

            response = self.app.get('/current_user', follow_redirects=True)
            
            assert response.data.decode('utf-8') == 'Error getting current user.'

        
 