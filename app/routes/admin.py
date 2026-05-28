import os
import uuid
from slugify import slugify
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, current_app, abort)
from flask_login import current_user
from werkzeug.utils import secure_filename
from PIL import Image
from app.extensions import db
from app.models import Product, Category, Brand, ProductImage, Inquiry
from app.forms.admin import ProductForm, CategoryForm, BrandForm, InquiryForm, ChangePasswordForm
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


def _save_image(file_storage):
    """Validate, sanitize and store an uploaded image. Returns stored filename or None."""
    if not file_storage or not file_storage.filename:
        return None
    original = secure_filename(file_storage.filename)
    if "." not in original:
        return None
    ext = original.rsplit(".", 1)[-1].lower()
    if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        return None
    new_name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_name)
    try:
        img = Image.open(file_storage)
        img.thumbnail((1200, 1200))
        if img.mode in ("RGBA", "P") and ext in ("jpg", "jpeg"):
            img = img.convert("RGB")
        img.save(path)
    except Exception:
        return None
    return new_name


def _unique_sku(sku, exclude_id=None):
    q = Product.query.filter(Product.sku == sku)
    if exclude_id:
        q = q.filter(Product.id != exclude_id)
    return q.first() is None


# ---------- Dashboard ----------
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    stats = {
        "products": Product.query.count(),
        "active_products": Product.query.filter_by(is_active=True).count(),
        "categories": Category.query.count(),
        "brands": Brand.query.count(),
        "inquiries": Inquiry.query.count(),
        "new_inquiries": Inquiry.query.filter_by(status="new").count(),
    }
    recent = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(6).all()
    low_stock = Product.query.filter(Product.stock <= 2, Product.is_active == True).limit(6).all()
    return render_template("admin/dashboard.html", stats=stats, recent=recent, low_stock=low_stock)


# ---------- Products ----------
@admin_bp.route("/products")
@admin_required
def products():
    q = request.args.get("q", "").strip()
    query = Product.query
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Product.name.ilike(like), Product.sku.ilike(like)))
    items = query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=items, q=q)


def _populate_choices(form):
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.display_order).all()]
    form.brand_id.choices = [(0, "— None —")] + [(b.id, b.name) for b in Brand.query.order_by(Brand.name).all()]


@admin_bp.route("/products/new", methods=["GET", "POST"])
@admin_required
def product_new():
    form = ProductForm()
    _populate_choices(form)
    if form.validate_on_submit():
        sku = form.sku.data.strip().upper()
        if not _unique_sku(sku):
            flash("That SKU already exists. Use a unique SKU.", "danger")
            return render_template("admin/product_form.html", form=form, mode="new", product=None)
        p = Product(
            name=form.name.data.strip(), sku=sku,
            slug=slugify(f"{form.name.data}-{sku}"),
            category_id=form.category_id.data,
            brand_id=(form.brand_id.data or None),
            price=form.price.data, discount_price=form.discount_price.data,
            stock=form.stock.data or 0, gender=form.gender.data,
            frame_shape=form.frame_shape.data or None, frame_size=form.frame_size.data or None,
            lens_type=form.lens_type.data or None, material=form.material.data or None,
            color=form.color.data or None, accessory_size=form.accessory_size.data or None,
            description=form.description.data or None,
            is_prescription_ready=form.is_prescription_ready.data,
            is_active=form.is_active.data, is_featured=form.is_featured.data,
            is_bestseller=form.is_bestseller.data,
        )
        db.session.add(p)
        db.session.commit()
        pos = 0
        for f in request.files.getlist("images"):
            name = _save_image(f)
            if name:
                db.session.add(ProductImage(product_id=p.id, filename=name, position=pos, alt_text=p.name))
                pos += 1
        db.session.commit()
        flash("Product created.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", form=form, mode="new", product=None)


@admin_bp.route("/products/<int:pid>/edit", methods=["GET", "POST"])
@admin_required
def product_edit(pid):
    p = Product.query.get_or_404(pid)
    form = ProductForm(obj=p)
    _populate_choices(form)
    if request.method == "GET":
        form.brand_id.data = p.brand_id or 0
        form.frame_shape.data = p.frame_shape or ""
        form.frame_size.data = p.frame_size or ""
    if form.validate_on_submit():
        sku = form.sku.data.strip().upper()
        if not _unique_sku(sku, exclude_id=p.id):
            flash("That SKU already exists.", "danger")
            return render_template("admin/product_form.html", form=form, mode="edit", product=p)
        p.name = form.name.data.strip()
        p.sku = sku
        p.slug = slugify(f"{p.name}-{sku}")
        p.category_id = form.category_id.data
        p.brand_id = form.brand_id.data or None
        p.price = form.price.data
        p.discount_price = form.discount_price.data
        p.stock = form.stock.data or 0
        p.gender = form.gender.data
        p.frame_shape = form.frame_shape.data or None
        p.frame_size = form.frame_size.data or None
        p.lens_type = form.lens_type.data or None
        p.material = form.material.data or None
        p.color = form.color.data or None
        p.accessory_size = form.accessory_size.data or None
        p.description = form.description.data or None
        p.is_prescription_ready = form.is_prescription_ready.data
        p.is_active = form.is_active.data
        p.is_featured = form.is_featured.data
        p.is_bestseller = form.is_bestseller.data
        pos = len(p.images)
        for f in request.files.getlist("images"):
            name = _save_image(f)
            if name:
                db.session.add(ProductImage(product_id=p.id, filename=name, position=pos, alt_text=p.name))
                pos += 1
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", form=form, mode="edit", product=p)


@admin_bp.route("/products/<int:pid>/delete", methods=["POST"])
@admin_required
def product_delete(pid):
    p = Product.query.get_or_404(pid)
    for img in p.images:
        try:
            os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], img.filename))
        except OSError:
            pass
    db.session.delete(p)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for("admin.products"))


@admin_bp.route("/products/image/<int:image_id>/delete", methods=["POST"])
@admin_required
def product_image_delete(image_id):
    img = ProductImage.query.get_or_404(image_id)
    pid = img.product_id
    try:
        os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], img.filename))
    except OSError:
        pass
    db.session.delete(img)
    db.session.commit()
    flash("Image removed.", "info")
    return redirect(url_for("admin.product_edit", pid=pid))


# ---------- Categories ----------
@admin_bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        slug = slugify(form.name.data)
        if Category.query.filter_by(slug=slug).first():
            flash("A category with that name already exists.", "danger")
        else:
            db.session.add(Category(name=form.name.data.strip(), slug=slug,
                                    kind=form.kind.data, display_order=form.display_order.data or 0,
                                    is_active=form.is_active.data))
            db.session.commit()
            flash("Category added.", "success")
        return redirect(url_for("admin.categories"))
    items = Category.query.order_by(Category.display_order).all()
    return render_template("admin/categories.html", form=form, categories=items)


@admin_bp.route("/categories/<int:cid>/toggle", methods=["POST"])
@admin_required
def category_toggle(cid):
    c = Category.query.get_or_404(cid)
    c.is_active = not c.is_active
    db.session.commit()
    flash(f"Category '{c.name}' is now {'active' if c.is_active else 'hidden'}.", "info")
    return redirect(url_for("admin.categories"))


# ---------- Brands ----------
@admin_bp.route("/brands", methods=["GET", "POST"])
@admin_required
def brands():
    form = BrandForm()
    if form.validate_on_submit():
        slug = slugify(form.name.data)
        if Brand.query.filter_by(slug=slug).first():
            flash("That brand already exists.", "danger")
        else:
            db.session.add(Brand(name=form.name.data.strip(), slug=slug, is_active=form.is_active.data))
            db.session.commit()
            flash("Brand added.", "success")
        return redirect(url_for("admin.brands"))
    items = Brand.query.order_by(Brand.name).all()
    return render_template("admin/brands.html", form=form, brands=items)


@admin_bp.route("/brands/<int:bid>/toggle", methods=["POST"])
@admin_required
def brand_toggle(bid):
    b = Brand.query.get_or_404(bid)
    b.is_active = not b.is_active
    db.session.commit()
    flash(f"Brand '{b.name}' is now {'active' if b.is_active else 'hidden'}.", "info")
    return redirect(url_for("admin.brands"))


# ---------- Inquiries (Reserve inbox) ----------
@admin_bp.route("/inquiries")
@admin_required
def inquiries():
    status = request.args.get("status", "")
    query = Inquiry.query
    if status:
        query = query.filter_by(status=status)
    items = query.order_by(Inquiry.created_at.desc()).all()
    return render_template("admin/inquiries.html", inquiries=items, status=status)


@admin_bp.route("/inquiries/<int:iid>", methods=["GET", "POST"])
@admin_required
def inquiry_detail(iid):
    inq = Inquiry.query.get_or_404(iid)
    form = InquiryForm(obj=inq)
    if form.validate_on_submit():
        inq.status = form.status.data
        inq.admin_notes = form.admin_notes.data
        db.session.commit()
        flash("Inquiry updated.", "success")
        return redirect(url_for("admin.inquiries"))
    return render_template("admin/inquiry_detail.html", inq=inq, form=form)


# ---------- Change Password ----------
@admin_bp.route("/change-password", methods=["GET", "POST"])
@admin_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/change_password.html", form=form)
