from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models.user import User, Role
from models.audit import AuditLog
from utils.decorators import admin_required, log_action
from app import db
from forms.auth import RegistrationForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('admin/index.html', users=users, logs=logs)

@admin_bp.route('/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = RegistrationForm()
    form.role_id.choices = [(role.id, role.name) for role in Role.query.all()]
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role_id=form.role_id.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        log_action(f'Utilisateur {user.username} créé')
        flash(f'Utilisateur {user.username} créé avec succès', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/add_user.html', title='Ajouter un utilisateur', form=form)

@admin_bp.route('/user/toggle/<int:id>')
@login_required
@admin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    if user.username == 'admin':
        flash('Impossible de désactiver le super administrateur par défaut', 'danger')
        return redirect(url_for('admin.index'))
    user.active = not user.active
    db.session.commit()
    log_action(f'Statut utilisateur {user.username} changé en {"Actif" if user.active else "Inactif"}')
    flash(f'Utilisateur {user.username} mis à jour', 'success')
    return redirect(url_for('admin.index'))
