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
                    name='Butter Chicken',
                    description='Creamy curry with tender chicken',
                    price=299.00,
                    category='Main Course'
                ),
                MenuItem(
                    name='Paneer Tikka',
                    description='Grilled cottage cheese with spices',
                    price=199.00,
                    category='Starters'
                ),
                MenuItem(
                    name='Gulab Jamun',
                    description='Sweet milk dumplings',
                    price=99.00,
                    category='Desserts'
                ),
                MenuItem(
                    name='Masala Dosa',
                    description='Crispy crepe with spiced potato filling',
                    price=149.00,
                    category='South Indian'
                ),
                MenuItem(
                    name='Biryani',
                    description='Fragrant rice with spices and meat/vegetables',
                    price=249.00,
                    category='Main Course'
                ),
                MenuItem(
                    name='Mango Lassi',
                    description='Sweet yogurt drink with mango',
                    price=79.00,
                    category='Beverages'
                )
            ]
            db.session.bulk_save_objects(sample_items)
            
            db.session.commit()
            print('Database initialized with admin user and sample menu items!')

if __name__ == '__main__':
    init_db()  # Initialize database and add sample data
    app.run(debug=True)