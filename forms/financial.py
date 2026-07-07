from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, TextAreaField, SelectField, SubmitField, DateField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Optional

class CotisationForm(FlaskForm):
    member_id = SelectField('Adhérent', coerce=int, validators=[DataRequired()])
    month = SelectField('Mois', coerce=int, choices=[(i, str(i)) for i in range(1, 13)], validators=[DataRequired()])
    year = IntegerField('Année', default=2024, validators=[DataRequired()])
    amount_expected = DecimalField('Montant attendu', default=20.0, validators=[DataRequired()])
    amount_paid = DecimalField('Montant versé', validators=[DataRequired()])
    date_paid = DateField('Date du versement', validators=[DataRequired()])
    notes = TextAreaField('Observation')
    submit = SubmitField('Enregistrer')

class CauseForm(FlaskForm):
    name = StringField('Nom de la cause', validators=[DataRequired()])
    description = TextAreaField('Description')
    start_date = DateField('Date de début', validators=[DataRequired()])
    end_date = DateField('Date de fin', validators=[DataRequired()])
    target_amount = DecimalField('Objectif financier', validators=[DataRequired()])
    status = SelectField('Statut', choices=[('Active', 'Active'), ('Closed', 'Clôturée')])
    submit = SubmitField('Enregistrer')

class ContributionForm(FlaskForm):
    cause_id = SelectField('Cause', coerce=int, validators=[DataRequired()])
    member_id = SelectField('Adhérent', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Montant', validators=[DataRequired()])
    date_paid = DateField('Date', validators=[DataRequired()])
    notes = TextAreaField('Observation')
    submit = SubmitField('Enregistrer')

class FinanceEntryForm(FlaskForm):
    type = SelectField('Type', choices=[('Income', 'Entrée'), ('Expense', 'Sortie')], validators=[DataRequired()])
    category_id = SelectField('Catégorie', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Montant', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    label = StringField('Libellé', validators=[DataRequired()])
    attachment = FileField('Justificatif (PDF, JPG, PNG)', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png', 'jpeg'], 'Fichiers autorisés: PDF, JPG, PNG')])
    submit = SubmitField('Enregistrer')
