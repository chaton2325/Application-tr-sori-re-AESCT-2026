from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Optional

class MemberForm(FlaskForm):
    last_name = StringField('Nom', validators=[DataRequired()])
    first_name = StringField('Prénom', validators=[DataRequired()])
    phone = StringField('Téléphone')
    email = StringField('Email', validators=[Optional(), Email()])
    address = TextAreaField('Adresse')
    join_date = DateField('Date d\'adhésion', validators=[DataRequired()])
    active = BooleanField('Actif', default=True)
    submit = SubmitField('Enregistrer')
