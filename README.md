Environment Variables that need to be set before running app:

GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Todor\Desktop\starlord\secrets\secrets.json"
FLASK_ENV = "development"
SPOTIPY_CLIENT_ID=
SPOTIPY_CLIENT_SECRET=
SPOTIPY_REDIRECT_URI="http://localhost:8080/"

Uses a virtual env "starlord" with the necessary dependencies installed.
Ensure to activate before running the app.

First:
 \starlord\Scripts\activate

Then:
flask run -p 8080

To run tests:
cd test
pytest -W ignore::DeprecationWarning
