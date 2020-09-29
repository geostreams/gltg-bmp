from flask.json import jsonify
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import Text
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from api.db import Base


class Practice(Base):
    __tablename__ = "practices"

    id = Column(BigInteger, primary_key=True, index=True)
    huc_8 = Column(Text, ForeignKey("huc8.huc8"))
    huc_12 = Column(Text)
    state = Column(Text, ForeignKey("states.id"))
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

    huc_8_object = relationship("HUC8", backref=backref("practices", lazy=True))

    state_object = relationship("State", backref=backref("practices", lazy=True))

    def serialize(self):
        return {
            "id": self.id,
            "huc_8": self.huc_8,
            "huc_12": self.huc_12,
            "state": self.state,
            "county_code": self.county_code,
            "county": self.county,
            "nrcs_practice_code": self.nrcs_practice_code,
            "practice_name": self.practice_name,
            "program": self.program,
            "fund_code": self.fund_code,
            "applied_amount": self.applied_amount,
            "practice_units": self.practice_units,
            "applied_date": self.applied_date,
            "funding": self.funding,
            "sunset": self.sunset,
            "active_year": self.active_year,
            "category": self.category,
            "wq_benefits": self.wq_benefits,
            "area_treated": self.area_treated,
            "ancillary_benefits": self.ancillary_benefits,
            "p_reduction_fraction": self.p_reduction_fraction,
            "n_reduction_fraction": self.n_reduction_fraction,
            "p_reduction_percentage_statewide": self.p_reduction_percentage_statewide,
            "n_reduction_percentage_statewide": self.n_reduction_percentage_statewide,
            "p_reduction_gom_lbs": self.p_reduction_gom_lbs,
            "n_reduction_gom_lbs": self.n_reduction_gom_lbs,
        }


def get(practice_id):
    return jsonify(Practice.query.get(practice_id).serialize())


def search():
    return jsonify(list(map(lambda x: x.serialize(), Practice.query.all())))
