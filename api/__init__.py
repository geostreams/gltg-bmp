from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_sqlalchemy.model import BindMetaMixin, Model
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from api.init_db import init_db


class NoNameMeta(BindMetaMixin, DeclarativeMeta):
    pass


db = SQLAlchemy(
    model_class=declarative_base(cls=Model, metaclass=NoNameMeta, name="Model")
)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    db.init_app(app)
    app.cli.add_command(init_db)

    from api import views

    app.register_blueprint(views.api)

    return app
