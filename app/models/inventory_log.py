from datetime import datetime
from app.extensions import db

class InventoryLog(db.Model):
    __tablename__ = 'inventory_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'Created', 'Restocked', 'Sold', 'Rented', 'Returned', 'Damaged'
    quantity = db.Column(db.Integer, nullable=False)  # Change in stock (positive or negative)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<InventoryLog Product #{self.product_id} - {self.action} ({self.quantity})>'
