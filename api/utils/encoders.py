import json

from flask import current_app
from sqlalchemy import func
from sqlalchemy.ext.declarative import DeclarativeMeta


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # A SQLAlchemy class
            fields = {}
            for field in [
                x for x in dir(obj) if not x.startswith("_") and x != "metadata"
            ]:
                data = obj.__getattribute__(field)

                # If column is geometry, serialize it as geojson
                if (
                    field in obj.__table__.c
                    and hasattr(obj.__table__.c[field].type, "name")
                    and obj.__table__.c[field].type.name == "geometry"
                ):
                    fields[field] = json.loads(
                        current_app.db_session.scalar(func.ST_AsGeoJSON(data))
                    )
                else:
                    try:
                        json.dumps(
                            data
                        )  # this will fail on non-encodable values, like other classes
                        fields[field] = data
                    except TypeError:
                        fields[field] = None
            # A json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)
