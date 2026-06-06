from datetime import datetime
from slugify import slugify
from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    # type tells the frontend how to render: "eyewear" or "accessory"
    kind = db.Column(db.String(20), nullable=False, default="eyewear")
    icon = db.Column(db.String(200))  # optional category icon filename
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    products = db.relationship("Product", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category {self.name}>"


class Brand(db.Model):
    __tablename__ = "brands"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    logo = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)

    products = db.relationship("Product", backref="brand", lazy="dynamic")

    def __repr__(self):
        return f"<Brand {self.name}>"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    sku = db.Column(db.String(60), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=True)

    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_price = db.Column(db.Numeric(10, 2), nullable=True)
    stock = db.Column(db.Integer, default=0)

    # Common attributes
    gender = db.Column(db.String(20), default="Unisex")  # Men, Women, Unisex, Kids
    color = db.Column(db.String(60))
    material = db.Column(db.String(80))

    # Eyewear-only attributes (nullable for wallets/belts)
    frame_shape = db.Column(db.String(60))    # Round, Square, Aviator, Cat-eye, Rectangle, Wayfarer
    frame_size = db.Column(db.String(20))     # Small, Medium, Large
    lens_type = db.Column(db.String(60))      # Single Vision, Bifocal, Progressive, Blue-cut, Polarized
    is_prescription_ready = db.Column(db.Boolean, default=False)

    # Accessory-only attributes (nullable for eyewear)
    accessory_size = db.Column(db.String(40))  # belt size like 32/34/36 or wallet dimensions

    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_bestseller = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = db.relationship("ProductImage", backref="product", cascade="all, delete-orphan", lazy="select", order_by="ProductImage.position")
    wishlisted_by = db.relationship("Wishlist", backref="product", cascade="all, delete-orphan", lazy="dynamic")
    inquiries = db.relationship("Inquiry", backref="product", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.price:
            return round((1 - float(self.discount_price) / float(self.price)) * 100)
        return 0

    @property
    def primary_image(self):
        if self.images:
            return self.images[0].filename
        return None

    @property
    def tryon_image(self):
        import os
        from flask import current_app
        # 1. Check if SKU-specific tryon image exists (e.g. cg_3001_tryon.png)
        sku_clean = self.sku.lower().replace('-', '_')
        filename = f"{sku_clean}_tryon.png"
        path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
        if os.path.exists(path):
            return filename
        
        # 2. Check if shape-specific tryon image exists (e.g. cat_eye_tryon.png, aviator_tryon.png)
        shape_clean = (self.frame_shape or "").lower().replace('-', '_')
        shape_filename = f"{shape_clean}_tryon.png"
        shape_path = os.path.join(current_app.root_path, 'static', 'uploads', shape_filename)
        if os.path.exists(shape_path):
            return shape_filename
            
        # 3. Fallbacks
        shape_defaults = {
            "rectangle": "eg_1001.png",
            "round": "round_tryon.png",
        }
        if shape_clean in shape_defaults:
            return shape_defaults[shape_clean]
            
        return self.primary_image

    @staticmethod
    def generate_slug(name, sku):
        return f"{slugify(name)}-{sku.lower()}"

    def __repr__(self):
        return f"<Product {self.name} ({self.sku})>"


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(200))
    position = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<ProductImage {self.filename}>"
