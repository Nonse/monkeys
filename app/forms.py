from flask_wtf import Form
from wtforms import StringField#, EmailField
from wtforms.validators import *

class CreateMonkeyForm(Form):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
