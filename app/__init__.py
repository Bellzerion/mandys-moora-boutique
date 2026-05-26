import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Register routes / blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.customer import customer_bp
    from app.routes.staff import staff_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Context processor to expose cart count globally to templates
    @app.context_processor
    def inject_cart_count():
        from flask import session
        cart = session.get('cart', {})
        # cart is structured as {product_id: {type: 'buy'/'rent', quantity: int, duration: int}}
        total_items = sum(item.get('quantity', 1) for item in cart.values())
        return dict(cart_count=total_items)
        
    return app
