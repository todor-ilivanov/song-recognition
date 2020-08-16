
import os
from werkzeug.utils import secure_filename

from spotify_api import add_track

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_files(uploaded_files, upload_folder, cache_path):
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))
            #pprint.pprint("file uploaded")

    ## Add to playlist
    for filename in os.listdir(upload_folder):
        image_path = f'{upload_folder}/{filename}'
        add_track(cache_path, image_path)