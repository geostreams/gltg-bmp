from flask import jsonify
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Text

from api import helpers
from api.db import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Text, primary_key=True, index=True)
    area_sq_mi = Column(Float(53))
    size_ac = Column(Float(53))
    total_p_load_lbs = Column(Float(53))
    total_n_load_lbs = Column(Float(53))
    rowcrop_p_yield_lbs_per_ac = Column(Float(53))
    rowcrop_n_yield_lbs_per_ac = Column(Float(53))
    fraction_p = Column(Float(53))
    fraction_n = Column(Float(53))
    overall_p_yield_lbs_per_ac = Column(Float(53))
    overall_n_yield_lbs_per_ac = Column(Float(53))


def get(state_id):
    return jsonify(helpers.get(State, state_id))


def search(page, limit):
    return jsonify(helpers.search(State, page, limit))
