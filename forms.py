from wtforms import TextField, BooleanField
from wtforms.validators import Required
from flask.ext.wtf import Form, widgets, SelectMultipleField

class FormBase(Form):
    dummy = ''