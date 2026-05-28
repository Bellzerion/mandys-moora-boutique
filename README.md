# Mandy's Moora Fashion Boutique

A premium web-based fashion boutique platform offering e-commerce, clothing rentals, inventory logging, and business analytics. Built with a luxury minimalist aesthetic (matte black, soft pink, and white) inspired by high-end brands.

## Features

* **Customer Portal**: Browse products, add to cart, choose between buying or renting (with dynamic duration discounts), and checkout.
* **Staff Dashboard**: Manage product catalog, handle inventory updates with automatic logging, process orders, and manage rental returns (including late fee calculation).
* **Admin Analytics**: View business performance with interactive charts showing revenue, rental vs. sales distribution, top products, and low stock alerts.
* **Luxury UI**: Built with Tailwind CSS and custom animations for a premium shopping experience.

## Tech Stack

* **Backend**: Python, Flask
* **ORM**: SQLAlchemy for database interactions
* **Frontend**: HTML/Jinja2, Tailwind CSS, Vanilla JS, Chart.js
* **Database**: MySQL via XAMPP (Development) (SQLite optional for quick tests)

## Local Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
   cd mandys_moora
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   * Windows: `venv\Scripts\activate`
   * Mac/Linux: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   Create a `.env` file in the root directory and add the following:
   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-super-secret-key
   DATABASE_URL=mysql+pymysql://username:password@localhost/mandys_moora_db
   ```

6. **Initialize the database and seed data**
   ```bash
   python seed.py
   ```
   *(This will create the database and populate it with sample products, users, and mock sales data).*

7. **Run the application**
   ```bash
   flask run
   ```

8. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:5000`

## Demo Accounts

* **Admin**: admin@moora.com / admin123
* **Staff**: staff@moora.com / staff123
* **Customer**: customer@moora.com / customer123
