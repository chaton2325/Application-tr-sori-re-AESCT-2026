from functools import wraps
from flask import abort, request
from flask_login import current_user
from app.models.audit import AuditLog
from app import db

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            
            role = current_user.role.name
            
            if role == 'Super Administrateur':
                return f(*args, **kwargs)
            
            if permission == 'admin':
                abort(403)
            
            if role == 'Utilisateur Standard':
                # Standard can do everything except admin tasks
                return f(*args, **kwargs)
            
            if role in ['Utilisateur Lecture Seule', 'Simple Invité']:
                if permission == 'read':
                    return f(*args, **kwargs)
                else:
                    abort(403)
            
            abort(403)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required('admin')(f)

def log_action(action, old_value=None, new_value=None):
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        ip_address=request.remote_addr,
        action=action,
        old_value=str(old_value) if old_value else None,
        new_value=str(new_value) if new_value else None
    )
    db.session.add(log)
    db.session.commit()
