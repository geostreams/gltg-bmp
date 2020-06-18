from api import db


class Practices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    huc_8 = db.Column(db.String, nullable=False)
    state = db.Column(db.String)
    practice_name = db.Column(db.String)

    def serialize(self):
        return {
            "id": self.id,
            "huc_8": self.huc_8
        }
