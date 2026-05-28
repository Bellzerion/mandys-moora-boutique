from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app.extensions import db
from app.models.product import Product
from app.models.review import Review
from app.models.inventory_log import InventoryLog
from app.forms.product import ReviewForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # Fetch 4 featured products for showcase
    featured = Product.query.filter(Product.stock > 0).limit(4).all()
    return render_template('customer/index.html', featured=featured)

@main_bp.route('/shop')
def shop():
    category = request.args.get('category', '')
    size = request.args.get('size', '')
    sort_by = request.args.get('sort_by', 'newest')  # 'newest', 'price_asc', 'price_desc'
    search_query = request.args.get('q', '')
    
    query = Product.query
    
    # Filter by category
    if category:
        query = query.filter(Product.category == category)
        
    # Filter by size
    if size:
        query = query.filter(Product.size == size)
        
    # Filter by search
    if search_query:
        query = query.filter(
            Product.name.ilike(f'%{search_query}%') | 
            Product.description.ilike(f'%{search_query}%')
        )
        
    # Sorting
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())
        
    products = query.all()
    
    # Hide products out of stock for > 1 day
    visible_products = []
    now = datetime.utcnow()
    for p in products:
        if p.stock <= 0:
            latest_log = InventoryLog.query.filter_by(product_id=p.id).order_by(InventoryLog.created_at.desc()).first()
            if latest_log and (now - latest_log.created_at > timedelta(days=1)):
                continue
        visible_products.append(p)
    
    categories = ['Dresses', 'Outerwear', 'Jumpsuits', 'Tops', 'Bottoms', 'Accessories']
    sizes = ['XS', 'S', 'M', 'L', 'XL', 'One Size']
    
    return render_template('customer/shop.html', 
                           products=visible_products, 
                           categories=categories, 
                           sizes=sizes, 
                           current_category=category, 
                           current_size=size, 
                           current_sort=sort_by,
                           search_query=search_query)

@main_bp.route('/product/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    
    now = datetime.utcnow()
    if product.stock <= 0:
        latest_log = InventoryLog.query.filter_by(product_id=product.id).order_by(InventoryLog.created_at.desc()).first()
        if latest_log and (now - latest_log.created_at > timedelta(days=1)):
            flash('This product is no longer available.', 'warning')
            return redirect(url_for('main.shop'))
            
    form = ReviewForm()
    # Related products from same category
    related_candidates = Product.query.filter(Product.category == product.category, Product.id != product.id).all()
    
    related = []
    for p in related_candidates:
        if p.stock <= 0:
            latest_log = InventoryLog.query.filter_by(product_id=p.id).order_by(InventoryLog.created_at.desc()).first()
            if latest_log and (now - latest_log.created_at > timedelta(days=1)):
                continue
        related.append(p)
        if len(related) == 4:
            break
            
    return render_template('customer/product_details.html', product=product, related=related, form=form)

@main_bp.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def submit_review(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()
    if form.validate_on_submit():
        # Check if user already reviewed
        existing = Review.query.filter_by(product_id=product.id, user_id=current_user.id).first()
        if existing:
            flash('You have already reviewed this product.', 'warning')
        else:
            review = Review(
                product_id=product.id,
                user_id=current_user.id,
                rating=int(form.rating.data),
                comment=form.comment.data
            )
            db.session.add(review)
            db.session.commit()
            flash('Thank you for your review!', 'success')
    return redirect(url_for('main.product_details', product_id=product.id))

@main_bp.route('/about')
def about():
    return render_template('customer/about.html')

@main_bp.route('/contact')
def contact():
    return render_template('customer/contact.html')
