import functools
import json

from flask import Blueprint
from flask import g
from flask import request
from flask import session
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .models import Users

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return "Log in is required", 403

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = Users.query.get(id=user_id).serialize()


@bp.route("/login", methods=("POST",))
def login():
    """Log in a registered user by adding the user id to the session."""
    data = json.loads(request.data)
    email = data["email"]
    password = data["password"]
    error = None
    user = Users.query.get(email)

    if user is None:
        error = "Incorrect username."
    elif not check_password_hash(user.password, password):
        error = "Incorrect password."

    if error is None:
        # store the user id in a new session and return to the index
        session.clear()
        session["user_id"] = user.id
        return "token"

    return error, 403
