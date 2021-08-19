## GLTG BMP

This package contains an API application that serves the BMP data, and a Clowder extractor that updates the database
used by the API with the BMP Sheets added to datasets in Clowder.

You can run the API either directly or with docker. It is recommended to run Clowder and the BMP extractor with docker.

### Common setup

- Copy `.env-example` to `.env` and adjust the config variables for your environment.
- Download the HUC8 GeoDatabase from ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/WBD/National/GDB/
  and unzip the GDB file in `data/WBD_National_GDB`.

### Development setup

- Install the libraries in `requirements/dev.txt`.
- Run `pre-commit install` to set up the git hooks for the project.

### Run the AI directly

- Create a new Postgres database and install postgis on it.
  Make sure to set `DB_NAME` environment variable to the database you create.
  > The app might work with older versions of PostgreSQL, but it is only tested with version 13.
- Install the following requirements:
  - `requirements/api.txt` for the api
  - `requirements/extractor.txt` for the Clowder extractor
- Run `python api/app.py prepare-db` to load assumptions, states, and huc8 data into the database.
- Run `python api/app.py run` to start the API server. The server starts at `localhost:8000/bmp-api` by default.
  > You can see a list of all available options for the API server by running `python api/app.py --help`.

### Run with docker and docker-compose

- Start the services by running `docker-compose up -d`. It might take a while for all the services to start
  and the extractor to register with rabbitmq. The default port is 8080 and all the routes are handles by traefik.
  Here is the list of default routes, which can be changed via environment variables.
  - API: `/bmp-api`
  - Clowder: `/clowder`
  - Clowder monitor: `/monitor/`
- Run `docker-compose exec bmp_api python api/app.py prepare-db` to load
  assumptions, states, and huc8 data into the database.
