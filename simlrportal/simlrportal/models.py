from simlrportal import db

class DataFile(db.Model):
    __tablename__ = "datafiles"
    id = db.Column(db.String(21), primary_key=True)
    name = db.Column(db.String(64))
    owner = db.Column(db.String(64))
    description = db.Column(db.Text)
    modified = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    def __repr__(self):
        return '<file:  {}, path: {}>'.format(self.id, self.path)
