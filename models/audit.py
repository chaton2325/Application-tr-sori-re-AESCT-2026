from datetime import datetime
from app import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    action = db.Column(db.String(255))
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    
    user = db.relationship('User', backref='audit_logs_list')
