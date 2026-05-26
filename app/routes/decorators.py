from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """
    Decorator to restrict access to users with specific roles.
    Example: @role_required('staff', 'admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                from app.extensions import login_manager
                return login_manager.unauthorized()
            if current_user.role not in roles:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator
