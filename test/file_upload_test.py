import io
import os
import shutil
import unittest
import pytest
from unittest.mock import MagicMock
from src.file_upload import FileUploader

class FileMock:
    filename = None

    def __init__(self, filename):
        self.filename = filename

    def save(self, path):
        pass

class FlaskAppTests(unittest.TestCase):

    upload_test_folder = './upload_test'

    file_uploader = FileUploader(upload_test_folder)

    def tearDown(self):
        if os.path.exists(self.upload_test_folder):
            shutil.rmtree(self.upload_test_folder)


    def test_is_allowed_file(self):
        assert self.file_uploader.is_allowed_file('scrn-shot.jpg') is True
        assert self.file_uploader.is_allowed_file('homework.pdf') is False


    def test_file_upload_success(self):
        mock_files = [FileMock('image1.jpg'), FileMock('image2.jpg')]

        try:
            self.file_uploader.upload_files(mock_files)
        except:
            pytest.fail('File Upload failed.')

    def test_file_upload_failure(self):
        mock_files = [FileMock('image1.jpg'), FileMock('image2.txt')]

        with pytest.raises(ValueError) as e:
            self.file_uploader.upload_files(mock_files)

        assert e.value.args[0] == "File not supported."
