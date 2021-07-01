from flask import jsonify
from handlers.practices import Practice
from sqlalchemy import Column, Float, Text
from utils import db, query


class State(db.Base):
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
    return jsonify(query.get(State, state_id))


def search(page, limit):
    available_states = [
        state
        for (state,) in Practice.query.session.query(Practice.state)
        .group_by(Practice.state)
        .all()
    ]
    return jsonify(
        query.search(
            model=State,
            page=page,
            limit=limit,
            query_filters_config=[("id", "in_", available_states)],
        )
    )
