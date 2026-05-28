from flask import Blueprint, render_template, request
from app.models import Category, Brand, Product
from app.forms.reserve import ReserveForm

catalog_bp = Blueprint("catalog", __name__)

SHAPES = ["Rectangle", "Round", "Cat-eye", "Aviator", "Square", "Wayfarer"]
GENDERS = ["Men", "Women", "Unisex", "Kids"]
SIZES = ["Small", "Medium", "Large"]
PRICE_RANGES = [
    ("Under ₹500", 0, 500),
    ("₹500 - ₹1000", 500, 1000),
    ("₹1000 - ₹1500", 1000, 1500),
    ("₹1500 - ₹2000", 1500, 2000),
    ("Above ₹2000", 2000, 100000),
]


def _distinct(column):
    rows = Product.query.with_entities(column).filter(column.isnot(None)).distinct().all()
    return sorted({r[0] for r in rows if r[0]})


def _apply_filters(query):
    gender = request.args.get("gender")
    shape = request.args.get("shape")
    brand_slug = request.args.get("brand")
    size = request.args.get("size")
    material = request.args.get("material")
    color = request.args.get("color")
    min_p = request.args.get("min", type=float)
    max_p = request.args.get("max", type=float)

    if gender:
        query = query.filter(Product.gender == gender)
    if shape:
        query = query.filter(Product.frame_shape == shape)
    if size:
        query = query.filter(Product.frame_size == size)
    if material:
        query = query.filter(Product.material == material)
    if color:
        query = query.filter(Product.color == color)
    if brand_slug:
        b = Brand.query.filter_by(slug=brand_slug).first()
        if b:
            query = query.filter(Product.brand_id == b.id)
    if min_p is not None:
        query = query.filter(Product.price >= min_p)
    if max_p is not None:
        query = query.filter(Product.price <= max_p)

    sort = request.args.get("sort", "recommended")
    if sort == "price_low":
        query = query.order_by(Product.price.asc())
    elif sort == "price_high":
        query = query.order_by(Product.price.desc())
    elif sort == "newest":
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.is_featured.desc(), Product.created_at.desc())
    return query


def _filter_context():
    return {
        "shapes": SHAPES,
        "genders": GENDERS,
        "sizes": SIZES,
        "price_ranges": PRICE_RANGES,
        "brands": Brand.query.filter_by(is_active=True).all(),
        "materials": _distinct(Product.material),
        "colors": _distinct(Product.color),
    }


@catalog_bp.route("/c/<slug>")
def category(slug):
    cat = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    query = Product.query.filter_by(category_id=cat.id, is_active=True)
    products = _apply_filters(query).all()
    return render_template("catalog/listing.html",
                           category=cat, products=products,
                           title=cat.name, is_search=False, search_term="",
                           **_filter_context())


@catalog_bp.route("/search")
def search():
    term = request.args.get("q", "").strip()
    query = Product.query.filter_by(is_active=True)
    if term:
        query = query.filter(Product.name.ilike(f"%{term}%"))
    products = _apply_filters(query).all()
    title = f'Search results for "{term}"' if term else "All Products"
    return render_template("catalog/listing.html",
                           category=None, products=products,
                           title=title, is_search=True, search_term=term,
                           **_filter_context())


@catalog_bp.route("/product/<slug>")
def product_detail(slug):
    p = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = (Product.query
               .filter(Product.category_id == p.category_id,
                       Product.id != p.id,
                       Product.is_active == True)
               .limit(4).all())
    return render_template("product/detail.html", p=p, related=related, reserve_form=ReserveForm())

