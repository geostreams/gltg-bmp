import logging
import os

import connexion
from dotenv import load_dotenv

from api.db import get_db

# Load environment variables from .env
load_dotenv()
DEBUG = os.getenv("DEBUG", False)

# Logging
logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))

# DB
db_session = get_db(os.getenv("DATABASE_URI"))

# API
app = connexion.FlaskApp(
    __name__,
    specification_dir="swagger",
    resolver=connexion.resolver.RestyResolver("api"),
)
app.add_api("v1.0.yaml", strict_validation=True, options={"swagger_url": "/docs"})

application = app.app


@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    app.run(port=os.getenv("PORT", 8000), use_reloader=DEBUG, threaded=True)
