import json
import logging
import os

import connexion
from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import func
from sqlalchemy.ext.declarative import DeclarativeMeta

from api.db import get_db

# Load environment variables from .env
load_dotenv()
DEBUG = os.getenv("DEBUG", False)

# Logging
logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
if DEBUG:
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# DB
db_session = get_db(os.getenv("DATABASE_URI"))

# API
app = connexion.FlaskApp(
    __name__,
    specification_dir="swagger",
    resolver=connexion.resolver.RestyResolver("api"),
)
app.add_api("v1.0.yaml", strict_validation=True, options={"swagger_url": "/docs"})

application: Flask = app.app


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # A SQLAlchemy class
            fields = {}
            for field in [
                x for x in dir(obj) if not x.startswith("_") and x != "metadata"
            ]:
                data = obj.__getattribute__(field)

                # If column is geometry, serialize it as geojson
                if (
                    field in obj.__table__.c
                    and hasattr(obj.__table__.c[field].type, "name")
                    and obj.__table__.c[field].type.name == "geometry"
                ):
                    fields[field] = json.loads(
                        db_session.scalar(func.ST_AsGeoJSON(data))
                    )
                else:
                    try:
                        json.dumps(
                            data
                        )  # this will fail on non-encodable values, like other classes
                        fields[field] = data
                    except TypeError:
                        fields[field] = None
            # A json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


application.json_encoder = AlchemyEncoder


@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    app.run(port=os.getenv("PORT", 8000), use_reloader=DEBUG, threaded=True)
