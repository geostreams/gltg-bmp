from flask import jsonify
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import JSON
from sqlalchemy import or_
from sqlalchemy import Text

from api import helpers
from api.db import Base


class Practice(Base):
    __tablename__ = "practices"

    id = Column(BigInteger, primary_key=True, index=True)
    huc_8 = Column(Text)
    huc_12 = Column(Text)
    state = Column(Text)
    county_code = Column(Text)
    county = Column(Text)
    nrcs_practice_code = Column(Text)
    practice_name = Column(Text)
    program = Column(Text)
    fund_code = Column(Text)
    applied_amount = Column(Float(53))
    practice_units = Column(Text)
    applied_date = Column(BigInteger)
    funding = Column(Float(53))
    sunset = Column(BigInteger)
    active_year = Column(Float(53))
    category = Column(Text)
    wq_benefits = Column(Text)
    area_treated = Column(Float(53))
    ancillary_benefits = Column(JSON)
    p_reduction_fraction = Column(Float(53))
    n_reduction_fraction = Column(Float(53))
    p_reduction_percentage_statewide = Column(Float(53))
    n_reduction_percentage_statewide = Column(Float(53))
    p_reduction_gom_lbs = Column(Float(53))
    n_reduction_gom_lbs = Column(Float(53))


def get(practice_id):
    return jsonify(helpers.get(Practice, practice_id))


def search(page, limit, **filters):
    query_filters_config = {
        "huc8s": ("huc_8", "in_", filters.get("huc8s")),
        "states": ("state", "in_", filters.get("states")),
        "practice_code": ("nrcs_practice_code", "__eq__", filters.get("practice_code")),
        "applied_date": (
            or_,
            (
                ("applied_date", "__ge__", filters.get("applied_date")),
                ("applied_date", "is_", None),
            ),
        ),
        "sunset": (
            or_,
            (("sunset", "__le__", filters.get("sunset")), ("sunset", "is_", None)),
        ),
        "program": ("program", "__eq__", filters.get("program")),
        "min_applied_amount": (
            "applied_amount",
            "__ge__",
            filters.get("min_applied_amount"),
        ),
        "max_applied_amount": (
            "applied_amount",
            "__le__",
            filters.get("max_applied_amount"),
        ),
        "category": ("category", "__eq__", filters.get("category")),
        "wq_benefits": ("wq_benefits", "__eq__", filters.get("wq_benefits")),
        "ancillary_benefits": (
            "ancillary_benefits",
            "__in__",
            filters.get("ancillary_benefits"),
        ),
        "min_area_treated": ("area_treated", "__ge__", filters.get("min_area_treated")),
        "max_area_treated": ("area_treated", "__le__", filters.get("max_area_treated")),
    }

    return jsonify(
        helpers.search(
            Practice,
            page,
            limit,
            [v for k, v in query_filters_config.items() if filters.get(k)],
        )
    )
