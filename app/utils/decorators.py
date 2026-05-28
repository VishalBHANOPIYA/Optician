from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user
from app.models import User, Admin


def user_required(f):
    """Route requires a logged-in customer (not an admin)."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, User):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    """Route requires a logged-in admin. Returns 404 to hide admin area from non-admins."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            abort(404)
        return f(*args, **kwargs)
    return wrapper
