## A Clowder Extractor for processing BMP data

### How to run

You can adjust the variables for docker services in a `.env` file in the root folder. See `.env.example` for an example subset of all variables.

Bring up services with `docker-compose up` and access Clowder on port 8000 ad then create an account for the admin specified in the `CLOWDER_ADMINS` variable.

After signing in as an admin, you should see `bmp_data_extractor` in the list of extractors at `http://localhost:8000/extractors`.
If it is not there, you might have to wait a bit for Clowder to register the extractor.
