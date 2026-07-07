from app import create_app, db
from models.user import User, Role
from models.financial import Category

def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create roles
        roles = ['Super Administrateur', 'Utilisateur Standard', 'Utilisateur Lecture Seule', 'Simple Invité']
        for r_name in roles:
            if not Role.query.filter_by(name=r_name).first():
                role = Role(name=r_name)
                db.session.add(role)
        
        db.session.commit()
        
        # Create super admin
        admin_role = Role.query.filter_by(name='Super Administrateur').first()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', role_id=admin_role.id)
            admin.set_password('admin123')
            db.session.add(admin)
            
        # Create categories
        categories = [
            ('Cotisations', 'Income'),
            ('Contributions', 'Income'),
            ('Dons', 'Income'),
            ('Subventions', 'Income'),
            ('Location salle', 'Expense'),
            ('Impression', 'Expense'),
            ('Café', 'Expense'),
            ('Internet', 'Expense'),
            ('Eau', 'Expense'),
            ('Electricité', 'Expense'),
            ('Transport', 'Expense')
        ]
        for name, entry_type in categories:
            if not Category.query.filter_by(name=name).first():
                cat = Category(name=name, type=entry_type)
                db.session.add(cat)
                
        db.session.commit()
        print("Database seeded!")

if __name__ == '__main__':
    seed()
