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

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "dominant_unit": self.dominant_unit,
            "units": self.units,
            "alt_unit_1": self.alt_unit_1,
            "alt_unit_2": self.alt_unit_2,
            "alt_unit_3": self.alt_unit_3,
            "alt_unit_4": self.alt_unit_4,
            "alias_1": self.alias_1,
            "alias_2": self.alias_2,
            "alias_3": self.alias_3,
            "alias_4": self.alias_4,
            "alias_5": self.alias_5,
            "alias_6": self.alias_6,
            "alias_7": self.alias_7,
            "alias_8": self.alias_8,
            "alias_9": self.alias_9,
            "alias_10": self.alias_10,
            "alias_11": self.alias_11,
            "alias_12": self.alias_12,
            "alias_13": self.alias_13,
            "alias_14": self.alias_14,
            "alias_15": self.alias_15,
            "alias_16": self.alias_16,
            "alias_17": self.alias_17,
            "alias_18": self.alias_18,
            "alias_19": self.alias_19,
            "alias_20": self.alias_20,
            "alias_21": self.alias_21,
            "alias_22": self.alias_22,
            "wq": self.wq,
            "wq_benefits": self.wq_benefits,
            "life_span": self.life_span,
            "nitrogen": self.nitrogen,
            "phosphorus": self.phosphorus,
            "cost_share_fraction": self.cost_share_fraction,
            "category": self.category,
            "conv": self.conv,
            "ancillary_benefits": self.ancillary_benefits,
        }


def get(assumption_id):
    return helpers.get(Assumption, assumption_id)


def search(page, limit):
    return helpers.search(Assumption, page, limit)
