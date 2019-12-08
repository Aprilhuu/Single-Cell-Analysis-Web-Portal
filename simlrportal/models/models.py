from simlrportal import db

class DataFile(db.Model):
    __tablename__ = "datafiles"
    id = db.Column(db.String(64), primary_key=True)
    path = db.Column(db.String(64))
    source = db.Column(db.String(10))
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    modified = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    def __repr__(self):
        return '<file:  {} time: {}>'.format(self.id, self.modified)

    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'name': self.name,
            'path': self.path,
            'description': self.description,
            'modified':self.modified.strftime("%m/%d/%Y %H:%M:%S")
        }



class Process(db.Model):
    __tablename__ = "processes"
    id = db.Column(db.String(32), primary_key=True)
    index = db.Column(db.Integer, primary_key=True)
    call = db.Column(db.Text)
    status = db.Column(db.Integer)
    time = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    output = db.Column(db.Text)

    def __repr__(self):
        return '<id: {} index: {} call: {}>'.format(self.id, self.index, self.call)

    def to_dict(self):
        return {
            'id': self.id,
            'index': self.index,
            'call': self.call,
            'status': self.status,
            'time': self.time.strftime("%m/%d/%Y %H:%M:%S"),
            'output': self.output
        }


class WorkerRecord(db.Model):
    """Stores information for the worker"""

    __tablename__ = "worker"
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(32))
    status = db.Column(db.Integer)
    time = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    curr = db.Column(db.Integer)
    total = db.Column(db.Integer)

    def __repr__(self):
        return '<id: {} current: {}>'.format(self.id, self.curr)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'time': self.time.strftime("%m/%d/%Y %H:%M:%S"),
            'curr' : self.curr,
            'total': self.total
        }
