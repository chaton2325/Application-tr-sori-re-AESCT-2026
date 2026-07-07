from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models.user import User
from flask_login import current_user

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    role_id = SelectField('Rôle', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Enregistrer')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Ancien mot de passe', validators=[DataRequired()])
    new_password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer le nouveau mot de passe', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Changer le mot de passe')

    def validate_old_password(self, old_password):
        if not current_user.check_password(old_password.data):
            raise ValidationError('L\'ancien mot de passe est incorrect.')
