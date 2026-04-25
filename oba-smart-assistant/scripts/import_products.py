# -*- coding: utf-8 -*-
"""
Product Import Script for OBASA
Imports products to Supabase database with proper Azerbaijani names and image URLs
"""

import json
import requests

import os

SUPABASE_URL = "https://keleythlzrtmvoetixcl.supabase.co"
# Use service role key from environment or default to anon key
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', 
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtlbGV5dGhsenJ0bXZvZXRpeGNsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTE3OTMyMywiZXhwIjoyMDg0NzU1MzIzfQ.hF1w8xiH8LfCnmjY0KKGMAxsZOFOOQZYxfBmvPjMjGE")
STORAGE_URL = f"{SUPABASE_URL}/storage/v1/object/public/product-images"

# Categories mapping
CATEGORIES = {
    "Dairy": ["Süd", "Kərə yağı", "Pendir", "Qatıq", "Ayran", "Yoqurt", "Süzmə qaymaq", "Kefir"],
    "Bread": ["Ağ çörək", "Qara çörək", "Lavash", "Bulka", "Çörək kiçik", "Tost çörək"],
    "Fruits": ["Alma", "Armud", "Banan", "Portağal", "Limon", "Üzüm", "Nar", "Mandarin"],
    "Vegetables": ["Pomidor", "Xiyar", "Soğan", "Sarımsaq", "Kartof", "Kələm", "Badımcan", "Bibər"],
    "Meat": ["Mal əti", "Quzu əti", "Toyuq əti", "Toyuq qanadı", "Qiyma"],
    "Beverages": ["Su", "Kola", "Çay qara", "Çay yaşıl", "Qəhvə", "Meyvə şirəsi"],
    "Sweets": ["Şokolad", "Peçenye", "Tort", "Bal", "Halva"]
}

# Product definitions with proper Azerbaijani names
PRODUCTS = [
    # Dairy - Süd məhsulları
    {"name": "Süd 1L", "name_en": "Milk 1L", "price": 2.50, "category": "Dairy", "brand": "OBA", "desc": "Keyfiyyətli süd 1 litr", "stock": 150, "featured": False, "discount": 0},
    {"name": "Süd 1L Premium", "name_en": "Milk 1L Premium", "price": 3.00, "category": "Dairy", "brand": "OBA", "desc": "Premium keyfiyyətli süd 1 litr", "stock": 99, "featured": False, "discount": 0},
    {"name": "Süd 1L Organic", "name_en": "Milk 1L Organic", "price": 3.50, "category": "Dairy", "brand": "OBA", "desc": "Organik süd 1 litr", "stock": 127, "featured": False, "discount": 0},
    {"name": "Süd 2L", "name_en": "Milk 2L", "price": 4.50, "category": "Dairy", "brand": "OBA", "desc": "Keyfiyyətli süd 2 litr", "stock": 102, "featured": True, "discount": 0},
    {"name": "Süd 2L Premium", "name_en": "Milk 2L Premium", "price": 5.40, "category": "Dairy", "brand": "OBA", "desc": "Premium keyfiyyətli süd 2 litr", "stock": 151, "featured": False, "discount": 0},
    {"name": "Süd 2L Organic", "name_en": "Milk 2L Organic", "price": 6.30, "category": "Dairy", "brand": "OBA", "desc": "Organik süd 2 litr", "stock": 86, "featured": False, "discount": 20},
    
    {"name": "Kərə yağı 200q", "name_en": "Butter 200g", "price": 5.50, "category": "Dairy", "brand": "Milla", "desc": "Keyfiyyətli kərə yağı 200 qram", "stock": 157, "featured": False, "discount": 15},
    {"name": "Kərə yağı 200q Premium", "name_en": "Butter 200g Premium", "price": 6.60, "category": "Dairy", "brand": "Milla", "desc": "Premium kərə yağı 200 qram", "stock": 1, "featured": True, "discount": 10},
    {"name": "Kərə yağı 200q Organic", "name_en": "Butter 200g Organic", "price": 7.70, "category": "Dairy", "brand": "Milla", "desc": "Organik kərə yağı 200 qram", "stock": 72, "featured": False, "discount": 0},
    
    {"name": "Pendir 500q", "name_en": "Cheese 500g", "price": 8.00, "category": "Dairy", "brand": "Şəki", "desc": "Keyfiyyətli pendir 500 qram", "stock": 86, "featured": False, "discount": 0},
    {"name": "Pendir 500q Premium", "name_en": "Cheese 500g Premium", "price": 9.60, "category": "Dairy", "brand": "Şəki", "desc": "Premium pendir 500 qram", "stock": 49, "featured": False, "discount": 0},
    
    {"name": "Qatıq 500ml", "name_en": "Yogurt 500ml", "price": 1.80, "category": "Dairy", "brand": "OBA", "desc": "Keyfiyyətli qatıq 500 ml", "stock": 159, "featured": False, "discount": 0},
    {"name": "Qatıq 500ml Premium", "name_en": "Yogurt 500ml Premium", "price": 2.16, "category": "Dairy", "brand": "OBA", "desc": "Premium qatıq 500 ml", "stock": 105, "featured": False, "discount": 0},
    {"name": "Qatıq 500ml Organic", "name_en": "Yogurt 500ml Organic", "price": 2.52, "category": "Dairy", "brand": "OBA", "desc": "Organik qatıq 500 ml", "stock": 172, "featured": False, "discount": 0},
    
    {"name": "Ayran 500ml", "name_en": "Ayran 500ml", "price": 1.20, "category": "Dairy", "brand": "OBA", "desc": "Keyfiyyətli ayran 500 ml", "stock": 114, "featured": False, "discount": 0},
    {"name": "Ayran 500ml Premium", "name_en": "Ayran 500ml Premium", "price": 1.44, "category": "Dairy", "brand": "OBA", "desc": "Premium ayran 500 ml", "stock": 167, "featured": True, "discount": 0},
    
    {"name": "Yoqurt 150q", "name_en": "Yogurt 150g", "price": 1.00, "category": "Dairy", "brand": "Danone", "desc": "Keyfiyyətli yoqurt 150 qram", "stock": 126, "featured": False, "discount": 0},
    {"name": "Yoqurt 150q Premium", "name_en": "Yogurt 150g Premium", "price": 1.20, "category": "Dairy", "brand": "Danone", "desc": "Premium yoqurt 150 qram", "stock": 142, "featured": False, "discount": 0},
    
    {"name": "Süzmə qaymaq 200q", "name_en": "Sour Cream 200g", "price": 3.00, "category": "Dairy", "brand": "OBA", "desc": "Keyfiyyətli süzmə qaymaq 200 qram", "stock": 39, "featured": False, "discount": 15},
    {"name": "Süzmə qaymaq 200q Premium", "name_en": "Sour Cream 200g Premium", "price": 3.60, "category": "Dairy", "brand": "OBA", "desc": "Premium süzmə qaymaq 200 qram", "stock": 54, "featured": False, "discount": 0},
    
    {"name": "Kefir 1L", "name_en": "Kefir 1L", "price": 2.20, "category": "Dairy", "brand": "OBA", "desc": "Keyfiyyətli kefir 1 litr", "stock": 57, "featured": False, "discount": 20},
    {"name": "Kefir 1L Premium", "name_en": "Kefir 1L Premium", "price": 2.64, "category": "Dairy", "brand": "OBA", "desc": "Premium kefir 1 litr", "stock": 37, "featured": False, "discount": 0},
    {"name": "Kefir 1L Organic", "name_en": "Kefir 1L Organic", "price": 3.08, "category": "Dairy", "brand": "OBA", "desc": "Organik kefir 1 litr", "stock": 91, "featured": False, "discount": 0},
    
    # Bread - Çörək
    {"name": "Ağ çörək", "name_en": "White Bread", "price": 0.80, "category": "Bread", "brand": "Bakı çörəyi", "desc": "Keyfiyyətli ağ çörək", "stock": 196, "featured": False, "discount": 0},
    {"name": "Ağ çörək Premium", "name_en": "White Bread Premium", "price": 0.96, "category": "Bread", "brand": "Bakı çörəyi", "desc": "Premium ağ çörək", "stock": 175, "featured": False, "discount": 0},
    {"name": "Ağ çörək Organic", "name_en": "White Bread Organic", "price": 1.12, "category": "Bread", "brand": "Bakı çörəyi", "desc": "Organik ağ çörək", "stock": 3, "featured": False, "discount": 0},
    
    {"name": "Qara çörək", "name_en": "Black Bread", "price": 1.00, "category": "Bread", "brand": "Bakı çörəyi", "desc": "Keyfiyyətli qara çörək", "stock": 163, "featured": False, "discount": 15},
    {"name": "Qara çörək Premium", "name_en": "Black Bread Premium", "price": 1.20, "category": "Bread", "brand": "Bakı çörəyi", "desc": "Premium qara çörək", "stock": 58, "featured": False, "discount": 15},
    {"name": "Qara çörək Organic", "name_en": "Black Bread Organic", "price": 1.40, "category": "Bread", "brand": "Bakı çörəyi", "desc": "Organik qara çörək", "stock": 150, "featured": False, "discount": 0},
    
    {"name": "Lavaş", "name_en": "Lavash", "price": 0.50, "category": "Bread", "brand": "Local", "desc": "Keyfiyyətli lavaş", "stock": 144, "featured": False, "discount": 0},
    {"name": "Lavaş Premium", "name_en": "Lavash Premium", "price": 0.60, "category": "Bread", "brand": "Local", "desc": "Premium lavaş", "stock": 199, "featured": False, "discount": 0},
    
    {"name": "Bulka", "name_en": "Bun", "price": 0.60, "category": "Bread", "brand": "Local", "desc": "Keyfiyyətli bulka", "stock": 190, "featured": True, "discount": 0},
    
    {"name": "Çörək kiçik", "name_en": "Small Bread", "price": 0.40, "category": "Bread", "brand": "Local", "desc": "Keyfiyyətli kiçik çörək", "stock": 102, "featured": False, "discount": 0},
    {"name": "Çörək kiçik Premium", "name_en": "Small Bread Premium", "price": 0.48, "category": "Bread", "brand": "Local", "desc": "Premium kiçik çörək", "stock": 82, "featured": False, "discount": 0},
    
    {"name": "Tost çörəyi", "name_en": "Toast Bread", "price": 2.00, "category": "Bread", "brand": "Harry's", "desc": "Keyfiyyətli tost çörəyi", "stock": 40, "featured": False, "discount": 0},
    {"name": "Tost çörəyi Premium", "name_en": "Toast Bread Premium", "price": 2.40, "category": "Bread", "brand": "Harry's", "desc": "Premium tost çörəyi", "stock": 93, "featured": False, "discount": 0},
    
    # Fruits - Meyvələr
    {"name": "Alma 1kq", "name_en": "Apple 1kg", "price": 2.50, "category": "Fruits", "brand": "Local", "desc": "Keyfiyyətli alma 1 kq", "stock": 113, "featured": False, "discount": 0},
    {"name": "Alma 1kq Premium", "name_en": "Apple 1kg Premium", "price": 3.00, "category": "Fruits", "brand": "Local", "desc": "Premium alma 1 kq", "stock": 179, "featured": False, "discount": 25},
    
    {"name": "Armud 1kq", "name_en": "Pear 1kg", "price": 3.00, "category": "Fruits", "brand": "Local", "desc": "Keyfiyyətli armud 1 kq", "stock": 20, "featured": False, "discount": 20},
    
    {"name": "Banan 1kq", "name_en": "Banana 1kg", "price": 2.80, "category": "Fruits", "brand": "Import", "desc": "Keyfiyyətli banan 1 kq", "stock": 68, "featured": False, "discount": 0},
    {"name": "Banan 1kq Premium", "name_en": "Banana 1kg Premium", "price": 3.36, "category": "Fruits", "brand": "Import", "desc": "Premium banan 1 kq", "stock": 189, "featured": False, "discount": 0},
    {"name": "Banan 1kq Organic", "name_en": "Banana 1kg Organic", "price": 3.92, "category": "Fruits", "brand": "Import", "desc": "Organik banan 1 kq", "stock": 88, "featured": False, "discount": 20},
    
    {"name": "Portağal 1kq", "name_en": "Orange 1kg", "price": 3.50, "category": "Fruits", "brand": "Import", "desc": "Keyfiyyətli portağal 1 kq", "stock": 57, "featured": False, "discount": 0},
    {"name": "Portağal 1kq Premium", "name_en": "Orange 1kg Premium", "price": 4.20, "category": "Fruits", "brand": "Import", "desc": "Premium portağal 1 kq", "stock": 10, "featured": False, "discount": 0},
    {"name": "Portağal 1kq Organic", "name_en": "Orange 1kg Organic", "price": 4.90, "category": "Fruits", "brand": "Import", "desc": "Organik portağal 1 kq", "stock": 42, "featured": False, "discount": 15},
    
    {"name": "Limon 1kq", "name_en": "Lemon 1kg", "price": 4.00, "category": "Fruits", "brand": "Import", "desc": "Keyfiyyətli limon 1 kq", "stock": 117, "featured": False, "discount": 0},
    {"name": "Limon 1kq Premium", "name_en": "Lemon 1kg Premium", "price": 4.80, "category": "Fruits", "brand": "Import", "desc": "Premium limon 1 kq", "stock": 190, "featured": False, "discount": 0},
    {"name": "Limon 1kq Organic", "name_en": "Lemon 1kg Organic", "price": 5.60, "category": "Fruits", "brand": "Import", "desc": "Organik limon 1 kq", "stock": 129, "featured": False, "discount": 0},
    
    {"name": "Üzüm 1kq", "name_en": "Grape 1kg", "price": 5.00, "category": "Fruits", "brand": "Local", "desc": "Keyfiyyətli üzüm 1 kq", "stock": 111, "featured": False, "discount": 15},
    
    {"name": "Nar 1kq", "name_en": "Pomegranate 1kg", "price": 4.50, "category": "Fruits", "brand": "Local", "desc": "Keyfiyyətli nar 1 kq", "stock": 175, "featured": False, "discount": 0},
    {"name": "Nar 1kq Premium", "name_en": "Pomegranate 1kg Premium", "price": 5.40, "category": "Fruits", "brand": "Local", "desc": "Premium nar 1 kq", "stock": 22, "featured": False, "discount": 0},
    {"name": "Nar 1kq Organic", "name_en": "Pomegranate 1kg Organic", "price": 6.30, "category": "Fruits", "brand": "Local", "desc": "Organik nar 1 kq", "stock": 196, "featured": False, "discount": 25},
    
    {"name": "Mandarin 1kq", "name_en": "Mandarin 1kg", "price": 3.20, "category": "Fruits", "brand": "Import", "desc": "Keyfiyyətli mandarin 1 kq", "stock": 163, "featured": False, "discount": 0},
    
    # Vegetables - Tərəvəzlər
    {"name": "Pomidor 1kq", "name_en": "Tomato 1kg", "price": 3.00, "category": "Vegetables", "brand": "Local", "desc": "Keyfiyyətli pomidor 1 kq", "stock": 98, "featured": False, "discount": 0},
    
    {"name": "Xiyar 1kq", "name_en": "Cucumber 1kg", "price": 2.50, "category": "Vegetables", "brand": "Local", "desc": "Keyfiyyətli xiyar 1 kq", "stock": 15, "featured": False, "discount": 0},
    {"name": "Xiyar 1kq Premium", "name_en": "Cucumber 1kg Premium", "price": 3.00, "category": "Vegetables", "brand": "Local", "desc": "Premium xiyar 1 kq", "stock": 60, "featured": False, "discount": 0},
    {"name": "Xiyar 1kq Organic", "name_en": "Cucumber 1kg Organic", "price": 3.50, "category": "Vegetables", "brand": "Local", "desc": "Organik xiyar 1 kq", "stock": 142, "featured": True, "discount": 0},
    
    {"name": "Soğan 1kq", "name_en": "Onion 1kg", "price": 1.50, "category": "Vegetables", "brand": "Local", "desc": "Keyfiyyətli soğan 1 kq", "stock": 109, "featured": True, "discount": 25},
    {"name": "Soğan 1kq Premium", "name_en": "Onion 1kg Premium", "price": 1.80, "category": "Vegetables", "brand": "Local", "desc": "Premium soğan 1 kq", "stock": 154, "featured": False, "discount": 0},
    {"name": "Soğan 1kq Organic", "name_en": "Onion 1kg Organic", "price": 2.10, "category": "Vegetables", "brand": "Local", "desc": "Organik soğan 1 kq", "stock": 32, "featured": False, "discount": 10},
    
    {"name": "Sarımsaq 200q", "name_en": "Garlic 200g", "price": 2.00, "category": "Vegetables", "brand": "Local", "desc": "Keyfiyyətli sarımsaq 200 qram", "stock": 23, "featured": False, "discount": 25},
    {"name": "Sarımsaq 200q Premium", "name_en": "Garlic 200g Premium", "price": 2.40, "category": "Vegetables", "brand": "Local", "desc": "Premium sarımsaq 200 qram", "stock": 146, "featured": False, "discount": 10},
    {"name": "Sarımsaq 200q Organic", "name_en": "Garlic 200g Organic", "price": 2.80, "category": "Vegetables", "brand": "Local", "desc": "Organik sarımsaq 200 qram", "stock": 30, "featured": False, "discount": 20},
    
    {"name": "Kartof 1kq", "name_en": "Potato 1kg", "price": 1.20, "category": "Vegetables", "brand": "Local", "desc": "Keyfiyyətli kartof 1 kq", "stock": 49, "featured": False, "discount": 0},
    {"name": "Kartof 1kq Premium", "name_en": "Potato 1kg Premium", "price": 1.44, "category": "Vegetables", "brand": "Local", "desc": "Premium kartof 1 kq", "stock": 74, "featured": False, "discount": 0},
    
    {"name": "Kələm 1kq", "name_en": "Cabbage 1kg", "price": 1.00, "category": "Vegetables", "brand": "Local", "desc": "Keyfiyyətli kələm 1 kq", "stock": 31, "featured": False, "discount": 25},
    {"name": "Kələm 1kq Premium", "name_en": "Cabbage 1kg Premium", "price": 1.20, "category": "Vegetables", "brand": "Local", "desc": "Premium kələm 1 kq", "stock": 107, "featured": False, "discount": 0},
    {"name": "Kələm 1kq Organic", "name_en": "Cabbage 1kg Organic", "price": 1.40, "category": "Vegetables", "brand": "Local", "desc": "Organik kələm 1 kq", "stock": 116, "featured": False, "discount": 0},
    
    {"name": "Badımcan 1kq", "name_en": "Eggplant 1kg", "price": 2.80, "category": "Vegetables", "brand": "Local", "desc": "Keyfiyyətli badımcan 1 kq", "stock": 89, "featured": False, "discount": 0},
    {"name": "Badımcan 1kq Premium", "name_en": "Eggplant 1kg Premium", "price": 3.36, "category": "Vegetables", "brand": "Local", "desc": "Premium badımcan 1 kq", "stock": 28, "featured": False, "discount": 25},
    
    {"name": "Bibər 1kq", "name_en": "Pepper 1kg", "price": 4.00, "category": "Vegetables", "brand": "Local", "desc": "Keyfiyyətli bibər 1 kq", "stock": 154, "featured": False, "discount": 0},
    
    # Meat - Ət məhsulları
    {"name": "Mal əti 1kq", "name_en": "Beef 1kg", "price": 25.00, "category": "Meat", "brand": "Local", "desc": "Keyfiyyətli mal əti 1 kq", "stock": 195, "featured": False, "discount": 25},
    {"name": "Mal əti 1kq Premium", "name_en": "Beef 1kg Premium", "price": 30.00, "category": "Meat", "brand": "Local", "desc": "Premium mal əti 1 kq", "stock": 126, "featured": False, "discount": 20},
    
    {"name": "Quzu əti 1kq", "name_en": "Lamb 1kg", "price": 28.00, "category": "Meat", "brand": "Local", "desc": "Keyfiyyətli quzu əti 1 kq", "stock": 144, "featured": False, "discount": 20},
    {"name": "Quzu əti 1kq Premium", "name_en": "Lamb 1kg Premium", "price": 33.60, "category": "Meat", "brand": "Local", "desc": "Premium quzu əti 1 kq", "stock": 177, "featured": False, "discount": 0},
    
    {"name": "Toyuq əti 1kq", "name_en": "Chicken 1kg", "price": 8.00, "category": "Meat", "brand": "Ata", "desc": "Keyfiyyətli toyuq əti 1 kq", "stock": 10, "featured": False, "discount": 0},
    
    {"name": "Toyuq qanadı 1kq", "name_en": "Chicken Wings 1kg", "price": 6.50, "category": "Meat", "brand": "Ata", "desc": "Keyfiyyətli toyuq qanadı 1 kq", "stock": 165, "featured": False, "discount": 0},
    
    {"name": "Qiyma 500q", "name_en": "Ground Meat 500g", "price": 12.00, "category": "Meat", "brand": "Local", "desc": "Keyfiyyətli qiyma 500 qram", "stock": 65, "featured": False, "discount": 0},
    
    # Beverages - İçkilər
    {"name": "Su 1.5L", "name_en": "Water 1.5L", "price": 1.50, "category": "Beverages", "brand": "Sirab", "desc": "Keyfiyyətli su 1.5 litr", "stock": 3, "featured": False, "discount": 0},
    
    {"name": "Su 0.5L", "name_en": "Water 0.5L", "price": 0.80, "category": "Beverages", "brand": "Sirab", "desc": "Keyfiyyətli su 0.5 litr", "stock": 56, "featured": False, "discount": 0},
    {"name": "Su 0.5L Premium", "name_en": "Water 0.5L Premium", "price": 0.96, "category": "Beverages", "brand": "Sirab", "desc": "Premium su 0.5 litr", "stock": 191, "featured": False, "discount": 0},
    
    {"name": "Kola 1L", "name_en": "Cola 1L", "price": 2.50, "category": "Beverages", "brand": "Coca-Cola", "desc": "Keyfiyyətli kola 1 litr", "stock": 104, "featured": False, "discount": 0},
    {"name": "Kola 1L Premium", "name_en": "Cola 1L Premium", "price": 3.00, "category": "Beverages", "brand": "Coca-Cola", "desc": "Premium kola 1 litr", "stock": 195, "featured": False, "discount": 0},
    
    {"name": "Çay qara 100q", "name_en": "Black Tea 100g", "price": 4.00, "category": "Beverages", "brand": "Azərçay", "desc": "Keyfiyyətli qara çay 100 qram", "stock": 159, "featured": False, "discount": 0},
    
    {"name": "Çay yaşıl 100q", "name_en": "Green Tea 100g", "price": 4.50, "category": "Beverages", "brand": "Azərçay", "desc": "Keyfiyyətli yaşıl çay 100 qram", "stock": 4, "featured": False, "discount": 0},
    {"name": "Çay yaşıl 100q Premium", "name_en": "Green Tea 100g Premium", "price": 5.40, "category": "Beverages", "brand": "Azərçay", "desc": "Premium yaşıl çay 100 qram", "stock": 129, "featured": True, "discount": 0},
    {"name": "Çay yaşıl 100q Organic", "name_en": "Green Tea 100g Organic", "price": 6.30, "category": "Beverages", "brand": "Azərçay", "desc": "Organik yaşıl çay 100 qram", "stock": 49, "featured": False, "discount": 15},
    
    {"name": "Qəhvə 200q", "name_en": "Coffee 200g", "price": 12.00, "category": "Beverages", "brand": "Jacobs", "desc": "Keyfiyyətli qəhvə 200 qram", "stock": 42, "featured": False, "discount": 0},
    {"name": "Qəhvə 200q Premium", "name_en": "Coffee 200g Premium", "price": 14.40, "category": "Beverages", "brand": "Jacobs", "desc": "Premium qəhvə 200 qram", "stock": 64, "featured": False, "discount": 0},
    {"name": "Qəhvə 200q Organic", "name_en": "Coffee 200g Organic", "price": 16.80, "category": "Beverages", "brand": "Jacobs", "desc": "Organik qəhvə 200 qram", "stock": 72, "featured": False, "discount": 25},
    
    {"name": "Meyvə şirəsi 1L", "name_en": "Fruit Juice 1L", "price": 3.00, "category": "Beverages", "brand": "Jaffa", "desc": "Keyfiyyətli meyvə şirəsi 1 litr", "stock": 166, "featured": False, "discount": 0},
    
    # Sweets - Şirniyyatlar
    {"name": "Şokolad 100q", "name_en": "Chocolate 100g", "price": 3.50, "category": "Sweets", "brand": "Milka", "desc": "Keyfiyyətli şokolad 100 qram", "stock": 171, "featured": False, "discount": 0},
    {"name": "Şokolad 100q Premium", "name_en": "Chocolate 100g Premium", "price": 4.20, "category": "Sweets", "brand": "Milka", "desc": "Premium şokolad 100 qram", "stock": 97, "featured": False, "discount": 0},
    
    {"name": "Peçenye 200q", "name_en": "Cookies 200g", "price": 2.50, "category": "Sweets", "brand": "Siemens", "desc": "Keyfiyyətli peçenye 200 qram", "stock": 111, "featured": False, "discount": 10},
    
    {"name": "Tort 1kq", "name_en": "Cake 1kg", "price": 15.00, "category": "Sweets", "brand": "Local", "desc": "Keyfiyyətli tort 1 kq", "stock": 26, "featured": True, "discount": 0},
    
    {"name": "Bal 500q", "name_en": "Honey 500g", "price": 18.00, "category": "Sweets", "brand": "Local", "desc": "Keyfiyyətli bal 500 qram", "stock": 7, "featured": False, "discount": 0},
    
    {"name": "Halva 300q", "name_en": "Halva 300g", "price": 4.00, "category": "Sweets", "brand": "Local", "desc": "Keyfiyyətli halva 300 qram", "stock": 93, "featured": False, "discount": 15},
]

def get_image_url(name_en):
    """Generate Supabase Storage URL from English product name"""
    # Convert name to image filename format
    filename = name_en.replace(" ", "%20") + ".webp"
    return f"{STORAGE_URL}/{filename}"

def delete_existing_products():
    """Delete all existing products"""
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Delete all products
    response = requests.delete(
        f"{SUPABASE_URL}/rest/v1/products?id=gte.0",
        headers=headers
    )
    
    if response.status_code in [200, 204]:
        print("✓ Deleted existing products")
        return True
    else:
        print(f"Warning: Could not delete products: {response.status_code} - {response.text}")
        return False

def insert_products():
    """Insert all products to Supabase"""
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    products_to_insert = []
    
    for p in PRODUCTS:
        image_url = get_image_url(p["name_en"])
        
        product = {
            "name": p["name"],
            "description": p["desc"],
            "price": p["price"],
            "category": p["category"],
            "brand": p["brand"],
            "image_url": image_url,
            "stock_quantity": p["stock"],
            "is_featured": p["featured"],
            "is_deal": p["discount"] > 0,
            "discount_percentage": p["discount"],
            "is_active": True
        }
        products_to_insert.append(product)
    
    # Insert in batches
    batch_size = 50
    for i in range(0, len(products_to_insert), batch_size):
        batch = products_to_insert[i:i+batch_size]
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/products",
            headers=headers,
            json=batch
        )
        
        if response.status_code in [200, 201]:
            print(f"✓ Inserted batch {i//batch_size + 1}: {len(batch)} products")
        else:
            print(f"✗ Error inserting batch: {response.status_code} - {response.text}")
            return False
    
    return True

def main():
    print("=== OBASA Product Import ===")
    print(f"Total products to import: {len(PRODUCTS)}")
    print()
    
    # Delete existing products
    print("1. Deleting existing products...")
    delete_existing_products()
    
    # Insert new products
    print("2. Inserting new products...")
    if insert_products():
        print()
        print(f"✓ Successfully imported {len(PRODUCTS)} products!")
    else:
        print("✗ Failed to import products")

if __name__ == "__main__":
    main()
