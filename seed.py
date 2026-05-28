"""Seeds the database with categories, brands, and a default admin.
Run: python seed.py
"""
from app import create_app
from app.extensions import db
from app.models import Category, Brand, Admin

app = create_app()

CATEGORIES = [
    ("Eyeglasses", "eyeglasses", "eyewear", 1),
    ("Sunglasses", "sunglasses", "eyewear", 2),
    ("Computer Glasses", "computer-glasses", "eyewear", 3),
    ("Kids Glasses", "kids-glasses", "eyewear", 4),
    ("Reading Glasses", "reading-glasses", "eyewear", 5),
    ("Men's Wallets", "mens-wallets", "accessory", 6),
    ("Men's Belts", "mens-belts", "accessory", 7),
]

BRANDS = [
    ("SeeOne", "seeone"),
    ("Crizal", "crizal"),
    ("Nova", "nova"),
    ("Satin", "satin"),
    ("Blumax", "blumax"),
    ("Rodenstock", "rodenstock"),
    ("Essilor", "essilor"),
    ("Kodak", "kodak"),
    ("Zeiss", "zeiss"),
]

with app.app_context():
    # Categories
    for name, slug, kind, order in CATEGORIES:
        if not Category.query.filter_by(slug=slug).first():
            db.session.add(Category(name=name, slug=slug, kind=kind, display_order=order))

    # Brands
    for name, slug in BRANDS:
        if not Brand.query.filter_by(slug=slug).first():
            db.session.add(Brand(name=name, slug=slug))

    # Default super admin (CHANGE PASSWORD AFTER FIRST LOGIN)
    if not Admin.query.filter_by(username="ayanadmin").first():
        admin = Admin(
            username="ayanadmin",
            email="admin@ayan-optics.local",
            is_super=True,
        )
        admin.set_password("ChangeMe@2024")
        db.session.add(admin)

    db.session.commit()
    print("✅ Seeded categories, brands, and default admin.")
    print("   Admin login -> username: ayanadmin   password: ChangeMe@2024")
    print("   CHANGE THE ADMIN PASSWORD before going live.")
