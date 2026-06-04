from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models import Admin, User
from app.forms.auth import AdminLoginForm

# url_prefix is attached at registration time using ADMIN_SECRET_PATH
admin_auth_bp = Blueprint("admin_auth", __name__)


@admin_auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("main.home"))
    form = AdminLoginForm()
    if form.validate_on_submit():
        username_or_email = form.username.data.strip()
        # 1. Try finding in Admin (by username or email)
        admin = Admin.query.filter((Admin.username == username_or_email) | (Admin.email == username_or_email)).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            admin.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for("admin.dashboard"))
            
        # 2. Try finding in User (by email)
        user = User.query.filter_by(email=username_or_email.lower()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active_user:
                flash("This account has been disabled. Contact the store.", "danger")
                return render_template("admin/login.html", form=form)
            login_user(user)
            return redirect(url_for("main.home"))
            
        flash("Invalid credentials.", "danger")
    return render_template("admin/login.html", form=form)


@admin_auth_bp.route("/logout")
def logout():
    if isinstance(current_user, Admin):
        logout_user()
    return redirect(url_for("admin_auth.login"))
