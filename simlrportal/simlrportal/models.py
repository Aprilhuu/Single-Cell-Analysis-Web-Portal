from simlrportal import db

class DataFile(db.Model):
    __tablename__ = "datafiles"
    id = db.Column(db.String(64), primary_key=True)
    source = db.Column(db.String(10))
    name = db.Column(db.String(64))
    owner = db.Column(db.String(64))
    description = db.Column(db.Text)
    modified = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    def __repr__(self):
        return '<file:  {} time: {}>'.format(self.id, self.modified)

    def to_dict(self):
        dict_ = {
            'id': self.id,
            'source': self.source,
            'name': self.name,
            'owner': self.owner,
            'description': self.description,
            'modified':self.modified.strftime("%m/%d/%Y %H:%M:%S")
        }
        return dict_
