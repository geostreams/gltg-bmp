from flask import jsonify
from geoalchemy2 import Geometry
from handlers.practices import Practice
from sqlalchemy import Column, Float, Text
from utils import db, query


class HUC8(db.Base):
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
    return jsonify(query.get(HUC8, huc8_id))


def search(page, limit):
    available_huc8s = [
        huc8
        for (huc8,) in Practice.query.session.query(Practice.huc_8)
        .group_by(Practice.huc_8)
        .all()
    ]
    return jsonify(
        query.search(
            model=HUC8,
            page=page,
            limit=limit,
            query_filters_config=[("huc8", "in_", available_huc8s)],
            columns=[HUC8.huc8, HUC8.name, HUC8.area_acres, HUC8.states],
        )
    )
