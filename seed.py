import os
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.rental import Rental
from app.models.inventory_log import InventoryLog

def seed_db():
    app = create_app()
    with app.app_context():
        print("Recreating database tables...")
        db.drop_all()
        db.create_all()
        
        # 1. Create Users
        print("Seeding users...")
        admin = User(fullname="Mandy Moora", email="admin@moora.com", role="admin")
        admin.set_password("admin123")
        
        staff = User(fullname="Sarah Jenkins", email="staff@moora.com", role="staff")
        staff.set_password("staff123")
        
        customer1 = User(fullname="Elena Rostova", email="customer@moora.com", role="customer")
        customer1.set_password("customer123")

        customer2 = User(fullname="Sophia Loren", email="sophia@moora.com", role="customer")
        customer2.set_password("customer123")

        customer3 = User(fullname="Olivia Wilde", email="olivia@moora.com", role="customer")
        customer3.set_password("customer123")
        
        db.session.add_all([admin, staff, customer1, customer2, customer3])
        db.session.commit()
        
        # 2. Create Products
        print("Seeding luxury products...")
        products_data = [
            {
                "name": "Elysian Silk Slip Dress",
                "description": "A stunning 100% mulberry silk slip dress with a cowl neckline and an elegant low back. Perfect for formal evenings or luxury lounging.",
                "category": "Dresses",
                "price": 280.00,
                "rental_price": 35.00,
                "stock": 12,
                "size": "M",
                "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=600&auto=format&fit=crop"
            },
            {
                "name": "Elysian Silk Slip Dress (S)",
                "description": "A stunning 100% mulberry silk slip dress with a cowl neckline and an elegant low back. Size S.",
                "category": "Dresses",
                "price": 280.00,
                "rental_price": 35.00,
                "stock": 3,
                "size": "S",
                "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=600&auto=format&fit=crop"
            },
            {
                "name": "Belgrave Cashmere Trench",
                "description": "Double-breasted trench coat crafted from ultra-soft Mongolian cashmere. Featuring structured shoulders and a self-tie belt.",
                "category": "Outerwear",
                "price": 650.00,
                "rental_price": 75.00,
                "stock": 4,
                "size": "L",
                "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=600&auto=format&fit=crop"
            },
            {
                "name": "Siren Lace Jumpsuit",
                "description": "Tailored wide-leg jumpsuit with an intricate French lace bodice and sheer sleeves. Designed for a sleek, lengthening silhouette.",
                "category": "Jumpsuits",
                "price": 340.00,
                "rental_price": 45.00,
                "stock": 8,
                "size": "S",
                "image_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=600&auto=format&fit=crop"
            },
            {
                "name": "Aura Linen Blazer",
                "description": "Relaxed-fit unstructured blazer in natural ivory linen. Breathable yet structured, ideal for transitional tailoring.",
                "category": "Outerwear",
                "price": 195.00,
                "rental_price": 25.00,
                "stock": 0,
                "size": "M",
                "image_url": "https://images.unsplash.com/photo-1548624149-f7b3be68e373?q=80&w=600&auto=format&fit=crop"
            },
            {
                "name": "Noir Asymmetric Top",
                "description": "One-shoulder top in heavy-weight crepe with a sculptural drape. Double-lined with a concealed side zipper.",
                "category": "Tops",
                "price": 120.00,
                "rental_price": 15.00,
                "stock": 15,
                "size": "S",
                "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=600&auto=format&fit=crop"
            },
            {
                "name": "Satin Palazzo Pants",
                "description": "High-rise, wide-leg trousers in flowing matte satin. Features discreet side pockets and a comfortable elasticated back waistband.",
                "category": "Bottoms",
                "price": 160.00,
                "rental_price": 20.00,
                "stock": 10,
                "size": "M",
                "image_url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?q=80&w=600&auto=format&fit=crop"
            },
            {
                "name": "Pearl Drop Statement Earrings",
                "description": "Handcrafted Baroque freshwater pearls suspended from 18k gold-plated brass hoops. Every pair is completely unique.",
                "category": "Accessories",
                "price": 85.00,
                "rental_price": 10.00,
                "stock": 25,
                "size": "One Size",
                "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?q=80&w=600&auto=format&fit=crop"
            },
            {
                "name": "Valerie Velvet Corset Dress",
                "description": "Corseted bodice dress in rich midnight-black velvet. Structured boning provides lift, while the skirt features a subtle thigh-high split.",
                "category": "Dresses",
                "price": 420.00,
                "rental_price": 60.00,
                "stock": 6,
                "size": "S",
                "image_url": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?q=80&w=600&auto=format&fit=crop"
            },
            {
                "name": "Luxe Knit Lounge Cardigan",
                "description": "Oversized, chunky cardigan in a premium alpaca and wool blend. Cozy ribbed cuffs and tortoiseshell-effect buttons.",
                "category": "Outerwear",
                "price": 210.00,
                "rental_price": 25.00,
                "stock": 9,
                "size": "M",
                "image_url": "https://images.unsplash.com/photo-1574169208507-84376144848b?q=80&w=600&auto=format&fit=crop"
            }
        ]
        
        seeded_products = []
        for p in products_data:
            prod = Product(
                name=p["name"],
                description=p["description"],
                category=p["category"],
                price=p["price"],
                rental_price=p["rental_price"],
                stock=p["stock"],
                size=p["size"],
                image_url=p["image_url"]
            )
            prod.update_status()
            db.session.add(prod)
            seeded_products.append(prod)
        db.session.commit()
        
        # Log inventory creation
        for p in seeded_products:
            log = InventoryLog(
                product_id=p.id,
                action="Created",
                quantity=p.stock,
                notes="Initial database seeding"
            )
            db.session.add(log)
        db.session.commit()
        
        # 3. Create Orders (Sales)
        print("Seeding purchase orders...")
        now = datetime.utcnow()
        order_dates = [
            now - timedelta(days=25),
            now - timedelta(days=20),
            now - timedelta(days=18),
            now - timedelta(days=15),
            now - timedelta(days=12),
            now - timedelta(days=10),
            now - timedelta(days=7),
            now - timedelta(days=5),
            now - timedelta(days=3),
            now - timedelta(days=1),
        ]
        
        for i, date in enumerate(order_dates):
            cust = customer1 if i % 2 == 0 else customer2
            if i % 3 == 0: cust = customer3
            
            p1 = seeded_products[i % len(seeded_products)]
            p2 = seeded_products[(i + 2) % len(seeded_products)]
            
            qty1, qty2 = 1, 1
            sub1 = p1.price * qty1
            sub2 = p2.price * qty2
            total = sub1 + sub2
            
            order = Order(
                user_id=cust.id,
                total_amount=total,
                order_status="Delivered" if i < 7 else "Processing",
                payment_method="Credit Card" if i % 2 == 0 else "Cash on Delivery",
                created_at=date
            )
            db.session.add(order)
            db.session.commit()
            
            item1 = OrderItem(order_id=order.id, product_id=p1.id, quantity=qty1, subtotal=sub1)
            item2 = OrderItem(order_id=order.id, product_id=p2.id, quantity=qty2, subtotal=sub2)
            db.session.add_all([item1, item2])
            
            # Log stock decrement
            log1 = InventoryLog(product_id=p1.id, action="Sold", quantity=-qty1, created_at=date, notes=f"Order #{order.id} purchase")
            log2 = InventoryLog(product_id=p2.id, action="Sold", quantity=-qty2, created_at=date, notes=f"Order #{order.id} purchase")
            db.session.add_all([log1, log2])
            
        db.session.commit()
        
        # 4. Create Rentals
        print("Seeding rentals...")
        rental_records = [
            {
                "user": customer1,
                "product": seeded_products[0],
                "days": 7,
                "fee": float(seeded_products[0].rental_price) * 7 * 0.9,
                "status": "Returned",
                "rent_offset": 28,
                "return_offset": 21
            },
            {
                "user": customer2,
                "product": seeded_products[3],
                "days": 3,
                "fee": float(seeded_products[3].rental_price) * 3,
                "status": "Returned",
                "rent_offset": 20,
                "return_offset": 17
            },
            {
                "user": customer3,
                "product": seeded_products[6],
                "days": 7,
                "fee": float(seeded_products[6].rental_price) * 7 * 0.9,
                "status": "Active",
                "rent_offset": 4,
                "return_offset": None
            },
            {
                "user": customer1,
                "product": seeded_products[1],
                "days": 7,
                "fee": float(seeded_products[1].rental_price) * 7 * 0.9,
                "status": "Late",
                "rent_offset": 12,
                "return_offset": None
            },
            {
                "user": customer2,
                "product": seeded_products[8],
                "days": 14,
                "fee": float(seeded_products[8].rental_price) * 14 * 0.8,
                "status": "Pending",
                "rent_offset": 0,
                "return_offset": None
            }
        ]
        
        for rent in rental_records:
            rent_date = now - timedelta(days=rent["rent_offset"])
            expected = rent_date + timedelta(days=rent["days"])
            
            actual_return = None
            late_fee_val = 0.0
            if rent["return_offset"] is not None:
                actual_return = now - timedelta(days=rent["return_offset"])
                
            rental = Rental(
                user_id=rent["user"].id,
                product_id=rent["product"].id,
                rental_days=rent["days"],
                rental_fee=rent["fee"],
                rental_status=rent["status"],
                rent_date=rent_date,
                expected_return_date=expected,
                return_date=actual_return,
                late_fee=late_fee_val
            )
            
            if rent["status"] == "Late":
                daily_rate = float(rental.rental_fee) / rental.rental_days
                rental.late_fee = round(5 * (daily_rate * 2), 2)
                
            db.session.add(rental)
            db.session.commit()
            
            if rent["status"] in ["Active", "Late"]:
                log = InventoryLog(
                    product_id=rent["product"].id,
                    action="Rented",
                    quantity=-1,
                    created_at=rent_date,
                    notes=f"Rental #{rental.id} checkout"
                )
                db.session.add(log)
            elif rent["status"] == "Returned":
                log1 = InventoryLog(
                    product_id=rent["product"].id,
                    action="Rented",
                    quantity=-1,
                    created_at=rent_date,
                    notes=f"Rental #{rental.id} checkout"
                )
                log2 = InventoryLog(
                    product_id=rent["product"].id,
                    action="Returned",
                    quantity=1,
                    created_at=actual_return,
                    notes=f"Rental #{rental.id} return checkin"
                )
                db.session.add_all([log1, log2])
        
        db.session.commit()
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_db()
