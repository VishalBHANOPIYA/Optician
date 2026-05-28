from flask_wtf import FlaskForm
from wtforms import (StringField, DecimalField, IntegerField, SelectField,
                     BooleanField, TextAreaField, SubmitField, PasswordField)
from wtforms.validators import DataRequired, Optional, NumberRange, Length, EqualTo

GENDER_CHOICES = [("Men", "Men"), ("Women", "Women"), ("Unisex", "Unisex"), ("Kids", "Kids")]
SIZE_CHOICES = [("", "Any / N/A"), ("Small", "Small"), ("Medium", "Medium"), ("Large", "Large")]
SHAPE_CHOICES = [("", "Any / N/A"), ("Rectangle", "Rectangle"), ("Round", "Round"),
                 ("Cat-eye", "Cat-eye"), ("Aviator", "Aviator"), ("Square", "Square"), ("Wayfarer", "Wayfarer")]


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(2, 180)])
    sku = StringField("SKU (unique code)", validators=[DataRequired(), Length(2, 60)])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    brand_id = SelectField("Brand", coerce=int, validators=[Optional()])
    price = DecimalField("Price (₹)", validators=[DataRequired(), NumberRange(min=0)])
    discount_price = DecimalField("Discount Price (₹)", validators=[Optional(), NumberRange(min=0)])
    stock = IntegerField("Stock", default=0, validators=[Optional(), NumberRange(min=0)])
    gender = SelectField("Gender", choices=GENDER_CHOICES, default="Unisex")
    frame_shape = SelectField("Frame Shape", choices=SHAPE_CHOICES, validators=[Optional()])
    frame_size = SelectField("Frame Size", choices=SIZE_CHOICES, validators=[Optional()])
    lens_type = StringField("Lens Type", validators=[Optional(), Length(max=60)])
    material = StringField("Material", validators=[Optional(), Length(max=80)])
    color = StringField("Colour", validators=[Optional(), Length(max=60)])
    accessory_size = StringField("Accessory Size (belt/wallet)", validators=[Optional(), Length(max=40)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=2000)])
    is_prescription_ready = BooleanField("Prescription Ready")
    is_active = BooleanField("Active (visible on site)", default=True)
    is_featured = BooleanField("Featured")
    is_bestseller = BooleanField("Bestseller")
    submit = SubmitField("Save Product")


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(2, 80)])
    kind = SelectField("Kind", choices=[("eyewear", "Eyewear"), ("accessory", "Accessory")])
    display_order = IntegerField("Display Order", default=0, validators=[Optional()])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Category")


class BrandForm(FlaskForm):
    name = StringField("Brand Name", validators=[DataRequired(), Length(2, 80)])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Brand")


class InquiryForm(FlaskForm):
    status = SelectField("Status", choices=[
        ("new", "New"), ("contacted", "Contacted"), ("reserved", "Reserved"),
        ("fulfilled", "Fulfilled"), ("cancelled", "Cancelled")])
    admin_notes = TextAreaField("Internal Notes", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Update")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo("new_password", message="Passwords must match")])
    submit = SubmitField("Change Password")
