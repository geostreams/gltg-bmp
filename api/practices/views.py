from flask import Blueprint
from flask.json import jsonify

from .models import Practices

bp = Blueprint("practices", __name__, url_prefix="/practices")


@bp.route("/meta")
def meta():
    return jsonify({})


@bp.route("/<int:practice_id>")
def practices(practice_id):
    return jsonify(Practices.query.get(practice_id).serialize())
