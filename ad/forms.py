from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class ProcessImage(FlaskForm):
    logo_name = StringField(label='Logo Name:')
    ad_message = StringField(label='Ad Message:')
    submit = SubmitField(label='Submit')