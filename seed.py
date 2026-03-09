from app import create_app, db
from app.models.user import User
from app.models.category import Category
from datetime import datetime

app = create_app('development')

def seed_data():
    with app.app_context():

        # Create Admin User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@librarysphere.com',
                role='admin',
                is_active=True,
                created_at=datetime.utcnow()
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            print('✅ Admin user created')
        else:
            print('ℹ️  Admin already exists')

        # Create Librarian User
        librarian = User.query.filter_by(username='librarian').first()
        if not librarian:
            librarian = User(
                username='librarian',
                email='librarian@librarysphere.com',
                role='librarian',
                is_active=True,
                created_at=datetime.utcnow()
            )
            librarian.set_password('Librarian@123')
            db.session.add(librarian)
            print('✅ Librarian user created')
        else:
            print('ℹ️  Librarian already exists')

        # Create Default Categories
        categories = [
            {'name': 'Fiction', 'description': 'Fictional novels and stories'},
            {'name': 'Non-Fiction', 'description': 'Real world facts and events'},
            {'name': 'Science', 'description': 'Scientific books and research'},
            {'name': 'Technology', 'description': 'Technology and programming books'},
            {'name': 'History', 'description': 'Historical events and biographies'},
            {'name': 'Mathematics', 'description': 'Mathematics and statistics'},
            {'name': 'Literature', 'description': 'Classic and modern literature'},
            {'name': 'Business', 'description': 'Business and entrepreneurship'},
            {'name': 'Self Help', 'description': 'Personal development books'},
            {'name': 'Children', 'description': 'Books for children'},
        ]

        for cat_data in categories:
            cat = Category.query.filter_by(name=cat_data['name']).first()
            if not cat:
                cat = Category(**cat_data)
                db.session.add(cat)
                print(f"✅ Category '{cat_data['name']}' created")

        db.session.commit()
        print('\n🎉 Database seeded successfully!')
        print('\n📋 Login Credentials:')
        print('   Admin    → username: admin      | password: Admin@123')
        print('   Librarian→ username: librarian  | password: Librarian@123')

if __name__ == '__main__':
    seed_data()