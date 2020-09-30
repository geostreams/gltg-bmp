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

    def serialize(self):
        return {
            "state": self.id,
            "area_sq_mi": self.area_sq_mi,
            "size_ac": self.size_ac,
            "total_p_load_lbs": self.total_p_load_lbs,
            "total_n_load_lbs": self.total_n_load_lbs,
            "rowcrop_p_yield_lbs_per_ac": self.rowcrop_p_yield_lbs_per_ac,
            "rowcrop_n_yield_lbs_per_ac": self.rowcrop_n_yield_lbs_per_ac,
            "fraction_p": self.fraction_p,
            "fraction_n": self.fraction_n,
            "overall_p_yield_lbs_per_ac": self.overall_p_yield_lbs_per_ac,
            "overall_n_yield_lbs_per_ac": self.overall_n_yield_lbs_per_ac,
        }


def get(state_id):
    return helpers.get(State, state_id)


def search(page, limit):
    return helpers.search(State, page, limit)
