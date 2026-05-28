from flask import Flask, render_template
from .config import Config
from .extensions import db, migrate, login_manager, csrf
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import models  # noqa: F401
    from .models import User, Wishlist

    # Public + customer routes
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.catalog import catalog_bp
    from .routes.account import account_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(account_bp, url_prefix="/account")

    # Hidden admin routes behind the secret path from .env
    secret = app.config["ADMIN_SECRET_PATH"].strip("/")
    from .routes.admin_auth import admin_auth_bp
    from .routes.admin import admin_bp
    app.register_blueprint(admin_auth_bp, url_prefix=f"/{secret}")
    app.register_blueprint(admin_bp, url_prefix=f"/{secret}")

    @app.context_processor
    def inject_globals():
        return {"SHOP_NAME": "Ayan-Optics", "SHOP_PHONE": "098262 18888"}

    @app.context_processor
    def inject_wishlist():
        ids = set()
        from flask_login import current_user
        if current_user.is_authenticated and isinstance(current_user, User):
            ids = {w.product_id for w in current_user.wishlist_items.all()}
        return {"wishlist_ids": ids}

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    return app

