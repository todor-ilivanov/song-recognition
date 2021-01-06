import os
import shutil
from werkzeug.utils import secure_filename

from src.spotify_api import SpotifyAPI, SpotifyApiError
from src.vision import VisionApiError

class FileUploader:

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    def __init__(self, upload_folder):
        print("Initializing FileUploader...")
        self.upload_folder = upload_folder


    def is_allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS       


    def set_up_directories(self):
        if not os.path.exists(self.upload_folder):
            os.mkdir(self.upload_folder)


    def create_file_path(self, dir_name, filename):
        return os.path.join(dir_name, filename)


    def upload_files(self, uploaded_files):

        self.set_up_directories()

        for file in uploaded_files:
            if not self.is_allowed_file(file.filename):
                raise ValueError('File not supported.')

            if file:
                filename = secure_filename(file.filename)
                image_path = self.create_file_path(self.upload_folder, filename) 
                file.save(image_path)
                print(f'File saved to: {image_path}')

        print(os.listdir(self.upload_folder))
