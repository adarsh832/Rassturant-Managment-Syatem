from app import create_app, db
from app.models import User, MenuItem
from werkzeug.security import generate_password_hash

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if admin user exists
        if not User.query.filter_by(username='admin').first():
            # Create admin user
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                name='Admin User',
                role='admin',
                email='admin@example.com',
                phone='1234567890'
            )
            db.session.add(admin)
            
            # Add some sample menu items
            sample_items = [
                MenuItem(
                    name='Burger',
                    description='Classic beef burger with cheese',
                    price=199.00,
                    category='Main Course'
                ),
                MenuItem(
                    name='Caesar Salad',
                    description='Fresh romaine lettuce with caesar dressing',
                    price=149.00,
                    category='Starters'
                ),
                MenuItem(
                    name='Chocolate Cake',
                    description='Rich chocolate cake with frosting',
                    price=99.00,
                    category='Desserts'
                )
            ]
            db.session.bulk_save_objects(sample_items)
            
            db.session.commit()
            print('Database initialized with admin user and sample menu items!')

if __name__ == '__main__':
    init_db()  # Initialize database and add sample data
    app.run(debug=True)