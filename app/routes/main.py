from flask import Blueprint, render_template, request
from app.models.product import Product

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
    
    categories = ['Dresses', 'Outerwear', 'Jumpsuits', 'Tops', 'Bottoms', 'Accessories']
    sizes = ['XS', 'S', 'M', 'L', 'XL', 'One Size']
    
    return render_template('customer/shop.html', 
                           products=products, 
                           categories=categories, 
                           sizes=sizes, 
                           current_category=category, 
                           current_size=size, 
                           current_sort=sort_by,
                           search_query=search_query)

@main_bp.route('/product/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    # Related products from same category
    related = Product.query.filter(Product.category == product.category, Product.id != product.id).limit(4).all()
    return render_template('customer/product_details.html', product=product, related=related)

@main_bp.route('/about')
def about():
    return render_template('customer/about.html')

@main_bp.route('/contact')
def contact():
    return render_template('customer/contact.html')
