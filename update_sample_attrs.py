"""Backfills frame_size, material, color on existing sample products so filters demonstrate.
Run once: python update_sample_attrs.py"""
from app import create_app
from app.extensions import db
from app.models import Product

app = create_app()

ATTRS = {
    "EG-1001": ("Medium", "Acetate", "Black"),
    "EG-1002": ("Small", "Metal", "Rose Gold"),
    "EG-1003": ("Medium", "TR90", "Blue"),
    "EG-1004": ("Small", "Acetate", "Tortoise"),
    "EG-1005": ("Large", "Acetate", "Black"),
    "EG-1006": ("Medium", "Acetate", "Brown"),
    "SG-2001": ("Large", "Metal", "Gold"),
    "SG-2002": ("Medium", "Acetate", "Black"),
    "SG-2003": ("Small", "Metal", "Silver"),
    "SG-2004": ("Large", "TR90", "Black"),
    "CG-3001": ("Medium", "TR90", "Black"),
    "KG-4001": ("Small", "TR90", "Red"),
    "RG-7001": ("Medium", "Metal", "Black"),
    "WL-5001": (None, "Leather", "Brown"),
    "WL-5002": (None, "Leather", "Tan"),
    "BL-6001": (None, "Leather", "Black"),
    "BL-6002": (None, "Leather", "Brown"),
}

with app.app_context():
    for sku, (size, material, color) in ATTRS.items():
        p = Product.query.filter_by(sku=sku).first()
        if p:
            p.frame_size = size
            p.material = material
            p.color = color
    db.session.commit()
    print("✅ Updated sample product attributes (size, material, color).")
