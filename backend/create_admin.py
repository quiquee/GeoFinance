#!/usr/bin/env python3
"""
Script to create an admin user in the GeoFinance application
"""
from app import create_app
from models.user import User
from models.base import db

def create_admin_user(username='admin', password='admin123', name='Administrator'):
    """Create an admin user if one doesn't exist already"""
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username=username).first()
        if admin:
            print(f"Admin user '{username}' already exists. Use this username to log in.")
            return
        
        # Create new admin user
        admin = User(username=username, name=name, role='admin')
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("You can now log in with these credentials.")

if __name__ == '__main__':
    create_admin_user()