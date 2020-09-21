import pytest
import unittest
from unittest.mock import MagicMock, Mock
from src.vision import VisionAPI
from test_stubs import *


TEST_IMAGE_PATH = 'test\\test_images\song-screenshot-1.png'
vision_api = VisionAPI()

class VisionAPITests(unittest.TestCase):

    def mock_vision_response(self, text):
        text_annotations = TextAnnotations(text)
        response = AnnotateImageResponse([text_annotations])
        return response

    def test_extract_track_name_success(self):
        vision_api.client.text_detection = MagicMock(return_value=self.mock_vision_response("It's Random Song by Random Band"))
        response = vision_api.request(TEST_IMAGE_PATH)
        track_name = vision_api.extract_track_name(response)
        assert track_name == "Random Song Random Band"

    def test_extract_track_name_error(self):
        expected_response = AnnotateImageResponse(None)
        expected_response.error = Error('Could not process image.')
        expected_error_msg = '{}\nFor more info on error messages, check: https://cloud.google.com/apis/design/errors'.format(
                        expected_response.error.message)

        vision_api.client.text_detection = MagicMock(return_value=expected_response)

        with pytest.raises(Exception) as e:    
            response = vision_api.request(TEST_IMAGE_PATH)
            track_name = vision_api.extract_track_name(response)

        assert e.value.args[0] == expected_error_msg

    def test_extract_track_name_invalid_image(self):
        vision_api.client.text_detection = MagicMock(return_value=self.mock_vision_response("Found some text but not a song name."))
        response = vision_api.request(TEST_IMAGE_PATH)
        track_name = vision_api.extract_track_name(response)
        assert track_name is None

    def test_extract_track_name_malformed_response(self):    
        response = AnnotateImageResponse([])
        track_name = vision_api.extract_track_name(response)
        assert track_name is None