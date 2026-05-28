"""Adds a handful of sample products so the homepage has content to show.
Run once: python sample_products.py
Safe to re-run (skips existing SKUs)."""
from app import create_app
from app.extensions import db
from app.models import Category, Brand, Product

app = create_app()

SAMPLES = [
    # name, sku, category_slug, brand_slug, price, discount, gender, shape, featured, bestseller
    ("Classic Black Rectangle", "EG-1001", "eyeglasses", "nova", 1200, 899, "Men", "Rectangle", True, True),
    ("Rose Gold Cat-Eye", "EG-1002", "eyeglasses", "satin", 1500, 1199, "Women", "Cat-eye", True, False),
    ("Matte Blue Round", "EG-1003", "eyeglasses", "blumax", 1100, None, "Unisex", "Round", True, True),
    ("Aviator Sunglasses Gold", "SG-2001", "sunglasses", "nova", 1800, 1499, "Men", "Aviator", True, False),
    ("Wayfarer Sunglasses Black", "SG-2002", "sunglasses", "satin", 1600, 1299, "Unisex", "Wayfarer", False, True),
    ("Blue-Cut Computer Glasses", "CG-3001", "computer-glasses", "blumax", 999, 799, "Unisex", "Square", True, True),
    ("Kids Flexible Frame Red", "KG-4001", "kids-glasses", "nova", 800, 650, "Kids", "Round", True, False),
    ("Genuine Leather Wallet Brown", "WL-5001", "mens-wallets", None, 700, 499, "Men", None, True, True),
    ("Formal Leather Belt Black", "BL-6001", "mens-belts", None, 600, 449, "Men", None, True, False),

    ("Slim Round Tortoise", "EG-1004", "eyeglasses", "essilor", 1400, 1099, "Women", "Round", False, True),
    ("Bold Square Black", "EG-1005", "eyeglasses", "zeiss", 1700, None, "Men", "Square", True, False),
    ("Retro Wayfarer Eyeglasses", "EG-1006", "eyeglasses", "kodak", 1300, 999, "Unisex", "Wayfarer", False, True),
    ("Polarized Round Sunglasses", "SG-2003", "sunglasses", "crizal", 1900, 1599, "Women", "Round", True, False),
    ("Sport Wrap Sunglasses", "SG-2004", "sunglasses", "rodenstock", 2100, 1799, "Men", "Square", False, True),
    ("Reading Glasses +1.5", "RG-7001", "reading-glasses", "seeone", 500, 399, "Unisex", "Rectangle", False, False),
    ("Bifold Wallet Tan", "WL-5002", "mens-wallets", None, 800, 599, "Men", None, False, True),
    ("Reversible Belt Brown/Black", "BL-6002", "mens-belts", None, 750, 549, "Men", None, True, False),
]

with app.app_context():
    for name, sku, cat_slug, brand_slug, price, disc, gender, shape, feat, best in SAMPLES:
        if Product.query.filter_by(sku=sku).first():
            continue
        cat = Category.query.filter_by(slug=cat_slug).first()
        brand = Brand.query.filter_by(slug=brand_slug).first() if brand_slug else None
        p = Product(
            name=name,
            sku=sku,
            slug=Product.generate_slug(name, sku),
            description=f"{name} — quality {('frame' if cat and cat.kind=='eyewear' else 'accessory')} at a pocket-friendly price from Ayan-Optics.",
            category_id=cat.id,
            brand_id=brand.id if brand else None,
            price=price,
            discount_price=disc,
            stock=10,
            gender=gender,
            frame_shape=shape,
            is_active=True,
            is_featured=feat,
            is_bestseller=best,
        )
        db.session.add(p)
    db.session.commit()
    print("✅ Sample products added.")
