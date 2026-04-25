"""
Seed database with synthetic data
"""
import os
import sys
import pandas as pd
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load .env from project root
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine, Base
from app.models import User, Product, Category, Order, OrderItem, Review, Complaint
from app.utils.security import get_password_hash

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')


def create_tables(drop_existing=True):
    """Create all database tables."""
    print("Creating database tables...")
    if drop_existing:
        print("  Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")


def seed_users(db):
    """Seed users from CSV."""
    print("\nSeeding users...")
    
    users_path = os.path.join(DATA_DIR, 'users.csv')
    if not os.path.exists(users_path):
        print(f"  ❌ Users data not found: {users_path}")
        return
    
    users_df = pd.read_csv(users_path)
    
    count = 0
    for _, row in users_df.head(100).iterrows():  # Limit to 100 for faster seeding
        # Check if user exists
        existing = db.query(User).filter(User.email == row['email']).first()
        if existing:
            continue
        
        user = User(
            id=uuid.UUID(row['id']),
            email=row['email'],
            phone=row.get('phone'),
            full_name=row['full_name'],
            password_hash=get_password_hash('password123'),  # Default password
            points=int(row.get('points', 0)),
            is_active=bool(row.get('is_active', True)),
            is_admin=bool(row.get('is_admin', False))
        )
        db.add(user)
        count += 1
    
    db.commit()
    print(f"  ✅ Seeded {count} users")


def seed_categories(db):
    """Seed categories from CSV."""
    print("\nSeeding categories...")
    
    categories_path = os.path.join(DATA_DIR, 'categories.csv')
    if not os.path.exists(categories_path):
        print(f"  ❌ Categories data not found: {categories_path}")
        return
    
    categories_df = pd.read_csv(categories_path)
    
    count = 0
    for _, row in categories_df.iterrows():
        existing = db.query(Category).filter(Category.slug == row['slug']).first()
        if existing:
            continue
        
        category = Category(
            id=uuid.UUID(row['id']),
            name=row['name'],
            name_en=row.get('name_en'),
            slug=row['slug'],
            sort_order=int(row.get('sort_order', 0)),
            is_active=True
        )
        db.add(category)
        count += 1
    
    db.commit()
    print(f"  ✅ Seeded {count} categories")


def seed_products(db):
    """Seed products from CSV."""
    print("\nSeeding products...")
    
    products_path = os.path.join(DATA_DIR, 'products.csv')
    if not os.path.exists(products_path):
        print(f"  ❌ Products data not found: {products_path}")
        return
    
    products_df = pd.read_csv(products_path)
    
    # Drop duplicates based on SKU
    products_df = products_df.drop_duplicates(subset=['sku'], keep='first')
    
    count = 0
    seen_skus = set()
    for _, row in products_df.head(200).iterrows():  # Limit to 200
        existing = db.query(Product).filter(Product.slug == row['slug']).first()
        if existing:
            continue
        
        # Skip duplicate SKUs
        sku = row.get('sku')
        if sku in seen_skus:
            continue
        seen_skus.add(sku)
        
        product = Product(
            id=uuid.UUID(row['id']),
            name=row['name'],
            name_en=row.get('name_en'),
            slug=row['slug'],
            description=row.get('description'),
            category_id=uuid.UUID(row['category_id']) if pd.notna(row.get('category_id')) else None,
            brand=row.get('brand'),
            sku=sku,
            barcode=row.get('barcode'),
            price=float(row['price']),
            discount_price=float(row['discount_price']) if pd.notna(row.get('discount_price')) else None,
            discount_percent=int(row['discount_percent']) if pd.notna(row.get('discount_percent')) else None,
            stock_quantity=int(row.get('stock_quantity', 0)),
            unit=row.get('unit', 'ədəd'),
            is_active=True,
            is_featured=bool(row.get('is_featured', False)),
            view_count=int(row.get('view_count', 0)),
            sold_count=int(row.get('sold_count', 0)),
            avg_rating=float(row.get('avg_rating', 0)),
            review_count=int(row.get('review_count', 0))
        )
        db.add(product)
        count += 1
    
    db.commit()
    print(f"  ✅ Seeded {count} products")


def seed_reviews(db):
    """Seed reviews from CSV."""
    print("\nSeeding reviews...")
    
    reviews_path = os.path.join(DATA_DIR, 'reviews.csv')
    if not os.path.exists(reviews_path):
        print(f"  ❌ Reviews data not found: {reviews_path}")
        return
    
    reviews_df = pd.read_csv(reviews_path)
    
    # Get existing user and product IDs
    user_ids = set(str(u.id) for u in db.query(User).all())
    product_ids = set(str(p.id) for p in db.query(Product).all())
    
    count = 0
    for _, row in reviews_df.head(200).iterrows():
        # Skip if user or product doesn't exist
        if row['user_id'] not in user_ids or row['product_id'] not in product_ids:
            continue
        
        review = Review(
            id=uuid.UUID(row['id']),
            user_id=uuid.UUID(row['user_id']),
            product_id=uuid.UUID(row['product_id']),
            rating=int(row['rating']),
            comment=row.get('comment'),
            sentiment=row.get('sentiment'),
            sentiment_score=int(row['sentiment_score']) if pd.notna(row.get('sentiment_score')) else None,
            is_verified_purchase=bool(row.get('is_verified_purchase', False)),
            is_approved=True,
            helpful_count=int(row.get('helpful_count', 0))
        )
        db.add(review)
        count += 1
    
    db.commit()
    print(f"  ✅ Seeded {count} reviews")


def seed_complaints(db):
    """Seed complaints from CSV."""
    print("\nSeeding complaints...")
    
    complaints_path = os.path.join(DATA_DIR, 'complaints.csv')
    if not os.path.exists(complaints_path):
        print(f"  ❌ Complaints data not found: {complaints_path}")
        return
    
    complaints_df = pd.read_csv(complaints_path)
    
    # Get existing user IDs
    user_ids = set(str(u.id) for u in db.query(User).all())
    
    count = 0
    for _, row in complaints_df.head(100).iterrows():
        if row['user_id'] not in user_ids:
            continue
        
        complaint = Complaint(
            id=uuid.UUID(row['id']),
            ticket_number=row['ticket_number'],
            user_id=uuid.UUID(row['user_id']),
            category=row['category'],
            priority=row['priority'],
            subject=row.get('subject', row['description'][:50]),
            description=row['description'],
            status=row.get('status', 'pending')
        )
        db.add(complaint)
        count += 1
    
    db.commit()
    print(f"  ✅ Seeded {count} complaints")


def create_admin_user(db):
    """Create default admin user."""
    print("\nCreating admin user...")
    
    admin_email = "admin@oba.az"
    existing = db.query(User).filter(User.email == admin_email).first()
    
    if existing:
        print(f"  Admin user already exists: {admin_email}")
        return
    
    admin = User(
        email=admin_email,
        phone="+994501234567",
        full_name="Admin User",
        password_hash=get_password_hash("admin123"),
        is_active=True,
        is_admin=True,
        points=0
    )
    db.add(admin)
    db.commit()
    
    print(f"  ✅ Created admin user:")
    print(f"     Email: {admin_email}")
    print(f"     Password: admin123")


def main():
    """Seed database with all data."""
    print("\n" + "="*60)
    print("OBA Smart Assistant - Database Seeder")
    print("="*60)
    
    # Check if data exists
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ Data directory not found: {DATA_DIR}")
        print("   Run generate_data.py first!")
        return
    
    # Create tables
    create_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Seed data
        create_admin_user(db)
        seed_users(db)
        seed_categories(db)
        seed_products(db)
        seed_reviews(db)
        seed_complaints(db)
        
        print("\n" + "="*60)
        print("✅ Database seeded successfully!")
        print("="*60)
        
        # Print summary
        print("\nDatabase Summary:")
        print(f"  - Users: {db.query(User).count()}")
        print(f"  - Categories: {db.query(Category).count()}")
        print(f"  - Products: {db.query(Product).count()}")
        print(f"  - Reviews: {db.query(Review).count()}")
        print(f"  - Complaints: {db.query(Complaint).count()}")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
