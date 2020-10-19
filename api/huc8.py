from flask import jsonify
from geoalchemy2 import Geometry
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Text

from api import helpers
from api.db import Base


class HUC8(Base):
    __tablename__ = "huc8"

    huc8 = Column(Text, primary_key=True, index=True)
    name = Column(Text)
    area_acres = Column("areaacres", Float(53))
    states = Column(Text)
    geometry = Column(
        Geometry("MULTIPOLYGON", 4326, from_text="ST_GeomFromEWKT", name="geometry"),
        index=True,
    )


def get(huc8_id):
    return jsonify(helpers.get(HUC8, huc8_id))


def search(page, limit):
    return jsonify(
        helpers.search(
            HUC8, page, limit, [], [HUC8.huc8, HUC8.name, HUC8.area_acres, HUC8.states]
        )
    )
