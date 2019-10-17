from simlrportal import db

class DataFile(db.Model):
    __tablename__ = "datafiles"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64))
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    owner = db.Column(db.String(64))
    created = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    modified = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    def __repr__(self):
        return '<file:  {}>'.format(self.filename)
