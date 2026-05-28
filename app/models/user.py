from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wishlist_items = db.relationship("Wishlist", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    inquiries = db.relationship("Inquiry", backref="user", cascade="all, delete-orphan", lazy="dynamic")

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    def get_id(self):
        return f"user-{self.id}"

    def __repr__(self):
        return f"<User {self.email}>"


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_super = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    def get_id(self):
        return f"admin-{self.id}"

    def __repr__(self):
        return f"<Admin {self.username}>"


@login_manager.user_loader
def load_user(composite_id):
    """Composite IDs let User and Admin share Flask-Login without collision."""
    try:
        kind, raw_id = composite_id.split("-", 1)
        raw_id = int(raw_id)
    except (ValueError, AttributeError):
        return None
    if kind == "user":
        return User.query.get(raw_id)
    if kind == "admin":
        return Admin.query.get(raw_id)
    return None
