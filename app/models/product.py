from datetime import datetime
from app.extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # e.g., Dresses, Tops, Bottoms, Outerwear
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Selling price
    rental_price = db.Column(db.Numeric(10, 2), nullable=False)  # Base rental price per day
    stock = db.Column(db.Integer, nullable=False, default=0)
    size = db.Column(db.String(20), nullable=False)  # e.g., XS, S, M, L, XL
    image_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Available')  # 'Available', 'Low Stock', 'Out of Stock'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    rentals = db.relationship('Rental', backref='product', lazy=True)
    inventory_logs = db.relationship('InventoryLog', backref='product', lazy=True, cascade='all, delete-orphan')

    def update_status(self):
        if self.stock <= 0:
            self.status = 'Out of Stock'
        elif self.stock < 5:
            self.status = 'Low Stock'
        else:
            self.status = 'Available'

    def __repr__(self):
        return f'<Product {self.name} - Size {self.size}>'
