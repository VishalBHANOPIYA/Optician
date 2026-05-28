from datetime import datetime
from app.extensions import db


class Wishlist(db.Model):
    __tablename__ = "wishlist"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "product_id", name="uq_user_product_wishlist"),)


class Inquiry(db.Model):
    """A 'Reserve at Store' or contact request. Replaces the cart since there is no delivery."""
    __tablename__ = "inquiries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)

    # For guest inquiries (no account required)
    guest_name = db.Column(db.String(120))
    guest_phone = db.Column(db.String(20))
    guest_email = db.Column(db.String(120))

    message = db.Column(db.Text)
    status = db.Column(db.String(20), default="new")  # new, contacted, reserved, fulfilled, cancelled
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Inquiry {self.id} status={self.status}>"
