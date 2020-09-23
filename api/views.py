from flask import Blueprint
from flask.json import jsonify

from api.models import Practice, Assumption, HUC8, State

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/assumptions/<string:assumption_id>")
def assumption(assumption_id):
    return jsonify(Assumption.query.get(assumption_id).serialize())


@api.route("/assumptions")
def assumptions():
    return jsonify(list(map(lambda x: x.serialize(), Assumption.query.all())))


@api.route("/huc8/<string:huc8_id>")
def huc8(huc8_id):
    return jsonify(HUC8.query.get(huc8_id).serialize())


@api.route("/huc8")
def huc8s():
    return jsonify(list(map(lambda x: x.serialize(), HUC8.query.all())))


@api.route("/states/<string:state_id>")
def state(state_id):
    return jsonify(State.query.get(state_id).serialize())


@api.route("/states")
def states():
    return jsonify(list(map(lambda x: x.serialize(), State.query.all())))


@api.route("/practices/<int:practice_id>")
def practice(practice_id):
    return jsonify(Practice.query.get(practice_id).serialize())


@api.route("/practices")
def practices():
    return jsonify(list(map(lambda x: x.serialize(), Practice.query.all())))
