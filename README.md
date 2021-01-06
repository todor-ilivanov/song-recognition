# Starlord Recognition App
A web application that generates a Spotify playlist based on a screenshot with a result from a Google query.

Workflow of the app:
1. Scan a provided screenshot or list of screenshots for the track name
2. Find the track in Spotify
3. Create a playlist if it doesn't exist
4. Add the track to the dedicated playlist

## Running the App
1. Make sure you have the `virtualenv` package installed.
2. Create the virtualenv
    `virtualenv starlord-venv`
3. Activate the virtualenv
    `./{virtualenv_name}/Scripts/activate`
4. Run `pip install -r requirements.txt`
5. Navigate to the `src` directory
6. Run `flask run -p 8080`

## Running Tests
From the project directory, run: 
`pytest -W ignore::DeprecationWarning`