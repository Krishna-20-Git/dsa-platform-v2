from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize database
db = SQLAlchemy()

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # Relationship to track progress
    progress = db.relationship('UserProgress', backref='student', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"

# Progress Model
class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Progress('{self.module_name}')"