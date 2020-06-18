from flask import Blueprint
from flask.json import jsonify

from .models import Practices

bp = Blueprint("practices", __name__, url_prefix="/practices")


@bp.route("/<int:practice_id>")
def get(practice_id):
    return jsonify(Practices.query.get(practice_id).serialize())
