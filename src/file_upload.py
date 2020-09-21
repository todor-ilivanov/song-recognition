import os
from werkzeug.utils import secure_filename

from . import spotify_api

class FileUploader:

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    UPLOAD_FOLDER = '../uploads'
    UNSUCCESSFUL_FOLDER = '../unsuccessful_images'

    def is_allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def upload_files(self, uploaded_files, spotify_api):

        if not os.path.exists(self.UPLOAD_FOLDER):
            os.mkdir(self.UPLOAD_FOLDER)

        if not os.path.exists(self.UNSUCCESSFUL_FOLDER):
            os.mkdir(self.UNSUCCESSFUL_FOLDER)

        for file in uploaded_files:
            if file and self.is_allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(self.UPLOAD_FOLDER, filename)
                file.save(image_path)
                try:
                    spotify_api.add_track(image_path)
                    os.remove(image_path)
                except: # save to errors folder for inspection
                    file.save(os.path.join(self.UNSUCCESSFUL_FOLDER, filename))
                    os.remove(image_path)