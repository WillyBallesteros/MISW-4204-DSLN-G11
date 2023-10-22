import enum
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy import DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(80), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    source_type = db.Column(db.String(20), nullable=False)
    destination_type = db.Column(db.String(20), nullable=False)
    source_file_system = db.Column(db.String(800), nullable=False)
    destination_file_system = db.Column(db.String(800), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    insert_date = db.Column(db.DateTime, default=datetime.now)
    start_process_date = db.Column(db.DateTime)
    finish_process_date = db.Column(db.DateTime)
    completed_process_date = db.Column(db.DateTime)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    uuid = db.Column(db.String(64), nullable=False)

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        include_relationships = True
        include_fk = True
        load_instance = True