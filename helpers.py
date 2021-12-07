from functools import wraps
from flask import flash, g, request, redirect, url_for
import datetime
from tzlocal import get_localzone
import pytz

# Helper to flash WTForms validation errors in the message flashing area
# Takes a form as input
# Adapted from https://stackoverflow.com/questions/13585663/flask-wtfform-flash-does-not-display-errors (I changed it a bit)
def flash_errors(form):
	# Get all the errors in the form and flash them
	for field, errors in form.errors.items():
		for error in errors:
			# The replace statement just makes the errors more readable
			flash(f"{error}".replace("Field",getattr(form, field).label.text), 'error')

# Convert timezone of datetime object from UTC to local timezone 
def tzconvert(value):
	return value.replace(tzinfo=pytz.utc).astimezone(get_localzone())