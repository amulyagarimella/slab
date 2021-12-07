from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FieldList, FormField
from wtforms.validators import *
from flask_wtf import *

# Registration form
class RegistrationForm(FlaskForm):
	name = StringField('Name',[Length(min=1, max=25)])
	username = StringField('Username',[Length(min=1, max=25)])
	password = PasswordField('Password',[Length(min=1, max=15)])
	confirm = PasswordField('Password confirmation',[Length(min=1, max=15), EqualTo('password', message="Passwords must match.")])
	submit = SubmitField('Register') 

# Login form
class LoginForm(FlaskForm):
	username = StringField('Username',[Length(min=1, max=25)])
	password = PasswordField('Password',[Length(min=1, max=15)])
	submit = SubmitField('Log in') 

# Add lab protocols
class ProtocolSubmission(FlaskForm):
	title = StringField('Title',[Length(min=1, max=120)])
	text = TextAreaField('Protocol',[InputRequired(message="Protocol cannot be empty.")])
	submit = SubmitField('Submit') 

# Edit protocols

# Individual step editor
class StepEditor(FlaskForm):
	text = TextAreaField('Step',[InputRequired(message="Step cannot be empty.")])
	note = TextAreaField('Note')
	time_taken = StringField('Time Taken')

# Entire protocol editor - made up of several step editors
class ProtocolEditor(FlaskForm):
	title = StringField('Title',[Length(min=1, max=120)])
	steps = FieldList(FormField(StepEditor), min_entries=0)
	submit = SubmitField('Save') 
