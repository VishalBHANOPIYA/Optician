from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app.extensions import db
from app.models import Product, Wishlist, Inquiry
from app.forms.reserve import ReserveForm
from app.utils.decorators import user_required

account_bp = Blueprint("account", __name__)


@account_bp.route("/wishlist")
@user_required
def wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.id).order_by(Wishlist.created_at.desc()).all()
    products = [w.product for w in items if w.product and w.product.is_active]
    return render_template("account/wishlist.html", products=products)


@account_bp.route("/wishlist/toggle/<int:product_id>", methods=["POST"])
@user_required
def wishlist_toggle(product_id):
    product = Product.query.get_or_404(product_id)
    existing = Wishlist.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Removed from your wishlist.", "info")
    else:
        db.session.add(Wishlist(user_id=current_user.id, product_id=product.id))
        db.session.commit()
        flash("Saved to your wishlist.", "success")
    return redirect(request.referrer or url_for("main.home"))


@account_bp.route("/reserve/<int:product_id>", methods=["POST"])
@user_required
def reserve(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReserveForm()
    if form.validate_on_submit():
        inq = Inquiry(
            user_id=current_user.id,
            product_id=product.id,
            guest_name=current_user.full_name,
            guest_phone=current_user.phone,
            guest_email=current_user.email,
            message=form.message.data,
            status="new",
        )
        db.session.add(inq)
        db.session.commit()
        flash("Reserve request sent! We'll keep it ready at the store and may call to confirm.", "success")
    else:
        flash("Could not send your request. Please try again.", "danger")
    return redirect(url_for("catalog.product_detail", slug=product.slug))
