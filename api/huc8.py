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

    def serialize(self):
        return {
            "huc8": self.huc8,
            "name": self.name,
            "area_acres": self.area_acres,
            "states": self.states,
        }


def get(huc8_id):
    return helpers.get(HUC8, huc8_id)


def search(page, limit):
    return helpers.search(HUC8, page, limit)
