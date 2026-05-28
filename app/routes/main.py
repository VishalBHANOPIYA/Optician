from flask import Blueprint, render_template
from app.models import Category, Product, Brand

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    categories = (Category.query
                  .filter_by(is_active=True)
                  .order_by(Category.display_order)
                  .all())
    featured = (Product.query
                .filter_by(is_active=True, is_featured=True)
                .order_by(Product.created_at.desc())
                .limit(8).all())
    bestsellers = (Product.query
                   .filter_by(is_active=True, is_bestseller=True)
                   .order_by(Product.created_at.desc())
                   .limit(8).all())
    brands = Brand.query.filter_by(is_active=True).all()
    return render_template("index.html",
                           categories=categories,
                           featured=featured,
                           bestsellers=bestsellers,
                           brands=brands)


@main_bp.route("/health")
def health():
    return {"status": "ok", "shop": "Ayan-Optics"}
