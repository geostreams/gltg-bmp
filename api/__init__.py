from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from api.utils.import_data import import_data

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    db.init_app(app)
    app.cli.add_command(import_data)

    from api import auth, practices
    app.register_blueprint(auth.bp)
    app.register_blueprint(practices.bp)

    return app
