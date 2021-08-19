import logging
import os

import click
import connexion
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from utils.cli import is_true
from utils.db import Database
from utils.encoders import AlchemyEncoder

# Load environment variables from .env
load_dotenv()


def get_db(host: str, port: str, user: str, password: str, name: str) -> Database:
    return Database(host, port, user, password, name)


@click.group()
@click.option("--debug", is_flag=True, help="env variable: DEBUG")
@click.option(
    "--log",
    type=click.Choice(["DEBUG", "INFO", "WARN", "ERROR"], case_sensitive=False),
    default="INFO",
    help="env variable: API_LOG_LEVEL",
)
@click.option("--db-host", type=str, default="localhost", help="env variable: DB_HOST")
@click.option("--db-port", type=str, default="5432", help="env variable: DB_PORT")
@click.option("--db-name", type=str, default="gltg_bmp", help="env variable: DB_NAME")
@click.option("--db-user", type=str, default="postgres", help="env variable: DB_USER")
@click.option("--db-password", type=str, default="", help="env variable: DB_PASSWORD")
@click.pass_context
def cli(
    ctx,
    debug: bool,
    log: str,
    db_host: str,
    db_port: str,
    db_name: str,
    db_user: str,
    db_password: str,
):
    """All parameters are determined first by their respective environment variable and then by their cli flag."""
    ctx.ensure_object(dict)

    ctx.obj["DEBUG"] = is_true(os.getenv("API_DEBUG", "False")) or debug

    if ctx.obj["DEBUG"]:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    logging.basicConfig(level=getattr(logging, os.getenv("API_LOG_LEVEL", log)))

    ctx.obj["DATABASE"] = {
        "host": os.getenv("DB_HOST", db_host),
        "port": os.getenv("DB_PORT", db_port),
        "name": os.getenv("DB_NAME", db_name),
        "user": os.getenv("DB_USER", db_user),
        "password": os.getenv("DB_PASSWORD", db_password),
    }


@cli.command()
@click.pass_context
def prepare_db(ctx):
    """Import states, HUC8s, and assumptions into the database"""
    db = get_db(**ctx.obj["DATABASE"])
    db.prepare()


@cli.command()
@click.option(
    "--api-context",
    type=str,
    default="/bmp-api",
    help="env variable: API_CONTEXT",
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="env variable: API_PORT",
)
@click.pass_context
def run(ctx, api_context, port):
    """
    Start API Server
    All parameters are determined first by their respective environment variable and then by their cli flag.
    """
    app = connexion.FlaskApp(
        __name__,
        specification_dir="swagger",
        resolver=connexion.resolver.RestyResolver("handlers"),
    )
    app.add_api(
        "v1.0.yaml",
        base_path=os.getenv("API_CONTEXT", api_context),
        strict_validation=True,
        options={"swagger_url": "/docs"},
    )

    flask_app: Flask = app.app
    CORS(flask_app)
    flask_app.json_encoder = AlchemyEncoder

    db = get_db(**ctx.obj["DATABASE"])
    flask_app.db_session = db.get_session()

    @flask_app.teardown_appcontext
    def shutdown_session(exception=None):
        flask_app.db_session = None
        db.shutdown()

    flask_app.env = "development" if ctx.obj["DEBUG"] else "production"
    app.run(
        port=os.getenv("API_PORT", port),
        debug=ctx.obj["DEBUG"],
        use_reloader=ctx.obj["DEBUG"],
        threaded=True,
    )


if __name__ == "__main__":
    cli()
