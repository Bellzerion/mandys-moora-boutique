from app.extensions import login_manager
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.rental import Rental
from app.models.inventory_log import InventoryLog

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
