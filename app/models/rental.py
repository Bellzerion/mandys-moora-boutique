from datetime import datetime, timedelta
from app.extensions import db

class Rental(db.Model):
    __tablename__ = 'rentals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rental_days = db.Column(db.Integer, nullable=False)  # 3, 7, or 14 days
    rental_fee = db.Column(db.Numeric(10, 2), nullable=False)
    rental_status = db.Column(db.String(30), nullable=False, default='Pending')  # 'Pending', 'Active', 'Returned', 'Late'
    rent_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_return_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    late_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)

    def calculate_expected_return(self):
        if self.rent_date:
            self.expected_return_date = self.rent_date + timedelta(days=self.rental_days)

    def calculate_late_fee(self, actual_return_date=None):
        if not actual_return_date:
            actual_return_date = datetime.utcnow()
            
        if actual_return_date <= self.expected_return_date:
            return 0.0
            
        # Calculate full days difference
        diff = actual_return_date - self.expected_return_date
        late_days = diff.days
        
        # 1 day grace period: if difference is less than or equal to 1 day, no late fee is charged
        if late_days <= 1:
            return 0.0
            
        # Daily rate = rental_fee / rental_days
        daily_rate = float(self.rental_fee) / self.rental_days
        # Double the daily rate per late day
        total_late_fee = late_days * (daily_rate * 2)
        return round(total_late_fee, 2)

    def update_late_status(self):
        if self.rental_status == 'Active' and datetime.utcnow() > (self.expected_return_date + timedelta(days=1)):
            self.rental_status = 'Late'
            db.session.commit()

    def __repr__(self):
        return f'<Rental Product #{self.product_id} by User #{self.user_id} - {self.rental_status}>'
