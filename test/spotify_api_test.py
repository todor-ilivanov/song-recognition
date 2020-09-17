import pytest
from unittest.mock import MagicMock, Mock
from src.spotify_api import SpotifyAPI
from test_stubs import *

MOCK_CACHE_PATH = './mock/cache/path'
MOCK_PLAYLIST_RESPONSE = { "items": [{"name": "pl1", "id": 123}, {"name": "pl2", "id": 234}] }
MOCK_TRACK_SEARCH_RESPONSE = {"tracks": {"items": [{"id": 123}]}}
TEST_IMAGE_PATH = "test\\test_images\song-screenshot-2.png"

spotify_api = SpotifyAPI(MOCK_CACHE_PATH)

def init_mocks_no_error():
    spotify_api.client.search = MagicMock(return_value=MOCK_TRACK_SEARCH_RESPONSE)
    spotify_api.client.current_user_playlists = MagicMock(return_value=MOCK_PLAYLIST_RESPONSE)
    spotify_api.client.user_playlist_create = MagicMock(return_value={"id": 456})
    spotify_api.client.me = MagicMock(return_value={"id": 789})
    spotify_api.client.playlist_add_items = MagicMock(return_value={"id": 789})
    spotify_api.make_vision_request = MagicMock(return_value="Random Song by Random Band")

def test_current_user():
    spotify_api.client.current_user = MagicMock(return_value="Current user")
    response = spotify_api.current_user()

    assert response == "Current user"

def test_current_user_failure():
    spotify_api.client.current_user = Mock(side_effect=Exception)

    with pytest.raises(Exception) as e:    
        response = spotify_api.current_user()

    assert e.value.args[0] == "Error getting current user."

def test_currently_playing():
    spotify_api.client.current_user_playing_track = MagicMock(return_value="Song currently playing")
    response = spotify_api.currently_playing()

    assert response == "Song currently playing"

def test_currently_playing_failure():
    spotify_api.client.current_user_playing_track = MagicMock(return_value=None)
    response = spotify_api.currently_playing()

    assert response == "No track currently playing."

def test_get_playlists():
    spotify_api.client.current_user_playlists = MagicMock(return_value="User's playlists")
    response = spotify_api.get_playlists()

    assert response == "User's playlists"

def test_get_playlists_failure():
    spotify_api.client.current_user_playlists = Mock(side_effect=Exception)

    with pytest.raises(Exception) as e:    
        response = spotify_api.get_playlists()

    assert e.value.args[0] == "Error finding playlist."

def test_get_playlist_names():
    init_mocks_no_error()
    playlist_names = spotify_api.get_playlist_names()

    assert playlist_names == ["pl1", "pl2"] 

def test_get_playlist_id():
    init_mocks_no_error()
    playlist_id = spotify_api.get_playlist_id("pl1")

    assert playlist_id == 123

def test_create_playlist_not_exists():
    init_mocks_no_error()
    playlist_id = spotify_api.create_playlist("pl3")

    assert playlist_id == 456

def test_create_playlist_exists():
    init_mocks_no_error()
    playlist_id = spotify_api.create_playlist("pl1")

    assert playlist_id == 123

def test_create_playlist_error():
    spotify_api.client.user_playlist_create = Mock(side_effect=Exception)
    
    with pytest.raises(Exception) as e:    
        playlist_id = spotify_api.create_playlist("pl3")

    assert e.value.args[0] == "Error creating playlist."

def test_search_track_id():
    init_mocks_no_error()
    track_id = spotify_api.search_track_id("track1")

    assert track_id == 123

def test_search_track_id_failure():
    spotify_api.client.search = Mock(side_effect=Exception)
    
    with pytest.raises(Exception) as e:    
        track_id = spotify_api.search_track_id("track1")

    assert e.value.args[0] == "Error looking up track name."

def test_add_track():
    init_mocks_no_error()

    response = spotify_api.add_track(TEST_IMAGE_PATH)

    assert response == "Random Song by Random Band added to playlist."

def test_add_track_error():
    init_mocks_no_error()
    spotify_api.client.playlist_add_items = Mock(side_effect=Exception)

    with pytest.raises(Exception) as e:    
        response = spotify_api.add_track(TEST_IMAGE_PATH)

    assert e.value.args[0] == "Error adding track to playlist."

def test_add_track_no_track_name():
    spotify_api.make_vision_request = MagicMock(return_value=None)

    with pytest.raises(Exception) as e:    
        response = spotify_api.add_track(TEST_IMAGE_PATH)

    assert e.value.args[0] == "No song found in the image."