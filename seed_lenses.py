"""Seeds contact lens categories, brands, and products.
Run: python seed_lenses.py
"""
from app import create_app
from app.extensions import db
from app.models import Category, Brand, Product, ProductImage

app = create_app()

CATEGORIES = [
    ("Clear Contact Lenses", "clear-lenses", "lenses", 20),
    ("Color Contact Lenses", "color-lenses", "lenses", 21),
    ("Toric Contact Lenses", "toric-lenses", "lenses", 22),
    ("Contact Lens Solutions", "solutions", "lenses", 23),
    ("Contact Lens Accessories", "lens-accessories", "lenses", 24),
]

BRANDS = [
    ("Aqualens", "aqualens"),
    ("Aquacolor", "aquacolor"),
    ("Bausch & Lomb", "bausch-lomb"),
    ("Acuvue", "acuvue"),
    ("Alcon", "alcon"),
]

PRODUCTS = [
    # (name, sku, category_slug, brand_slug, price, discount, image_url, description)
    ("Aqualens 24H Daily Clear Lenses (30 Pack)", 
     "AL-1001", "clear-lenses", "aqualens", 1500, 1275,
     "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80",
     "Aqualens 24H Daily disposable clear contact lenses. High water content and UV blocking for all-day comfort."),
    
    ("Bausch & Lomb Ultra Clear Monthly (6 Pack)", 
     "BL-1002", "clear-lenses", "bausch-lomb", 1800, 1599,
     "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=600&q=80",
     "Bausch & Lomb Ultra moisture seal contact lenses. Designed for digital device users with 16-hour hydration comfort."),
    
    ("Aquacolor Dusky Brown Daily (10 Pack)", 
     "AC-2001", "color-lenses", "aquacolor", 999, 849,
     "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=600&q=80",
     "Aquacolor premium daily disposable color contact lenses in Dusky Brown. Elevate your daily look naturally."),
    
    ("Aquacolor Sterling Grey Daily (10 Pack)", 
     "AC-2002", "color-lenses", "aquacolor", 999, 849,
     "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=600&q=80",
     "Aquacolor daily disposable color contact lenses in Sterling Grey. Bold, beautiful color blending technology."),
    
    ("Aquacolor Gemstone Green Daily (10 Pack)", 
     "AC-2003", "color-lenses", "aquacolor", 999, 849,
     "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=600&q=80",
     "Aquacolor daily disposable color contact lenses in Gemstone Green. Rich, vibrant green tones with high comfort."),
    
    ("Aquacolor Brilliant Blue Daily (10 Pack)", 
     "AC-2004", "color-lenses", "aquacolor", 999, 849,
     "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80",
     "Aquacolor daily disposable color contact lenses in Brilliant Blue. Striking and natural deep blue shades."),

    ("Aqualens Comfort Toric (Astigmatism Pack)", 
     "AL-3001", "toric-lenses", "aqualens", 2200, 1999,
     "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=600&q=80",
     "Toric contact lenses from Aqualens for cylindrical powers. Stable vision and moisture seal comfort."),

    ("Aqualens Comfort Solution (360ml)", 
     "AL-4001", "solutions", "aqualens", 450, 399,
     "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?auto=format&fit=crop&w=600&q=80",
     "Aqualens double action moisturizing comfort solution. Perfect for cleaning, rinsing, and storing all soft lenses."),

    ("Aqualens Premium Double Contact Lens Case", 
     "AL-5001", "lens-accessories", "aqualens", 199, 149,
     "https://images.unsplash.com/photo-1617897903246-719242758050?auto=format&fit=crop&w=600&q=80",
     "Premium double case for hygienic storage of your contact lenses. Leakproof and travel friendly."),
]

with app.app_context():
    # 1. Seed Categories
    for name, slug, kind, order in CATEGORIES:
        cat = Category.query.filter_by(slug=slug).first()
        if not cat:
            cat = Category(name=name, slug=slug, kind=kind, display_order=order)
            db.session.add(cat)
            db.session.flush()
            print(f"Added category: {name}")
        else:
            cat.kind = kind
            cat.display_order = order
            print(f"Updated category: {name}")

    # 2. Seed Brands
    for name, slug in BRANDS:
        brand = Brand.query.filter_by(slug=slug).first()
        if not brand:
            brand = Brand(name=name, slug=slug)
            db.session.add(brand)
            db.session.flush()
            print(f"Added brand: {name}")

    db.session.commit()

    # 3. Seed Products
    for name, sku, cat_slug, brand_slug, price, discount, img_url, desc in PRODUCTS:
        p = Product.query.filter_by(sku=sku).first()
        cat = Category.query.filter_by(slug=cat_slug).first()
        brand = Brand.query.filter_by(slug=brand_slug).first()
        
        if not p:
            p = Product(
                name=name,
                sku=sku,
                slug=Product.generate_slug(name, sku),
                description=desc,
                category_id=cat.id if cat else 1,
                brand_id=brand.id if brand else None,
                price=price,
                discount_price=discount,
                stock=25,
                gender="Unisex",
                is_active=True,
                is_featured=True,
                is_bestseller=True
            )
            db.session.add(p)
            db.session.flush()
            
            # Add product image
            img = ProductImage(product_id=p.id, filename=img_url, alt_text=name, position=0)
            db.session.add(img)
            print(f"Created product: {name}")
        else:
            p.category_id = cat.id if cat else p.category_id
            p.brand_id = brand.id if brand else p.brand_id
            p.price = price
            p.discount_price = discount
            p.description = desc
            # Check image
            if not p.images:
                img = ProductImage(product_id=p.id, filename=img_url, alt_text=name, position=0)
                db.session.add(img)
            else:
                p.images[0].filename = img_url
            print(f"Updated product: {name}")

    db.session.commit()
    print("✅ Contact Lens database seeding complete!")
