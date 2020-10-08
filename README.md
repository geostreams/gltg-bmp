
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


### Run everything in Docker

Adjust the variables for docker services in a `.env` file in the root folder. See `.env.example` for an example subset of all variables.

- Run `docker-compose up -d postgres`  to start the database after adjusting its settings in `.env`
- Follow the above [Set up](#set-up) and [Intialize Database](#initialize-database) steps for importing data.

- Bring up services with `docker-compose up`. If you are using the example env file, the api can be accessed at http://localhost:8000/api/v1.0/ and clowder at http://localhost:8000/clowder.

To setup clowder, create an account using the `CLOWDER_ADMINS` variable or [follow these instructions](https://github.com/clowder-framework/clowder#initializing-clowder).

The practices extractor  (`bmp.practices_extractor`) status can be monitored at http://localhost:8000/monitor or at http://localhost:8000/clowder/extractors . If it is not there, you might have to wait a bit for Clowder to register the extractor.
