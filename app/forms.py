from flask_wtf import Form
from wtforms import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import *

class CreateMonkeyForm(Form):
    name = StringField('name', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])

class EditMonkeyForm(Form):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
