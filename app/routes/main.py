from flask import Blueprint, render_template, Response, request, url_for
from app.models import Category, Product, Brand

main_bp = Blueprint("main", __name__)


def get_diverse_products(products_list, limit=8, exclude_ids=None):
    if exclude_ids is None:
        exclude_ids = set()
    filtered = [p for p in products_list if p.id not in exclude_ids]
    
    # Group products by category_id to ensure category representation
    by_category = {}
    for p in filtered:
        by_category.setdefault(p.category_id, []).append(p)
        
    selected = []
    category_ids = list(by_category.keys())
    category_ids.sort()
    
    indices = {cid: 0 for cid in category_ids}
    while len(selected) < limit and any(indices[cid] < len(by_category[cid]) for cid in category_ids):
        for cid in category_ids:
            if len(selected) >= limit:
                break
            if indices[cid] < len(by_category[cid]):
                selected.append(by_category[cid][indices[cid]])
                indices[cid] += 1
    return selected


@main_bp.route("/")
def home():
    categories = (Category.query
                  .filter_by(is_active=True)
                  .order_by(Category.display_order)
                  .all())
    
    all_featured = (Product.query
                    .filter_by(is_active=True, is_featured=True)
                    .order_by(Product.created_at.desc())
                    .all())
    
    featured = get_diverse_products(all_featured, limit=14)
    featured_ids = {p.id for p in featured}
    
    all_bestsellers = (Product.query
                       .filter_by(is_active=True, is_bestseller=True)
                       .order_by(Product.created_at.desc())
                       .all())
    
    bestsellers = get_diverse_products(all_bestsellers, limit=14, exclude_ids=featured_ids)
    
    brands = Brand.query.filter_by(is_active=True).all()
    return render_template("index.html",
                           categories=categories,
                           featured=featured,
                           bestsellers=bestsellers,
                           brands=brands)


@main_bp.route("/health")
def health():
    return {"status": "ok", "shop": "Ayan-Optics"}


@main_bp.route("/contact")
def contact():
    return render_template("contact.html")


@main_bp.route("/contact-lenses")
def contact_lenses():
    featured_lenses = (Product.query
                       .join(Category)
                       .filter(Category.kind == "lenses", Product.is_active == True)
                       .limit(8).all())
    return render_template("contact_lenses.html", featured_lenses=featured_lenses)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/robots.txt")
def robots():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /account/\n"
        f"Sitemap: {request.url_root}sitemap.xml\n"
    )
    return Response(body, mimetype="text/plain")


@main_bp.route("/sitemap.xml")
def sitemap():
    urls = [
        url_for("main.home", _external=True),
        url_for("main.contact", _external=True),
        url_for("main.about", _external=True),
    ]
    for c in Category.query.filter_by(is_active=True).all():
        urls.append(url_for("catalog.category", slug=c.slug, _external=True))
    for p in Product.query.filter_by(is_active=True).all():
        urls.append(url_for("catalog.product_detail", slug=p.slug, _external=True))
    items = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>'
    return Response(xml, mimetype="application/xml")
