from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.user import User, Role
from app.models.audit import AuditLog
from app.utils.decorators import admin_required, log_action
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('admin/index.html', users=users, logs=logs)

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
