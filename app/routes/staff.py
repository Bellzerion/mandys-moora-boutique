import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from PIL import Image

from app.extensions import db
from app.models.product import Product
from app.models.order import Order
from app.models.rental import Rental
from app.models.inventory_log import InventoryLog
from app.forms.product import ProductForm
from app.routes.decorators import role_required

staff_bp = Blueprint('staff', __name__)

def save_and_optimize_image(form_file):
    """
    Saves an uploaded image file, converting it to JPEG, resizing it to a max boundary,
    and compressing it using Pillow.
    """
    if not form_file or form_file.filename == '':
        return None
        
    filename = secure_filename(form_file.filename)
    unique_name = f"{uuid.uuid4().hex}_{os.path.splitext(filename)[0]}.jpg"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
    
    # Process with Pillow
    img = Image.open(form_file)
    
    # Convert RGBA to RGB
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])
        else:
            background.paste(img)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
        
    # Resize (max width/height 800px)
    img.thumbnail((800, 800))
    
    # Save optimized JPEG
    img.save(file_path, 'JPEG', quality=85)
    
    # Return relative path for url_for
    return f"uploads/{unique_name}"

@staff_bp.route('/products', methods=['GET', 'POST'])
@login_required
@role_required('staff', 'admin')
def products():
    form = ProductForm()
    if form.validate_on_submit():
        image_path = None
        if form.image.data:
            image_path = save_and_optimize_image(form.image.data)
            if image_path:
                image_path = url_for('static', filename=image_path)
                
        # Set default image if none provided
        if not image_path:
            image_path = "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=600&auto=format&fit=crop"
            
        prod = Product(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            price=form.price.data,
            rental_price=form.rental_price.data,
            stock=form.stock.data,
            size=form.size.data,
            image_url=image_path
        )
        prod.update_status()
        db.session.add(prod)
        db.session.commit()
        
        # Log Inventory Creation
        log = InventoryLog(
            product_id=prod.id,
            action='Created',
            quantity=prod.stock,
            notes='Added new product via product manager'
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Product "{prod.name}" added successfully.', 'success')
        return redirect(url_for('staff.products'))
        
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('staff/products.html', products=all_products, form=form)

@staff_bp.route('/products/edit/<int:product_id>', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def edit_product(product_id):
    prod = Product.query.get_or_404(product_id)
    
    # We retrieve from standard form request
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')
    price = float(request.form.get('price', 0))
    rental_price = float(request.form.get('rental_price', 0))
    new_stock = int(request.form.get('stock', 0))
    size = request.form.get('size')
    
    # Calculate stock change for logs
    stock_change = new_stock - prod.stock
    
    prod.name = name
    prod.description = description
    prod.category = category
    prod.price = price
    prod.rental_price = rental_price
    prod.stock = new_stock
    prod.size = size
    
    # Image upload processing
    uploaded_file = request.files.get('image')
    if uploaded_file and uploaded_file.filename != '':
        image_path = save_and_optimize_image(uploaded_file)
        if image_path:
            prod.image_url = url_for('static', filename=image_path)
            
    prod.update_status()
    db.session.commit()
    
    # Log stock change if any
    if stock_change != 0:
        log = InventoryLog(
            product_id=prod.id,
            action='Restocked' if stock_change > 0 else 'Damaged',
            quantity=stock_change,
            notes=f"Stock manually modified in editor from {prod.stock - stock_change} to {prod.stock}"
        )
        db.session.add(log)
        db.session.commit()
        
    flash(f'Product "{prod.name}" updated successfully.', 'success')
    return redirect(url_for('staff.products'))

@staff_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def delete_product(product_id):
    prod = Product.query.get_or_404(product_id)
    name = prod.name
    
    # Delete product logs, then the product itself
    # SQLAlchemy handles delete-orphan for logs
    db.session.delete(prod)
    db.session.commit()
    
    flash(f'Product "{name}" deleted.', 'info')
    return redirect(url_for('staff.products'))

@staff_bp.route('/inventory')
@login_required
@role_required('staff', 'admin')
def inventory():
    products_list = Product.query.order_by(Product.name.asc()).all()
    logs = InventoryLog.query.order_by(InventoryLog.created_at.desc()).limit(100).all()
    
    # Calculate low stock count
    low_stock_count = sum(1 for p in products_list if p.stock < 5)
    out_of_stock_count = sum(1 for p in products_list if p.stock == 0)
    
    return render_template('staff/inventory.html', 
                           products=products_list, 
                           logs=logs,
                           low_stock_count=low_stock_count,
                           out_of_stock_count=out_of_stock_count)

@staff_bp.route('/inventory/adjust', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def adjust_stock():
    product_id = request.form.get('product_id', type=int)
    adjustment = request.form.get('quantity', type=int)
    action = request.form.get('action', 'Restocked') # 'Restocked', 'Damaged', 'Lost'
    notes = request.form.get('notes', '')
    
    prod = Product.query.get_or_404(product_id)
    
    # Calculate adjusted stock
    prod.stock += adjustment
    if prod.stock < 0:
        prod.stock = 0
    prod.update_status()
    
    # Log details
    log = InventoryLog(
        product_id=prod.id,
        action=action,
        quantity=adjustment,
        notes=notes or f"Manual adjustments: {action}"
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'Inventory for "{prod.name}" adjusted by {adjustment}. New stock: {prod.stock}', 'success')
    return redirect(url_for('staff.inventory'))

@staff_bp.route('/orders')
@login_required
@role_required('staff', 'admin')
def orders():
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('staff/orders.html', orders=all_orders)

@staff_bp.route('/orders/status/<int:order_id>', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    order.order_status = new_status
    db.session.commit()
    
    flash(f'Order #{order.id} status updated to {new_status}.', 'success')
    return redirect(url_for('staff.orders'))

@staff_bp.route('/rentals')
@login_required
@role_required('staff', 'admin')
def rentals():
    all_rentals = Rental.query.order_by(Rental.rent_date.desc()).all()
    
    # Check late status of active rentals dynamically
    for r in all_rentals:
        r.update_late_status()
        
    return render_template('staff/rentals.html', rentals=all_rentals)

@staff_bp.route('/rentals/status/<int:rental_id>', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def update_rental_status(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    action = request.form.get('action') # 'approve' (pick up), 'return'
    
    if action == 'approve':
        rental.rental_status = 'Active'
        rental.rent_date = datetime.utcnow()
        rental.calculate_expected_return()
        
        # Log inventory transition
        log = InventoryLog(
            product_id=rental.product_id,
            action='Rented',
            quantity=0, # Already decremented on checkout checkout
            notes=f"Rental #{rental.id} picked up (marked Active)"
        )
        db.session.add(log)
        db.session.commit()
        flash(f'Rental #{rental.id} has been picked up. Status set to Active.', 'success')
        
    elif action == 'return':
        now = datetime.utcnow()
        late_fee = rental.calculate_late_fee(now)
        
        rental.return_date = now
        rental.rental_status = 'Returned'
        rental.late_fee = late_fee
        
        # Replenish stock
        product = Product.query.get(rental.product_id)
        if product:
            product.stock += 1
            product.update_status()
            
            # Create Inventory Log
            log = InventoryLog(
                product_id=product.id,
                action='Returned',
                quantity=1,
                notes=f"Rental #{rental.id} return checkin"
            )
            db.session.add(log)
            
        db.session.commit()
        if late_fee > 0:
            flash(f'Rental #{rental.id} returned. LATE FEE APPLIED: ${late_fee:.2f}', 'warning')
        else:
            flash(f'Rental #{rental.id} returned successfully on time.', 'success')
            
    return redirect(url_for('staff.rentals'))
