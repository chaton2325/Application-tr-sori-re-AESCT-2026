from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user import User
from app.forms.auth import LoginForm, ChangePasswordForm
from app.utils.decorators import log_action
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nom d\'utilisateur ou mot de passe invalide', 'danger')
            return redirect(url_for('auth.login'))
        if not user.active:
            flash('Votre compte est désactivé', 'warning')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        log_action('Connexion')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.index'))
    return render_template('auth/login.html', title='Connexion', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    log_action('Déconnexion')
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        db.session.commit()
        log_action('Changement de mot de passe')
        flash('Votre mot de passe a été mis à jour.', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/change_password.html', title='Changer le mot de passe', form=form)
