### Set up

- Copy `.env-example` to `.env` and adjust the config variables for your environment.
- Create a new Postgres database for the name used in `DATABASE_URI` in the `.env` file.
The app might work with older versions of PostgreSQL, but it is only tested with version 12.
- Install the requirements from `requirements.txt`. If you are setting up a development environment, install
`requirements-dev.txt` too.
- Before doing any development, run `pre-commit install` to set up the git hooks for the project.

### Initialize Database

- Download the HUC8 GeoDatabase from ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/WBD/National/GDB/
and unzip the GDB file in the path mentioned in `CONFIG["huc8"]` in `import_data.py`.
- Download the `practices` spreadsheet and put it in the path mentioned `CONFIG["practices"]` in `import_data.py`.
- Run `python import_data.py` to populate the database.

### Use Connexion

`./manage` script is a wrapper for Connexion cli.
It handles some of the environment variable for the Flask server used by Connexion.
This script accepts two flags:
`-h` shows help and `-d` calls `flask` with development variables.

In order to run the server in development mode, call `./manage -d`.
