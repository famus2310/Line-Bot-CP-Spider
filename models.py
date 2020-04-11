from app import db

class Contest(db.Model):
    __tablename__ = 'contests'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    link = db.Column(db.String())
    status = db.Column(db.String())

    def __init__(self, title, link, status):
        self.title = title
        self.link = link
        self.status = status
    
    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id, 
            'title': self.title,
            'link': self.link,
            'status': self.status
        }

class Notify(db.Model):
    __tablename__ = 'notifies'

    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String())
    source_id = db.Column(db.String())

    def __init__(self, source_type, source_id):
        self.source_type = source_type
        self.source_id = source_id
    
    def __repr__(self):
        return '<id {} {}>'.format(self.id, self.source_id)

    def serialize(self):
        return {
            'id': self.id, 
            'source_type': self.source_type,
            'source_id': self.source_id
        }
