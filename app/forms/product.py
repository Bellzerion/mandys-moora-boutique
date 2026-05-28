from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    category = SelectField('Category', choices=[
        ('Dresses', 'Dresses'),
        ('Outerwear', 'Outerwear'),
        ('Jumpsuits', 'Jumpsuits'),
        ('Tops', 'Tops'),
        ('Bottoms', 'Bottoms'),
        ('Accessories', 'Accessories')
    ], validators=[DataRequired()])
    price = DecimalField('Purchase Price ($)', validators=[DataRequired(), NumberRange(min=0.00)])
    rental_price = DecimalField('Rental Price / Day ($)', validators=[DataRequired(), NumberRange(min=0.00)])
    stock = IntegerField('Initial Stock', validators=[DataRequired(), NumberRange(min=0)])
    size = SelectField('Size', choices=[
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('One Size', 'One Size')
    ], validators=[DataRequired()])
    image = FileField('Product Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'webp', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Save Product')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('5', '★★★★★ (5/5)'),
        ('4', '★★★★☆ (4/5)'),
        ('3', '★★★☆☆ (3/5)'),
        ('2', '★★☆☆☆ (2/5)'),
        ('1', '★☆☆☆☆ (1/5)')
    ], validators=[DataRequired()])
    comment = TextAreaField('Review (Optional)', validators=[Length(max=500)])
    submit = SubmitField('Submit Review')
