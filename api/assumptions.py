from flask import jsonify
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import JSON
from sqlalchemy import Text

from api import helpers
from api.db import Base


class Assumption(Base):
    __tablename__ = "assumptions"

    id = Column(Text, primary_key=True, index=True)
    name = Column(Text)
    url = Column(Text)
    dominant_unit = Column(Text)
    units = Column(Text)
    alt_unit_1 = Column(Text)
    alt_unit_2 = Column(Text)
    alt_unit_3 = Column(Text)
    alt_unit_4 = Column(Text)
    alias_1 = Column(Text)
    alias_2 = Column(Text)
    alias_3 = Column(Text)
    alias_4 = Column(Text)
    alias_5 = Column(Text)
    alias_6 = Column(Text)
    alias_7 = Column(Text)
    alias_8 = Column(Text)
    alias_9 = Column(Text)
    alias_10 = Column(Text)
    alias_11 = Column(Text)
    alias_12 = Column(Text)
    alias_13 = Column(Text)
    alias_14 = Column(Text)
    alias_15 = Column(Text)
    alias_16 = Column(Text)
    alias_17 = Column(Text)
    alias_18 = Column(Text)
    alias_19 = Column(Text)
    alias_20 = Column(Text)
    alias_21 = Column(Text)
    alias_22 = Column(Text)
    wq = Column(BigInteger)
    wq_benefits = Column(JSON)
    life_span = Column(JSON)
    nitrogen = Column(JSON)
    phosphorus = Column(JSON)
    cost_share_fraction = Column(JSON)
    category = Column(JSON)
    conv = Column(JSON)
    ancillary_benefits = Column(JSON)


def get(assumption_id):
    return jsonify(helpers.get(Assumption, assumption_id))


def search(page, limit):
    return jsonify(helpers.search(Assumption, page, limit))
