from sqlalchemy import func
from datetime import datetime, timedelta
from app.extensions import db
from app.models.order import Order, OrderItem
from app.models.rental import Rental
from app.models.product import Product

def get_dashboard_metrics():
    """
    Computes business intelligence analytics for Mandy's Moora.
    """
    # 1. Total Revenue
    total_sales = db.session.query(func.sum(Order.total_amount)).scalar() or 0.0
    total_rentals_fee = db.session.query(func.sum(Rental.rental_fee)).scalar() or 0.0
    total_late_fee = db.session.query(func.sum(Rental.late_fee)).scalar() or 0.0
    total_rent = total_rentals_fee + total_late_fee
    
    total_revenue = float(total_sales) + float(total_rent)
    
    # 2. Key Stock Alerts
    low_stock = Product.query.filter(Product.stock < 5, Product.stock > 0).count()
    out_of_stock = Product.query.filter(Product.stock == 0).count()
    active_rentals = Rental.query.filter(Rental.rental_status.in_(['Active', 'Late'])).count()
    
    # 3. Monthly Chart Data (Last 6 months)
    now = datetime.utcnow()
    six_months_ago = now - timedelta(days=180)
    
    orders = Order.query.filter(Order.created_at >= six_months_ago).all()
    rentals = Rental.query.filter(Rental.rent_date >= six_months_ago).all()
    
    monthly_data = {}
    # Build last 6 months keys
    for i in range(5, -1, -1):
        month_start = now - timedelta(days=i*30)
        month_key = month_start.strftime("%b %Y")
        monthly_data[month_key] = {"sales": 0.0, "rentals": 0.0}
        
    for o in orders:
        mkey = o.created_at.strftime("%b %Y")
        if mkey in monthly_data:
            monthly_data[mkey]["sales"] += float(o.total_amount)
            
    for r in rentals:
        mkey = r.rent_date.strftime("%b %Y")
        if mkey in monthly_data:
            monthly_data[mkey]["rentals"] += float(r.rental_fee) + float(r.late_fee)
            
    # 4. Sales and Rentals by Product Category
    cat_sales = db.session.query(
        Product.category, 
        func.sum(OrderItem.quantity)
    ).join(OrderItem).group_by(Product.category).all()
    cat_sales_dict = {cat: int(count) for cat, count in cat_sales}
    
    cat_rents = db.session.query(
        Product.category,
        func.count(Rental.id)
    ).join(Rental).group_by(Product.category).all()
    cat_rents_dict = {cat: int(count) for cat, count in cat_rents}
    
    categories = list(set(list(cat_sales_dict.keys()) + list(cat_rents_dict.keys())))
    # Default list if empty
    if not categories:
        categories = ['Dresses', 'Outerwear', 'Jumpsuits', 'Tops', 'Bottoms', 'Accessories']
        
    category_chart = {
        "labels": categories,
        "sales": [cat_sales_dict.get(c, 0) for c in categories],
        "rentals": [cat_rents_dict.get(c, 0) for c in categories]
    }
    
    # 5. Top Performing Products
    top_sold = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_qty')
    ).join(OrderItem).group_by(Product.name).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()
    
    top_rented = db.session.query(
        Product.name,
        func.count(Rental.id).label('total_rents')
    ).join(Rental).group_by(Product.name).order_by(func.count(Rental.id).desc()).limit(5).all()
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_sales": round(float(total_sales), 2),
        "total_rent": round(float(total_rent), 2),
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "active_rentals": active_rentals,
        "monthly_chart": {
            "labels": list(monthly_data.keys()),
            "sales": [round(v["sales"], 2) for v in monthly_data.values()],
            "rentals": [round(v["rentals"], 2) for v in monthly_data.values()]
        },
        "category_chart": category_chart,
        "top_sold": [{"name": name, "qty": int(qty)} for name, qty in top_sold],
        "top_rented": [{"name": name, "qty": int(qty)} for name, qty in top_rented]
    }
