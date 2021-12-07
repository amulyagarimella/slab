from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import flask_login
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Create our database
db = SQLAlchemy()

# User table (represented by a Python class)
class User(db.Model, flask_login.UserMixin):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), unique=False, nullable=False)
	username = db.Column(db.String(50), unique=True, nullable=False)
	password = db.Column(db.String(50), unique=False, nullable=False)

	# Each User can have unlimited associated Protocols which in turn can have unlimited associated Steps
	# User is associated with both Protocol and Step objects
	children = relationship('Protocol')
	children = relationship('Step')

	# Initialize
	def __init__(self, name, username, password):
		self.name = name
		self.username = username
		self.password = password

	# Representation in command line
	def __repr__(self):
		return f'<User {self.username}; ID {self.id}>'

	# Check passed password hash against stored password hash
	def verify_password(self, pwd):
		return check_password_hash(self.password, pwd)

# Protocol table (represented by a Python class)
class Protocol(db.Model):
	__tablename__ = 'protocol'
	id = db.Column(db.Integer, primary_key=True)
	u_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	title = db.Column(db.String(120), unique=False, nullable=False)
	time_created = db.Column(DateTime(timezone=True), default=func.now())
	time_updated = db.Column(DateTime(timezone=True), default=func.now())

	# Each Protocol can have unlimited associated Steps
	children = relationship('Step')

	# Initialize - time_created and time_updated initialized by default
	def __init__(self, title):
		self.u_id = flask_login.current_user.id
		self.title = title
		self.time_updated = self.time_created

	# Representation in command line
	def __repr__(self):
		return f'<Protocol {self.title}; ID {self.id}; by user ID {self.u_id}>'

class Step(db.Model):
	__tablename__ = 'step'
	id = db.Column(db.Integer, primary_key=True)
	u_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	p_id = db.Column(db.Integer, db.ForeignKey('protocol.id'))
	text = db.Column(db.Text, unique=False, nullable=False)
	note = db.Column(db.Text, unique=False, nullable=True)
	time_taken = db.Column(db.Text, unique=False, nullable=True)

	# Initialize - note and time_taken are null by default since user doesn't add notes or time taken immediately upon creating a new protocol
	def __init__(self, protocol, text):
		self.u_id = flask_login.current_user.id
		self.p_id = protocol
		self.text = text

	# Representation in command line
	def __repr__(self):
		return f'<Step in Protocol {self.p_id}, by user ID {self.u_id}: {self.text}>'