from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models import User, Admin
from app.forms.auth import SignupForm, LoginForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated and isinstance(current_user, User):
        return redirect(url_for("main.home"))
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
            return render_template("auth/signup.html", form=form)
        if form.phone.data and User.query.filter_by(phone=form.phone.data.strip()).first():
            flash("This phone number is already registered.", "danger")
            return render_template("auth/signup.html", form=form)
        user = User(
            full_name=form.full_name.data.strip(),
            email=email,
            phone=(form.phone.data.strip() if form.phone.data else None),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Welcome to Ayan-Optics! Your account is ready.", "success")
        return redirect(url_for("main.home"))
    return render_template("auth/signup.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and isinstance(current_user, User):
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            if not user.is_active_user:
                flash("This account has been disabled. Contact the store.", "danger")
                return render_template("auth/login.html", form=form)
            login_user(user, remember=form.remember.data)
            nxt = request.args.get("next")
            if nxt and nxt.startswith("/") and not nxt.startswith("//"):
                return redirect(nxt)
            return redirect(url_for("main.home"))
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    # Only log out customers here; admins use their own logout
    if isinstance(current_user, User):
        logout_user()
        flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
