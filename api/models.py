from geoalchemy2 import Geometry

from api import db


class Practice(db.Model):
    __tablename__ = "practices"

    id = db.Column(db.BigInteger, primary_key=True, index=True)
    huc_8 = db.Column(db.Text, db.ForeignKey("huc8.huc8"))
    huc_12 = db.Column(db.Text)
    state = db.Column(db.Text, db.ForeignKey("states.id"))
    county_code = db.Column(db.Text)
    county = db.Column(db.Text)
    nrcs_practice_code = db.Column(db.Text)
    practice_name = db.Column(db.Text)
    program = db.Column(db.Text)
    fund_code = db.Column(db.Text)
    applied_amount = db.Column(db.Float(53))
    practice_units = db.Column(db.Text)
    applied_date = db.Column(db.BigInteger)
    funding = db.Column(db.Float(53))
    sunset = db.Column(db.BigInteger)
    active_year = db.Column(db.Float(53))
    category = db.Column(db.Text)
    wq_benefits = db.Column(db.Text)
    area_treated = db.Column(db.Float(53))
    ancillary_benefits = db.Column(db.JSON)
    p_reduction_fraction = db.Column(db.Float(53))
    n_reduction_fraction = db.Column(db.Float(53))
    p_reduction_percentage_statewide = db.Column(db.Float(53))
    n_reduction_percentage_statewide = db.Column(db.Float(53))
    p_reduction_gom_lbs = db.Column(db.Float(53))
    n_reduction_gom_lbs = db.Column(db.Float(53))

    huc_8_object = db.relationship("HUC8", backref=db.backref("practices", lazy=True))

    state_object = db.relationship("State", backref=db.backref("practices", lazy=True))

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


class Assumption(db.Model):
    __tablename__ = "assumptions"

    id = db.Column(db.Text, primary_key=True, index=True)
    name = db.Column(db.Text)
    url = db.Column(db.Text)
    dominant_unit = db.Column(db.Text)
    units = db.Column(db.Text)
    alt_unit_1 = db.Column(db.Text)
    alt_unit_2 = db.Column(db.Text)
    alt_unit_3 = db.Column(db.Text)
    alt_unit_4 = db.Column(db.Text)
    alias_1 = db.Column(db.Text)
    alias_2 = db.Column(db.Text)
    alias_3 = db.Column(db.Text)
    alias_4 = db.Column(db.Text)
    alias_5 = db.Column(db.Text)
    alias_6 = db.Column(db.Text)
    alias_7 = db.Column(db.Text)
    alias_8 = db.Column(db.Text)
    alias_9 = db.Column(db.Text)
    alias_10 = db.Column(db.Text)
    alias_11 = db.Column(db.Text)
    alias_12 = db.Column(db.Text)
    alias_13 = db.Column(db.Text)
    alias_14 = db.Column(db.Text)
    alias_15 = db.Column(db.Text)
    alias_16 = db.Column(db.Text)
    alias_17 = db.Column(db.Text)
    alias_18 = db.Column(db.Text)
    alias_19 = db.Column(db.Text)
    alias_20 = db.Column(db.Text)
    alias_21 = db.Column(db.Text)
    alias_22 = db.Column(db.Text)
    wq = db.Column(db.BigInteger)
    wq_benefits = db.Column(db.JSON)
    life_span = db.Column(db.JSON)
    nitrogen = db.Column(db.JSON)
    phosphorus = db.Column(db.JSON)
    cost_share_fraction = db.Column(db.JSON)
    category = db.Column(db.JSON)
    conv = db.Column(db.JSON)
    ancillary_benefits = db.Column(db.JSON)

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


class HUC8(db.Model):
    __tablename__ = "huc8"

    huc8 = db.Column(db.Text, primary_key=True, index=True)
    name = db.Column(db.Text)
    area_acres = db.Column("areaacres", db.Float(53))
    states = db.Column(db.Text)
    geometry = db.Column(
        Geometry("MULTIPOLYGON", 4326, from_text="ST_GeomFromEWKT", name="geometry"),
        index=True,
    )

    def serialize(self):
        return {
            "huc8": self.huc8,
            "name": self.name,
            "area_acres": self.area_acres,
            "states": self.states,
        }


class State(db.Model):
    __tablename__ = "states"

    id = db.Column(db.Text, primary_key=True, index=True)
    area_sq_mi = db.Column(db.Float(53))
    size_ac = db.Column(db.Float(53))
    total_p_load_lbs = db.Column(db.Float(53))
    total_n_load_lbs = db.Column(db.Float(53))
    rowcrop_p_yield_lbs_per_ac = db.Column(db.Float(53))
    rowcrop_n_yield_lbs_per_ac = db.Column(db.Float(53))
    fraction_p = db.Column(db.Float(53))
    fraction_n = db.Column(db.Float(53))
    overall_p_yield_lbs_per_ac = db.Column(db.Float(53))
    overall_n_yield_lbs_per_ac = db.Column(db.Float(53))

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
