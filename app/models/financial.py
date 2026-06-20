from datetime import datetime
from app import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    type = db.Column(db.String(10)) # 'Income' or 'Expense'
    entries = db.relationship('FinanceEntry', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

class FinanceEntry(db.Model):
    __tablename__ = 'finance_entries'
    id = db.Column(db.Integer, primary_key=True)
    ref = db.Column(db.String(20), unique=True)
    type = db.Column(db.String(10)) # 'Income' or 'Expense'
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    amount = db.Column(db.Numeric(10, 2))
    date = db.Column(db.Date, default=datetime.utcnow().date())
    label = db.Column(db.String(200))
    attachment_path = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

class Cotisation(db.Model):
    __tablename__ = 'cotisations'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    amount_expected = db.Column(db.Numeric(10, 2))
    amount_paid = db.Column(db.Numeric(10, 2))
    date_paid = db.Column(db.Date, default=datetime.utcnow().date())
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

class Cause(db.Model):
    __tablename__ = 'causes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    target_amount = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20), default='Active') # 'Active', 'Closed'
    contributions = db.relationship('Contribution', backref='cause', lazy='dynamic')

class Contribution(db.Model):
    __tablename__ = 'contributions'
    id = db.Column(db.Integer, primary_key=True)
    cause_id = db.Column(db.Integer, db.ForeignKey('causes.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    amount = db.Column(db.Numeric(10, 2))
    date_paid = db.Column(db.Date, default=datetime.utcnow().date())
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
