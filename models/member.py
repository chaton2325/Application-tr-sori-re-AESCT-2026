from datetime import datetime
from app import db

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(64), index=True)
    first_name = db.Column(db.String(64), index=True)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    address = db.Column(db.Text)
    join_date = db.Column(db.Date, default=datetime.utcnow().date())
    active = db.Column(db.Boolean, default=True)
    
    cotisations = db.relationship('Cotisation', backref='member', lazy='dynamic')
    contributions = db.relationship('Contribution', backref='member', lazy='dynamic')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<Member {self.full_name}>'
