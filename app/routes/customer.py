from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_file
from flask_login import login_required, current_user
from datetime import datetime
import io
from fpdf import FPDF
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.rental import Rental
from app.models.inventory_log import InventoryLog

customer_bp = Blueprint('customer', __name__)

def calculate_rental_fee(daily_rate, days):
    rate = float(daily_rate)
    total = rate * days
    if days == 7:
        total *= 0.90  # 10% off
    elif days == 14:
        total *= 0.80  # 20% off
    return round(total, 2)

@customer_bp.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total_buy = 0.0
    total_rent = 0.0
    
    for key, item in cart.items():
        product = Product.query.get(item['product_id'])
        if not product:
            continue
            
        if item['type'] == 'buy':
            price = float(product.price)
            subtotal = price * item['quantity']
            total_buy += subtotal
        else:
            price = calculate_rental_fee(product.rental_price, item['duration'])
            subtotal = price * item['quantity']
            total_rent += subtotal
            
        cart_items.append({
            'key': key,
            'product': product,
            'type': item['type'],
            'quantity': item['quantity'],
            'duration': item.get('duration', 0),
            'price': price,
            'subtotal': subtotal
        })
        
    grand_total = total_buy + total_rent
    return render_template('customer/cart.html', cart_items=cart_items, total_buy=total_buy, total_rent=total_rent, grand_total=grand_total)

@customer_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    action_type = request.form.get('action_type', 'buy')  # 'buy' or 'rent'
    duration = request.form.get('rental_duration', type=int, default=3)  # 3, 7, 14
    qty = request.form.get('quantity', type=int, default=1)
    
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        flash('Sorry, this item is currently out of stock.', 'warning')
        return redirect(url_for('main.product_details', product_id=product_id))
        
    cart = session.get('cart', {})
    
    if action_type == 'buy':
        key = f"buy_{product_id}"
        price = float(product.price)
    else:
        key = f"rent_{product_id}_{duration}"
        price = calculate_rental_fee(product.rental_price, duration)
        
    if key in cart:
        cart[key]['quantity'] += qty
    else:
        cart[key] = {
            'product_id': product_id,
            'type': action_type,
            'quantity': qty,
            'duration': duration,
            'price': price
        }
        
    session['cart'] = cart
    session.modified = True
    flash(f'{product.name} added to cart.', 'success')
    return redirect(url_for('customer.view_cart'))

@customer_bp.route('/cart/remove/<string:key>', methods=['POST'])
def remove_from_cart(key):
    cart = session.get('cart', {})
    if key in cart:
        cart.pop(key)
        session['cart'] = cart
        session.modified = True
        flash('Item removed from cart.', 'info')
    return redirect(url_for('customer.view_cart'))

@customer_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    session['cart'] = {}
    session.modified = True
    flash('Cart cleared.', 'info')
    return redirect(url_for('customer.view_cart'))

@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('main.shop'))
        
    cart_items = []
    total_buy = 0.0
    total_rent = 0.0
    
    for key, item in cart.items():
        product = Product.query.get(item['product_id'])
        if not product:
            continue
        if item['type'] == 'buy':
            price = float(product.price)
            subtotal = price * item['quantity']
            total_buy += subtotal
        else:
            price = calculate_rental_fee(product.rental_price, item['duration'])
            subtotal = price * item['quantity']
            total_rent += subtotal
            
        cart_items.append({
            'key': key,
            'product': product,
            'type': item['type'],
            'quantity': item['quantity'],
            'duration': item.get('duration', 0),
            'price': price,
            'subtotal': subtotal
        })
        
    grand_total = total_buy + total_rent
    
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        address = request.form.get('address')
        city = request.form.get('city')
        zipcode = request.form.get('zipcode')
        payment_method = request.form.get('payment_method', 'Credit Card')
        
        # Verify stock
        insufficient_stock = False
        for item in cart_items:
            product = item['product']
            # For rentals, quantity refers to total items checkin, let's check
            required_qty = item['quantity']
            if product.stock < required_qty:
                flash(f'Insufficient stock for {product.name}. Available: {product.stock}', 'danger')
                insufficient_stock = True
        
        if insufficient_stock:
            return redirect(url_for('customer.view_cart'))
            
        purchase_items = [x for x in cart_items if x['type'] == 'buy']
        rental_items = [x for x in cart_items if x['type'] == 'rent']
        
        # 1. Process standard orders
        if purchase_items:
            order = Order(
                user_id=current_user.id,
                total_amount=total_buy,
                order_status='Pending',
                payment_method=payment_method
            )
            db.session.add(order)
            db.session.commit()
            
            for item in purchase_items:
                product = item['product']
                sub = item['subtotal']
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item['quantity'],
                    subtotal=sub
                )
                db.session.add(order_item)
                
                # Reduce stock
                product.stock -= item['quantity']
                product.update_status()
                
                # Log stock adjustment
                log = InventoryLog(
                    product_id=product.id,
                    action='Sold',
                    quantity=-item['quantity'],
                    notes=f"Order #{order.id} purchase"
                )
                db.session.add(log)
            db.session.commit()
            
        # 2. Process rentals
        if rental_items:
            for item in rental_items:
                product = item['product']
                for _ in range(item['quantity']):
                    rent = Rental(
                        user_id=current_user.id,
                        product_id=product.id,
                        rental_days=item['duration'],
                        rental_fee=item['price'],
                        rental_status='Pending',
                        rent_date=datetime.utcnow()
                    )
                    rent.calculate_expected_return()
                    db.session.add(rent)
                    
                    product.stock -= 1
                    product.update_status()
                    
                    log = InventoryLog(
                        product_id=product.id,
                        action='Rented',
                        quantity=-1,
                        notes=f"Rental pending pickup"
                    )
                    db.session.add(log)
            db.session.commit()
            
        session['cart'] = {}
        session.modified = True
        
        flash('Checkout complete! Order details saved.', 'success')
        return redirect(url_for('customer.order_history'))
        
    return render_template('customer/checkout.html', cart_items=cart_items, grand_total=grand_total)

@customer_bp.route('/orders')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    rentals = Rental.query.filter_by(user_id=current_user.id).order_by(Rental.rent_date.desc()).all()
    
    # Dynamically update late status
    for r in rentals:
        r.update_late_status()
        
    return render_template('customer/order_history.html', orders=orders, rentals=rentals)

@customer_bp.route('/order/<int:order_id>/invoice')
@login_required
def download_invoice(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('customer.order_history'))
        
    class PDF(FPDF):
        def header(self):
            self.set_font('helvetica', 'B', 20)
            self.cell(0, 10, "Mandy's Moora Boutique", ln=True, align='C')
            self.set_font('helvetica', 'I', 10)
            self.cell(0, 10, 'Luxury Fashion & Rentals', ln=True, align='C')
            self.ln(10)
            
        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', align='C')

    pdf = PDF()
    pdf.add_page()
    
    # Invoice Details
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, f'INVOICE #{order.id}', ln=True)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 8, f'Date: {order.created_at.strftime("%Y-%m-%d %H:%M")}', ln=True)
    pdf.cell(0, 8, f'Customer: {current_user.fullname} ({current_user.email})', ln=True)
    pdf.cell(0, 8, f'Status: {order.order_status}', ln=True)
    pdf.cell(0, 8, f'Payment Method: {order.payment_method}', ln=True)
    pdf.ln(10)
    
    # Table Header
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(100, 10, 'Item', border=1)
    pdf.cell(30, 10, 'Qty', border=1, align='C')
    pdf.cell(60, 10, 'Subtotal', border=1, align='R')
    pdf.ln(10)
    
    # Items
    pdf.set_font('helvetica', '', 10)
    for item in order.items:
        pdf.cell(100, 10, item.product.name, border=1)
        pdf.cell(30, 10, str(item.quantity), border=1, align='C')
        pdf.cell(60, 10, f'${float(item.subtotal):,.2f}', border=1, align='R')
        pdf.ln(10)
        
    # Total
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(130, 10, 'Total:', border=1, align='R')
    pdf.cell(60, 10, f'${float(order.total_amount):,.2f}', border=1, align='R')
    
    # Return PDF
    pdf_bytes = pdf.output()
    return send_file(
        io.BytesIO(pdf_bytes),
        as_attachment=True,
        download_name=f'invoice_{order.id}.pdf',
        mimetype='application/pdf'
    )

@customer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check duplicate emails
        dupe = User.query.filter_by(email=email.lower()).first()
        if dupe and dupe.id != current_user.id:
            flash('Email already in use.', 'danger')
            return redirect(url_for('customer.profile'))
            
        current_user.fullname = fullname
        current_user.email = email.lower()
        if password:
            current_user.set_password(password)
            
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('customer.profile'))
        
    return render_template('customer/profile.html')
