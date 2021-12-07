import os
import datetime
import pytz
from flask import Flask, flash, render_template, request, session, redirect, url_for
from models import *
from helpers import *
from forms import *
from werkzeug.exceptions import HTTPException

# Configuring our app and database
app = Flask(__name__)
app.app_context().push()
db.init_app(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# Tmplates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Link to databse
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

# Configuring our login manager
login_manager = flask_login.LoginManager()
# This will let us redirect unauthorized views to the login screen
login_manager.login_view = 'login'
login_manager.init_app(app)
# Configure user loader
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)

# Add our custom time-zone filter to our app
app.add_template_filter(tzconvert)

# Before the first request, generate the database
# Help: https://stackoverflow.com/questions/44941757/sqlalchemy-exc-operationalerror-sqlite3-operationalerror-no-such-table
@app.before_first_request
def create_tables():
	db.drop_all()
	db.create_all()

# Homepage
@app.route('/index')
@app.route('/')
def index():
	return render_template('index.html')

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
	# Log the user out first
	flask_login.logout_user()
	# Create a new RegistrationForm object with the form data (blank if a GET request)
	form = RegistrationForm(request.form)
	# If the form was submitted via a POST request and all the validators check out (i.e. no validation errors)
	if form.validate_on_submit():
		# Get data from the form
		name = form.name.data
		username = form.username.data.lower()
		# Make sure username is unique (we check for this to allow message flashing and avoid redirect to error page)
		users = User.query.filter_by(username=username).all()
		if len(users) != 0:
			flash("That username is taken.")
			return redirect('/register')
		# Generate a hash for the password
		password = generate_password_hash(str(form.password.data))
		# Create a new User object; add to database
		new_user = User(name, username, password)
		db.session.add(new_user)
		db.session.commit()			
		flash('Registration successful!')
		return redirect('/login')
	else:
		# If there were validation errors, flash these
		flash_errors(form)
	return render_template('register.html', form=form)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	# First, log the user out
	flask_login.logout_user()
	# Create a new login form with the form data (blank if a GET request)
	form = LoginForm(request.form)
	# If the form was submitted via a POST request and all the validators check out (i.e. no validation errors)
	if form.validate_on_submit():
		# Get data from form
		username = form.username.data.lower()
		password = str(form.password.data)
		# Check to make sure username exists
		user = User.query.filter_by(username=username).first()
		if user == None:
			flash("That username isn't in our records, try again.")
			return redirect('/login')
		# Check password
		if user.verify_password(password):
			# log user in
			flask_login.login_user(user)
			flash('Login successful!')
			return redirect('/index')
		else:
			flash("Incorrect password, try again.")
			return redirect('/login')
	else:
		# If there were validation errors, flash these
		flash_errors(form)
	return render_template('login.html', form=form)

# Logout
@app.route('/logout')
@flask_login.login_required
def logout():
	# Log user out; redirect to homepage
	flask_login.logout_user()
	flash("Logout successful.")
	return redirect('/index')

# New protocol page
@app.route('/new', methods=['GET', 'POST'])
@flask_login.login_required
def new():
	# Create a new protocol submission form with the data from the form
	form = ProtocolSubmission(request.form)
	# if the form was submitted via POST request and all the validators check out
	if form.validate_on_submit():
		# Get data from form, create a new Protocol object, add to database
		title = form.title.data
		prot = form.text.data
		new_protocol = Protocol(title)
		print(new_protocol)
		db.session.add(new_protocol)
		db.session.commit()
		p_id = new_protocol.id
		# Parse input and create new steps
		steps = prot.split("\r\n")
		# Create new step object
		for s in steps:
			new_step = Step(p_id, s)
			db.session.add(new_step)
			db.session.commit()
		# go to editing page
		flash("Protocol created!")
		return redirect(url_for('edit', p_id=p_id))
	else:
		# Flash any validation errors
		flash_errors(form)
	return render_template('new.html', form=form)

# Protocol editing page
# Takes ID of protocol as a URL parameter
@app.route('/edit/<p_id>', methods=['GET', 'POST'])
@flask_login.login_required
def edit(p_id):
	# Finds the protocol matching passed ID + child steps
	protocol = Protocol.query.filter_by(id=p_id).first()
	step_list = Step.query.filter_by(p_id=p_id).all()
	# Create a new protocol editing form... but don't add any data just yet because we do different things depending on the type of request
	form = ProtocolEditor()
	if request.method == 'GET':
		# If it's a GET request — i.e. the user clicked on a link to get here — populate the form with the existing protocol and step data
		form.title.data = protocol.title
		for i in range(len(step_list)):
			form.steps.append_entry(vars(step_list[i]))
	elif form.validate_on_submit():
		# If it's a POST request and validation checks pass, get the new data from the form and use it to update protocol and step objects
		protocol.title = form.title.data
		protocol.time_updated = datetime.datetime.now(tz=pytz.utc)
		for i in range(len(step_list)):
			step_list[i].text = form.steps[i].text.data
			step_list[i].note = form.steps[i].note.data
			step_list[i].time_taken = form.steps[i].time_taken.data
		db.session.commit()
		flash("Protocol saved!")
		return redirect('/index')
	else:
		# Flash validation errors
		flash_errors(form)
	return render_template('/edit.html', form=form, protocol = protocol, steps = step_list)

# Protocol view page
@app.route('/protocols')
@flask_login.login_required
def view():
	# Get a list of the user's protocols and pass to the template!
	protocol_list = Protocol.query.filter_by(u_id=flask_login.current_user.id).all()
	return render_template('/protocols.html', protocols = protocol_list)

# Error handler
@app.errorhandler(HTTPException)
def handle_bad_request(e):
	# Display error page
    return render_template('/error.html', e=str(e))