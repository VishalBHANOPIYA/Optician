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
