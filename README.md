### Set up

- Copy `config-example.py` to `instance/config.py` and adjust the config variables for your environment.
- Create a new Postgres database for the name used in `SQLALCHEMY_DATABASE_URI` in the config file.
The app might work with older versions of PostgreSQL, but it is only tested with version 12.
- Install the requirements from `requirements.txt`. If you are setting up a development environment, install
`requirements-dev.txt` too.

### Initialize Database

- Download the HUC8 Geodatabase from ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/WBD/National/GDB/,
unzip the GDB file, and update its path in `INIT_DB["huc8"]` in `config.py` to point to the path you saved the GDB.
- Download the `practices` spreadsheet and update its path in `INIT_DB["practices"]` in `config.py` to point to the path
you saved the Excel file.
- Run `./manage init-db` to populate the database.

### Use Flask

`./manage`  script is a wrapper for Flask cli, which handles some of the environment variable for Flask.
All arguments passed to `./manage` get passed to `flask` command directly. This script accepts two flags:
`-h` shows help and `-d` calls `flask` with development variables.

In order to run the server in development mode, call `./manage -d run`.
