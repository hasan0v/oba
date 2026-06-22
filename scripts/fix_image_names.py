# -*- coding: utf-8 -*-
"""
Fix Image Names Script for OBASA
Updates product image_url in Supabase to match actual storage file names
Storage format: lowercase_with_underscores.webp (e.g., apple_1kg_premium.webp)
"""

import requests
from urllib.parse import unquote

# Supabase Configuration
SUPABASE_URL = "https://keleythlzrtmvoetixcl.supabase.co"
# Service role key (has full access to bypass RLS)
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtlbGV5dGhsenJ0bXZvZXRpeGNsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTE3OTMyMywiZXhwIjoyMDg0NzU1MzIzfQ.AtEPGg_hVYzJOjwPLaOdRkozemgiLL8ILCp9v2OOxV4"
STORAGE_URL = f"{SUPABASE_URL}/storage/v1/object/public/product-images"

def convert_to_storage_format(old_url):
    """
    Convert old image URL format to new storage format
    Old: https://.../Milk%201L%20Premium.webp
    New: https://.../milk_1l_premium.webp
    """
    if not old_url:
        return None
    
    # Extract filename from URL
    filename = old_url.split('/')[-1]
    # Decode URL encoding
    filename = unquote(filename)
    # Convert: lowercase, replace spaces with underscores
    new_filename = filename.lower().replace(" ", "_")
    
    return f"{STORAGE_URL}/{new_filename}"

def get_all_products():
    """Fetch all products from database"""
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/products?select=id,name,image_url",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching products: {response.status_code} - {response.text}")
        return []

def update_product_image(product_id, new_image_url):
    """Update a product's image_url"""
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/products?id=eq.{product_id}",
        headers=headers,
        json={"image_url": new_image_url}
    )
    
    if response.status_code in [200, 204]:
        return True
    else:
        print(f"  Error updating: {response.status_code} - {response.text}")
        return False

def main():
    print("=== OBASA Image Name Fixer ===")
    print()
    
    # Fetch all products
    print("1. Fetching products from database...")
    products = get_all_products()
    print(f"   Found {len(products)} products")
    print()
    
    if not products:
        return
    
    # Update each product
    print("2. Updating image URLs...")
    print("   Converting format: 'Milk 1L.webp' -> 'milk_1l.webp'")
    print()
    
    updated = 0
    failed = 0
    skipped = 0
    
    for product in products:
        product_id = product.get('id')
        name = product.get('name', '')
        old_url = product.get('image_url', '')
        
        if not old_url:
            print(f"   ? Skipped: {name} (no image URL)")
            skipped += 1
            continue
        
        # Convert to new format
        new_url = convert_to_storage_format(old_url)
        
        if old_url == new_url:
            print(f"   = No change: {name}")
            skipped += 1
            continue
        
        if update_product_image(product_id, new_url):
            old_filename = unquote(old_url.split('/')[-1])
            new_filename = new_url.split('/')[-1]
            print(f"   ✓ Updated: {name}")
            print(f"      {old_filename} -> {new_filename}")
            updated += 1
        else:
            print(f"   ✗ Failed: {name}")
            failed += 1
    
    print()
    print("=== Summary ===")
    print(f"✓ Updated: {updated}")
    print(f"✗ Failed: {failed}")
    print(f"= Skipped: {skipped}")

if __name__ == "__main__":
    main()
