Environment Variables that need to be set before running app:

GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Todor\Desktop\starlord\secrets\secrets.json"
FLASK_ENV = "development"
SPOTIPY_CLIENT_ID=
SPOTIPY_CLIENT_SECRET=
SPOTIPY_REDIRECT_URI="http://localhost:8080/"

Dependencies:

google-cloud-vision
spotipy
flask

Uses a virtual env "starlord" with flask installed.
Ensure to activate before running the app.

First:
 \starlord\Scripts\activate

Then:
flask run -p 8080

To run tests:
pytest -W ignore::DeprecationWarning
