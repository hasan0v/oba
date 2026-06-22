"""
Synthetic Data Generator for OBA Smart Assistant

This script generates realistic synthetic data for testing and development:
- Users
- Products & Categories
- Orders & Order Items
- Reviews
- Complaints
- Sales History
- User-Product Interactions (for recommendations)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid
import os

try:
    from faker import Faker
    fake = Faker(['az_AZ', 'tr_TR'])  # Azerbaijani and Turkish
except ImportError:
    fake = None
    print("Warning: Faker not installed. Using basic random data.")

# Configuration
NUM_USERS = 2000
NUM_PRODUCTS = 500
NUM_ORDERS = 10000
NUM_REVIEWS = 1000
NUM_COMPLAINTS = 500

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Categories in Azerbaijani
CATEGORIES = [
    {'name': 'Süd məhsulları', 'name_en': 'Dairy Products'},
    {'name': 'Çörək', 'name_en': 'Bread'},
    {'name': 'Meyvə', 'name_en': 'Fruits'},
    {'name': 'Tərəvəz', 'name_en': 'Vegetables'},
    {'name': 'Ət', 'name_en': 'Meat'},
    {'name': 'Balıq', 'name_en': 'Fish'},
    {'name': 'İçkilər', 'name_en': 'Beverages'},
    {'name': 'Şirniyyat', 'name_en': 'Sweets'},
    {'name': 'Qənnadi', 'name_en': 'Confectionery'},
    {'name': 'Dondurma', 'name_en': 'Ice Cream'},
    {'name': 'Konservlər', 'name_en': 'Canned Foods'},
    {'name': 'Makaron', 'name_en': 'Pasta'},
    {'name': 'Düyü və taxıl', 'name_en': 'Rice & Grains'},
    {'name': 'Yağ', 'name_en': 'Oil'},
    {'name': 'Duz və ədviyyat', 'name_en': 'Salt & Spices'}
]

# Product names by category
PRODUCT_NAMES = {
    'Süd məhsulları': [
        ('Süd 1L', 'Milk 1L', 2.5, 'OBA'),
        ('Süd 2L', 'Milk 2L', 4.5, 'OBA'),
        ('Kərə yağı 200q', 'Butter 200g', 5.5, 'Milla'),
        ('Pendir 500q', 'Cheese 500g', 8.0, 'Şəki'),
        ('Qatıq 500ml', 'Yogurt 500ml', 1.8, 'OBA'),
        ('Ayran 500ml', 'Ayran 500ml', 1.2, 'OBA'),
        ('Yoqurt 150q', 'Yogurt 150g', 1.0, 'Danone'),
        ('Süzmə qaymaq 200q', 'Sour Cream 200g', 3.0, 'OBA'),
        ('Kefir 1L', 'Kefir 1L', 2.2, 'OBA'),
    ],
    'Çörək': [
        ('Ağ çörək', 'White Bread', 0.8, 'Bakı Çörəyi'),
        ('Qara çörək', 'Black Bread', 1.0, 'Bakı Çörəyi'),
        ('Lavash', 'Lavash', 0.5, 'Local'),
        ('Bulka', 'Bun', 0.6, 'Local'),
        ('Çörək kiçik', 'Small Bread', 0.4, 'Local'),
        ('Tost çörəyi', 'Toast Bread', 2.0, 'Harry\'s'),
    ],
    'Meyvə': [
        ('Alma 1kq', 'Apple 1kg', 2.5, 'Local'),
        ('Armud 1kq', 'Pear 1kg', 3.0, 'Local'),
        ('Banan 1kq', 'Banana 1kg', 2.8, 'Import'),
        ('Portağal 1kq', 'Orange 1kg', 3.5, 'Import'),
        ('Limon 1kq', 'Lemon 1kg', 4.0, 'Import'),
        ('Üzüm 1kq', 'Grape 1kg', 5.0, 'Local'),
        ('Nar 1kq', 'Pomegranate 1kg', 4.5, 'Local'),
        ('Mandarin 1kq', 'Mandarin 1kg', 3.2, 'Import'),
    ],
    'Tərəvəz': [
        ('Pomidor 1kq', 'Tomato 1kg', 3.0, 'Local'),
        ('Xiyar 1kq', 'Cucumber 1kg', 2.5, 'Local'),
        ('Soğan 1kq', 'Onion 1kg', 1.5, 'Local'),
        ('Sarımsaq 200q', 'Garlic 200g', 2.0, 'Local'),
        ('Kartof 1kq', 'Potato 1kg', 1.2, 'Local'),
        ('Kələm 1kq', 'Cabbage 1kg', 1.0, 'Local'),
        ('Badımcan 1kq', 'Eggplant 1kg', 2.8, 'Local'),
        ('Bibər 1kq', 'Pepper 1kg', 4.0, 'Local'),
    ],
    'Ət': [
        ('Mal əti 1kq', 'Beef 1kg', 25.0, 'Local'),
        ('Quzu əti 1kq', 'Lamb 1kg', 28.0, 'Local'),
        ('Toyuq əti 1kq', 'Chicken 1kg', 8.0, 'Ata'),
        ('Toyuq qanadı 1kq', 'Chicken Wings 1kg', 6.5, 'Ata'),
        ('Qiyma 500q', 'Ground Meat 500g', 12.0, 'Local'),
    ],
    'İçkilər': [
        ('Su 1.5L', 'Water 1.5L', 1.5, 'Sirab'),
        ('Su 0.5L', 'Water 0.5L', 0.8, 'Sirab'),
        ('Kola 1L', 'Cola 1L', 2.5, 'Coca-Cola'),
        ('Çay qara 100q', 'Black Tea 100g', 4.0, 'Azerçay'),
        ('Çay yaşıl 100q', 'Green Tea 100g', 4.5, 'Azerçay'),
        ('Qəhvə 200q', 'Coffee 200g', 12.0, 'Jacobs'),
        ('Meyvə şirəsi 1L', 'Fruit Juice 1L', 3.0, 'Jaffa'),
    ],
    'Şirniyyat': [
        ('Şokolad 100q', 'Chocolate 100g', 3.5, 'Milka'),
        ('Peçenye 200q', 'Cookies 200g', 2.5, 'Siemens'),
        ('Tort 1kq', 'Cake 1kg', 15.0, 'Local'),
        ('Bal 500q', 'Honey 500g', 18.0, 'Local'),
        ('Halva 300q', 'Halva 300g', 4.0, 'Local'),
    ],
}

# Azerbaijani first names and last names
AZ_FIRST_NAMES = [
    'Aynur', 'Rəşad', 'Gülnara', 'Elvin', 'Nigar', 'Tural', 'Leyla', 'Ali',
    'Sevinc', 'Orxan', 'Aysel', 'Ruslan', 'Könül', 'Elşən', 'Günel', 'Samir',
    'Vüsalə', 'Murad', 'Ülviyyə', 'Elnur', 'Fidan', 'Kamran', 'Lamiyə', 'Vüsal',
    'Aytən', 'Rəşad', 'Nərgiz', 'İlkin', 'Aygün', 'Ceyhun', 'Lalə', 'Elçin'
]

AZ_LAST_NAMES = [
    'Məmmədov', 'Əliyev', 'Hüseynov', 'Quliyev', 'Həsənov', 'Rəhimov',
    'Əhmədov', 'Cəfərov', 'Babayev', 'İsmayılov', 'Kazımov', 'Nəsibov',
    'Mustafayev', 'Vəliyev', 'Sadıqov', 'Rzayev', 'Kərimov', 'Mirzəyev'
]

# Review templates
POSITIVE_REVIEWS = [
    "Çox yaxşı məhsuldur, tövsiyə edirəm",
    "Keyfiyyəti əla, qiyməti münasibdir",
    "Həmişə buradan alıram, çox məmnunam",
    "Məhsul təzədir, dad və ətri gözəldir",
    "Ailə üçün ideal seçimdir",
    "Super keyfiyyət, dəfələrlə aldım",
    "Çox dadlıdır, uşaqlar çox sevir",
    "Qiyməti uyğundur, tövsiyə edirəm"
]

NEUTRAL_REVIEWS = [
    "Normal məhsuldur",
    "Qiyməti bir az bahadır",
    "İdeal deyil amma pis də deyil",
    "Gözləntilərə uyğundur",
    "Orta keyfiyyət",
    "Başqa alternativ yoxdur"
]

NEGATIVE_REVIEWS = [
    "Məhsul köhnə idi, son istifadə tarixi yaxındır",
    "Dadı yaxşı deyil, bəyənmədim",
    "Qiyməti çox bahadır",
    "Keyfiyyət gözləntilərə uyğun deyil",
    "Bir daha almayacağam",
    "Qablaşdırma zədələnmişdi"
]

# Complaint templates
COMPLAINT_TEMPLATES = {
    'product': [
        "Aldığım süd xarab idi, son istifadə tarixi keçmişdi",
        "Çörək bayatdır, təzə deyil",
        "Meyvələr çürük idi, yeyilə bilməzdi",
        "Məhsulun qablaşdırması zədələnmişdi",
        "Pendir qoxusu var idi, xarab olub",
        "Yumurtalardan 3-ü sınıq idi"
    ],
    'service': [
        "Kassir çox kobud davrandı",
        "Növbə çox uzun idi, gözləmə vaxtı çoxdur",
        "İşçilər kömək etmədilər",
        "Xidmət keyfiyyəti aşağıdır",
        "Sualıma cavab verən olmadı"
    ],
    'delivery': [
        "Sifariş gecikmə ilə gəldi",
        "Kuryer məhsulu səliqəsiz çatdırdı",
        "Çatdırılma ünvanı səhv idi",
        "Bəzi məhsullar çatdırılmadı",
        "Çatdırılma vaxtı çox uzun idi"
    ],
    'pricing': [
        "Qiymət düzgün hesablanmadı",
        "Endirimdə olan məhsulun qiyməti düzgün hesablanmadı",
        "Çek ilə vitrin qiyməti fərqlidir",
        "Kampaniya qiyməti tətbiq edilmədi",
        "Artıq pul alındı, qaytarılmadı"
    ],
    'other': [
        "Mağaza çox çirklidi",
        "Soyuducu işləmirdi, məhsullar isti idi",
        "Tualet təmiz deyildi",
        "Parkinq yeri yox idi"
    ]
}


def generate_name():
    """Generate random Azerbaijani name."""
    first = random.choice(AZ_FIRST_NAMES)
    last = random.choice(AZ_LAST_NAMES)
    # Adjust last name ending based on gender (simplified)
    if first[-1] in ['a', 'ə', 'e']:  # Typically female names
        if last.endswith('ov'):
            last = last[:-2] + 'ova'
        elif last.endswith('yev'):
            last = last[:-3] + 'yeva'
    return f"{first} {last}"


def generate_email(name):
    """Generate email from name."""
    parts = name.lower().replace(' ', '.').replace('ə', 'e').replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace('ş', 's').replace('ç', 'c').replace('ğ', 'g')
    domains = ['gmail.com', 'mail.ru', 'yahoo.com', 'box.az', 'outlook.com']
    return f"{parts}{random.randint(1, 999)}@{random.choice(domains)}"


def generate_phone():
    """Generate Azerbaijani phone number."""
    prefixes = ['50', '51', '55', '70', '77', '99']
    return f"+994{random.choice(prefixes)}{random.randint(1000000, 9999999)}"


def generate_users():
    """Generate synthetic users."""
    print("Generating users...")
    users = []
    
    for i in range(NUM_USERS):
        name = generate_name()
        user = {
            'id': str(uuid.uuid4()),
            'email': generate_email(name),
            'phone': generate_phone(),
            'full_name': name,
            'points': random.randint(0, 5000),
            'is_active': random.random() > 0.05,  # 95% active
            'is_admin': i < 5,  # First 5 are admins
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 730))).isoformat()
        }
        users.append(user)
    
    df = pd.DataFrame(users)
    df.to_csv(os.path.join(OUTPUT_DIR, 'users.csv'), index=False)
    print(f"  Generated {len(users)} users")
    return df


def generate_categories():
    """Generate categories."""
    print("Generating categories...")
    categories = []
    
    for i, cat in enumerate(CATEGORIES):
        category = {
            'id': str(uuid.uuid4()),
            'name': cat['name'],
            'name_en': cat['name_en'],
            'slug': cat['name_en'].lower().replace(' ', '-').replace('&', 'and'),
            'sort_order': i,
            'is_active': True
        }
        categories.append(category)
    
    df = pd.DataFrame(categories)
    df.to_csv(os.path.join(OUTPUT_DIR, 'categories.csv'), index=False)
    print(f"  Generated {len(categories)} categories")
    return df


def generate_products(categories_df):
    """Generate synthetic products."""
    print("Generating products...")
    products = []
    
    category_map = dict(zip(categories_df['name'], categories_df['id']))
    
    for category_name, product_list in PRODUCT_NAMES.items():
        category_id = category_map.get(category_name)
        
        for name_az, name_en, base_price, brand in product_list:
            # Create 2-3 variants per product
            for variant in range(random.randint(1, 3)):
                # Add discount for some products
                has_discount = random.random() < 0.3
                discount_percent = random.choice([10, 15, 20, 25]) if has_discount else None
                discount_price = round(base_price * (1 - discount_percent/100), 2) if has_discount else None
                
                product = {
                    'id': str(uuid.uuid4()),
                    'name': name_az if variant == 0 else f"{name_az} {'Premium' if variant == 1 else 'Organic'}",
                    'name_en': name_en if variant == 0 else f"{name_en} {'Premium' if variant == 1 else 'Organic'}",
                    'slug': f"{name_en.lower().replace(' ', '-')}-{variant}",
                    'description': f"Keyfiyyətli {name_az.lower()}",
                    'category_id': category_id,
                    'brand': brand,
                    'sku': f"SKU{random.randint(10000, 99999)}",
                    'barcode': f"{random.randint(1000000000000, 9999999999999)}",
                    'price': round(base_price * (1 + variant * 0.2), 2),
                    'discount_price': discount_price,
                    'discount_percent': discount_percent,
                    'stock_quantity': random.randint(0, 200),
                    'min_stock_level': 10,
                    'unit': 'kq' if '1kq' in name_az else 'ədəd',
                    'image_urls': f'["https://example.com/products/{uuid.uuid4()}.jpg"]',
                    'is_active': True,
                    'is_featured': random.random() < 0.1,
                    'view_count': random.randint(0, 1000),
                    'sold_count': random.randint(0, 500),
                    'avg_rating': round(random.uniform(3.5, 5.0), 1),
                    'review_count': random.randint(0, 50),
                    'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
                }
                products.append(product)
    
    df = pd.DataFrame(products)
    df.to_csv(os.path.join(OUTPUT_DIR, 'products.csv'), index=False)
    print(f"  Generated {len(products)} products")
    return df


def generate_orders(users_df, products_df):
    """Generate synthetic orders."""
    print("Generating orders...")
    orders = []
    order_items = []
    
    user_ids = users_df['id'].tolist()
    product_list = products_df.to_dict('records')
    
    start_date = datetime.now() - timedelta(days=90)
    
    for i in range(NUM_ORDERS):
        user_id = random.choice(user_ids)
        order_id = str(uuid.uuid4())
        order_date = start_date + timedelta(days=random.randint(0, 90))
        
        # Weekend spike
        if order_date.weekday() >= 5:
            num_items = random.randint(3, 15)
        else:
            num_items = random.randint(1, 8)
        
        total_amount = 0
        
        # Generate order items
        selected_products = random.sample(product_list, min(num_items, len(product_list)))
        
        for product in selected_products:
            quantity = random.randint(1, 5)
            discount_price = product.get('discount_price')
            # Handle NaN and None values
            if discount_price is None or (isinstance(discount_price, float) and pd.isna(discount_price)):
                unit_price = product['price']
            else:
                unit_price = discount_price
            subtotal = unit_price * quantity
            total_amount += subtotal
            
            order_items.append({
                'id': str(uuid.uuid4()),
                'order_id': order_id,
                'product_id': product['id'],
                'product_name': product['name'],
                'quantity': quantity,
                'unit_price': product['price'],
                'discount_price': product['discount_price'],
                'subtotal': round(subtotal, 2)
            })
        
        # Calculate delivery fee
        delivery_fee = 3.0 if total_amount < 30 else 0
        
        orders.append({
            'id': order_id,
            'order_number': f"OBA{order_date.strftime('%y%m%d')}{random.randint(1000, 9999)}",
            'user_id': user_id,
            'subtotal': round(total_amount, 2),
            'discount_amount': 0,
            'delivery_fee': delivery_fee,
            'total_amount': round(total_amount + delivery_fee, 2),
            'status': random.choices(
                ['delivered', 'processing', 'shipped', 'cancelled'],
                weights=[0.7, 0.15, 0.1, 0.05]
            )[0],
            'payment_status': 'paid',
            'payment_method': random.choice(['card', 'cash', 'online']),
            'delivery_type': random.choice(['delivery', 'pickup']),
            'delivery_address': 'Bakı, Nizami rayonu, Nərimanov küçəsi 25',
            'points_earned': int(total_amount),
            'created_at': order_date.isoformat()
        })
    
    orders_df = pd.DataFrame(orders)
    items_df = pd.DataFrame(order_items)
    
    orders_df.to_csv(os.path.join(OUTPUT_DIR, 'orders.csv'), index=False)
    items_df.to_csv(os.path.join(OUTPUT_DIR, 'order_items.csv'), index=False)
    
    print(f"  Generated {len(orders)} orders with {len(order_items)} items")
    return orders_df, items_df


def generate_reviews(users_df, products_df, orders_df):
    """Generate synthetic reviews."""
    print("Generating reviews...")
    reviews = []
    
    user_ids = users_df['id'].tolist()
    product_ids = products_df['id'].tolist()
    
    for _ in range(NUM_REVIEWS):
        rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.15, 0.3, 0.4])[0]
        
        if rating >= 4:
            comment = random.choice(POSITIVE_REVIEWS)
            sentiment = 'positive'
        elif rating == 3:
            comment = random.choice(NEUTRAL_REVIEWS)
            sentiment = 'neutral'
        else:
            comment = random.choice(NEGATIVE_REVIEWS)
            sentiment = 'negative'
        
        reviews.append({
            'id': str(uuid.uuid4()),
            'user_id': random.choice(user_ids),
            'product_id': random.choice(product_ids),
            'rating': rating,
            'comment': comment,
            'sentiment': sentiment,
            'sentiment_score': rating * 20,
            'is_verified_purchase': random.random() < 0.7,
            'is_approved': True,
            'helpful_count': random.randint(0, 20),
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
        })
    
    df = pd.DataFrame(reviews)
    df.to_csv(os.path.join(OUTPUT_DIR, 'reviews.csv'), index=False)
    print(f"  Generated {len(reviews)} reviews")
    return df


def generate_complaints(users_df, orders_df):
    """Generate synthetic complaints."""
    print("Generating complaints...")
    complaints = []
    
    user_ids = users_df['id'].tolist()
    order_ids = orders_df['id'].tolist()
    
    categories = list(COMPLAINT_TEMPLATES.keys())
    
    for i in range(NUM_COMPLAINTS):
        category = random.choice(categories)
        description = random.choice(COMPLAINT_TEMPLATES[category])
        
        # Determine priority based on keywords
        if any(word in description.lower() for word in ['xarab', 'çürük', 'zədə', 'keçmiş']):
            priority = 'high'
        elif any(word in description.lower() for word in ['gecik', 'kobud', 'çirkli']):
            priority = 'medium'
        else:
            priority = 'low'
        
        complaints.append({
            'id': str(uuid.uuid4()),
            'ticket_number': f"TKT{datetime.now().strftime('%y%m%d')}{i:04d}",
            'user_id': random.choice(user_ids),
            'order_id': random.choice([random.choice(order_ids), None]),
            'category': category,
            'priority': priority,
            'subject': description[:50],
            'description': description,
            'status': random.choices(
                ['pending', 'in_progress', 'resolved', 'closed'],
                weights=[0.3, 0.3, 0.3, 0.1]
            )[0],
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        })
    
    df = pd.DataFrame(complaints)
    df.to_csv(os.path.join(OUTPUT_DIR, 'complaints.csv'), index=False)
    print(f"  Generated {len(complaints)} complaints")
    return df


def generate_sales_history(products_df):
    """Generate daily sales history for forecasting."""
    print("Generating sales history...")
    sales = []
    
    # Use first 50 products for demo
    product_ids = products_df['id'].tolist()[:50]
    start_date = datetime.now() - timedelta(days=90)
    
    for product_id in product_ids:
        base_demand = random.randint(30, 150)
        
        for day in range(90):
            date = start_date + timedelta(days=day)
            
            # Weekly pattern (weekend spike)
            day_factor = 1.3 if date.weekday() >= 5 else 1.0
            
            # Random noise
            noise = random.uniform(0.7, 1.3)
            
            quantity = int(base_demand * day_factor * noise)
            
            sales.append({
                'date': date.strftime('%Y-%m-%d'),
                'product_id': product_id,
                'quantity': max(0, quantity)
            })
    
    df = pd.DataFrame(sales)
    df.to_csv(os.path.join(OUTPUT_DIR, 'sales_history.csv'), index=False)
    print(f"  Generated {len(sales)} sales records")
    return df


def generate_interactions(users_df, products_df, orders_df, order_items_df, reviews_df):
    """Generate user-product interactions for recommendation system."""
    print("Generating interactions...")
    interactions = []
    
    user_ids = users_df['id'].tolist()
    product_ids = products_df['id'].tolist()
    
    # From orders (implicit: purchase = rating 5)
    order_user_map = dict(zip(orders_df['id'], orders_df['user_id']))
    
    for _, item in order_items_df.iterrows():
        user_id = order_user_map.get(item['order_id'])
        if user_id:
            interactions.append({
                'user_id': user_id,
                'product_id': item['product_id'],
                'rating': 5,
                'interaction_type': 'purchase',
                'timestamp': datetime.now().isoformat()
            })
    
    # From reviews (explicit ratings)
    for _, review in reviews_df.iterrows():
        interactions.append({
            'user_id': review['user_id'],
            'product_id': review['product_id'],
            'rating': review['rating'],
            'interaction_type': 'review',
            'timestamp': review['created_at']
        })
    
    # Generate views (implicit: view = rating 3)
    for _ in range(5000):
        interactions.append({
            'user_id': random.choice(user_ids),
            'product_id': random.choice(product_ids),
            'rating': 3,
            'interaction_type': 'view',
            'timestamp': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
        })
    
    df = pd.DataFrame(interactions)
    df.to_csv(os.path.join(OUTPUT_DIR, 'interactions.csv'), index=False)
    print(f"  Generated {len(interactions)} interactions")
    return df


def main():
    """Generate all synthetic data."""
    print("\n" + "="*60)
    print("OBA Smart Assistant - Synthetic Data Generator")
    print("="*60 + "\n")
    
    # Generate data
    users_df = generate_users()
    categories_df = generate_categories()
    products_df = generate_products(categories_df)
    orders_df, order_items_df = generate_orders(users_df, products_df)
    reviews_df = generate_reviews(users_df, products_df, orders_df)
    complaints_df = generate_complaints(users_df, orders_df)
    sales_df = generate_sales_history(products_df)
    interactions_df = generate_interactions(users_df, products_df, orders_df, order_items_df, reviews_df)
    
    print("\n" + "="*60)
    print("✅ All synthetic data generated successfully!")
    print(f"📁 Data saved to: {os.path.abspath(OUTPUT_DIR)}")
    print("="*60)
    
    # Print summary
    print("\nSummary:")
    print(f"  - Users: {len(users_df)}")
    print(f"  - Categories: {len(categories_df)}")
    print(f"  - Products: {len(products_df)}")
    print(f"  - Orders: {len(orders_df)}")
    print(f"  - Order Items: {len(order_items_df)}")
    print(f"  - Reviews: {len(reviews_df)}")
    print(f"  - Complaints: {len(complaints_df)}")
    print(f"  - Sales History: {len(sales_df)}")
    print(f"  - Interactions: {len(interactions_df)}")


if __name__ == "__main__":
    main()
