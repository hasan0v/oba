import psycopg2

# Supabase database connection details
# Format: postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
DATABASE_URL = "postgresql://postgres.keleythlzrtmvoetixcl:OBASmartAssistant2024!@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

products = [
    # Dairy - Süd məhsulları
    ('Süd 1L', 'Keyfiyyətli süd 1 litr', 2.50, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Milk%201L.webp', 150, False, False, 0),
    ('Süd 1L Premium', 'Premium keyfiyyətli süd 1 litr', 3.00, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Milk%201L%20Premium.webp', 99, False, False, 0),
    ('Süd 1L Organic', 'Organik süd 1 litr', 3.50, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Milk%201L%20Organic.webp', 127, False, False, 0),
    ('Süd 2L', 'Keyfiyyətli süd 2 litr', 4.50, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Milk%202L.webp', 102, True, False, 0),
    ('Süd 2L Premium', 'Premium keyfiyyətli süd 2 litr', 5.40, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Milk%202L%20Premium.webp', 151, False, False, 0),
    ('Süd 2L Organic', 'Organik süd 2 litr', 6.30, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Milk%202L%20Organic.webp', 86, False, True, 20),
    ('Kərə yağı 200q', 'Keyfiyyətli kərə yağı 200 qram', 5.50, 'Dairy', 'Milla', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Butter%20200g.webp', 157, False, True, 15),
    ('Kərə yağı 200q Premium', 'Premium kərə yağı 200 qram', 6.60, 'Dairy', 'Milla', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Butter%20200g%20Premium.webp', 1, True, True, 10),
    ('Kərə yağı 200q Organic', 'Organik kərə yağı 200 qram', 7.70, 'Dairy', 'Milla', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Butter%20200g%20Organic.webp', 72, False, False, 0),
    ('Pendir 500q', 'Keyfiyyətli pendir 500 qram', 8.00, 'Dairy', 'Şəki', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cheese%20500g.webp', 86, False, False, 0),
    ('Pendir 500q Premium', 'Premium pendir 500 qram', 9.60, 'Dairy', 'Şəki', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cheese%20500g%20Premium.webp', 49, False, False, 0),
    ('Qatıq 500ml', 'Keyfiyyətli qatıq 500 ml', 1.80, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Yogurt%20500ml.webp', 159, False, False, 0),
    ('Qatıq 500ml Premium', 'Premium qatıq 500 ml', 2.16, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Yogurt%20500ml%20Premium.webp', 105, False, False, 0),
    ('Qatıq 500ml Organic', 'Organik qatıq 500 ml', 2.52, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Yogurt%20500ml%20Organic.webp', 172, False, False, 0),
    ('Ayran 500ml', 'Keyfiyyətli ayran 500 ml', 1.20, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Ayran%20500ml.webp', 114, False, False, 0),
    ('Ayran 500ml Premium', 'Premium ayran 500 ml', 1.44, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Ayran%20500ml%20Premium.webp', 167, True, False, 0),
    ('Yoqurt 150q', 'Keyfiyyətli yoqurt 150 qram', 1.00, 'Dairy', 'Danone', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Yogurt%20150g.webp', 126, False, False, 0),
    ('Yoqurt 150q Premium', 'Premium yoqurt 150 qram', 1.20, 'Dairy', 'Danone', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Yogurt%20150g%20Premium.webp', 142, False, False, 0),
    ('Süzmə qaymaq 200q', 'Keyfiyyətli süzmə qaymaq 200 qram', 3.00, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Sour%20Cream%20200g.webp', 39, False, True, 15),
    ('Süzmə qaymaq 200q Premium', 'Premium süzmə qaymaq 200 qram', 3.60, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Sour%20Cream%20200g%20Premium.webp', 54, False, False, 0),
    ('Kefir 1L', 'Keyfiyyətli kefir 1 litr', 2.20, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Kefir%201L.webp', 57, False, True, 20),
    ('Kefir 1L Premium', 'Premium kefir 1 litr', 2.64, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Kefir%201L%20Premium.webp', 37, False, False, 0),
    ('Kefir 1L Organic', 'Organik kefir 1 litr', 3.08, 'Dairy', 'OBA', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Kefir%201L%20Organic.webp', 91, False, False, 0),
    # Bread - Çörək
    ('Ağ çörək', 'Keyfiyyətli ağ çörək', 0.80, 'Bread', 'Bakı çörəyi', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/White%20Bread.webp', 196, False, False, 0),
    ('Ağ çörək Premium', 'Premium ağ çörək', 0.96, 'Bread', 'Bakı çörəyi', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/White%20Bread%20Premium.webp', 175, False, False, 0),
    ('Ağ çörək Organic', 'Organik ağ çörək', 1.12, 'Bread', 'Bakı çörəyi', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/White%20Bread%20Organic.webp', 3, False, False, 0),
    ('Qara çörək', 'Keyfiyyətli qara çörək', 1.00, 'Bread', 'Bakı çörəyi', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Black%20Bread.webp', 163, False, True, 15),
    ('Qara çörək Premium', 'Premium qara çörək', 1.20, 'Bread', 'Bakı çörəyi', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Black%20Bread%20Premium.webp', 58, False, True, 15),
    ('Qara çörək Organic', 'Organik qara çörək', 1.40, 'Bread', 'Bakı çörəyi', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Black%20Bread%20Organic.webp', 150, False, False, 0),
    ('Lavaş', 'Keyfiyyətli lavaş', 0.50, 'Bread', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Lavash.webp', 144, False, False, 0),
    ('Lavaş Premium', 'Premium lavaş', 0.60, 'Bread', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Lavash%20Premium.webp', 199, False, False, 0),
    ('Bulka', 'Keyfiyyətli bulka', 0.60, 'Bread', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Bun.webp', 190, True, False, 0),
    ('Çörək kiçik', 'Keyfiyyətli kiçik çörək', 0.40, 'Bread', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Small%20Bread.webp', 102, False, False, 0),
    ('Çörək kiçik Premium', 'Premium kiçik çörək', 0.48, 'Bread', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Small%20Bread%20Premium.webp', 82, False, False, 0),
    ('Tost çörəyi', 'Keyfiyyətli tost çörəyi', 2.00, 'Bread', "Harry's", 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Toast%20Bread.webp', 40, False, False, 0),
    ('Tost çörəyi Premium', 'Premium tost çörəyi', 2.40, 'Bread', "Harry's", 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Toast%20Bread%20Premium.webp', 93, False, False, 0),
    # Fruits - Meyvələr
    ('Alma 1kq', 'Keyfiyyətli alma 1 kq', 2.50, 'Fruits', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Apple%201kg.webp', 113, False, False, 0),
    ('Alma 1kq Premium', 'Premium alma 1 kq', 3.00, 'Fruits', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Apple%201kg%20Premium.webp', 179, False, True, 25),
    ('Armud 1kq', 'Keyfiyyətli armud 1 kq', 3.00, 'Fruits', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Pear%201kg.webp', 20, False, True, 20),
    ('Banan 1kq', 'Keyfiyyətli banan 1 kq', 2.80, 'Fruits', 'Import', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Banana%201kg.webp', 68, False, False, 0),
    ('Banan 1kq Premium', 'Premium banan 1 kq', 3.36, 'Fruits', 'Import', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Banana%201kg%20Premium.webp', 189, False, False, 0),
    ('Banan 1kq Organic', 'Organik banan 1 kq', 3.92, 'Fruits', 'Import', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Banana%201kg%20Organic.webp', 88, False, True, 20),
    ('Portağal 1kq', 'Keyfiyyətli portağal 1 kq', 3.50, 'Fruits', 'Import', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Orange%201kg.webp', 57, False, False, 0),
    ('Portağal 1kq Premium', 'Premium portağal 1 kq', 4.20, 'Fruits', 'Import', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Orange%201kg%20Premium.webp', 10, False, False, 0),
    ('Portağal 1kq Organic', 'Organik portağal 1 kq', 4.90, 'Fruits', 'Import', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Orange%201kg%20Organic.webp', 42, False, True, 15),
    ('Limon 1kq', 'Keyfiyyətli limon 1 kq', 4.00, 'Fruits', 'Import', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Lemon%201kg.webp', 117, False, False, 0),
    ('Limon 1kq Premium', 'Premium limon 1 kq', 4.80, 'Fruits', 'Import', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Lemon%201kg%20Premium.webp', 190, False, False, 0),
    ('Limon 1kq Organic', 'Organik limon 1 kq', 5.60, 'Fruits', 'Import', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Lemon%201kg%20Organic.webp', 129, False, False, 0),
    ('Üzüm 1kq', 'Keyfiyyətli üzüm 1 kq', 5.00, 'Fruits', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Grape%201kg.webp', 111, False, True, 15),
    ('Nar 1kq', 'Keyfiyyətli nar 1 kq', 4.50, 'Fruits', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Pomegranate%201kg.webp', 175, False, False, 0),
    ('Nar 1kq Premium', 'Premium nar 1 kq', 5.40, 'Fruits', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Pomegranate%201kg%20Premium.webp', 22, False, False, 0),
    ('Nar 1kq Organic', 'Organik nar 1 kq', 6.30, 'Fruits', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Pomegranate%201kg%20Organic.webp', 196, False, True, 25),
    ('Mandarin 1kq', 'Keyfiyyətli mandarin 1 kq', 3.20, 'Fruits', 'Import', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Mandarin%201kg.webp', 163, False, False, 0),
    # Vegetables - Tərəvəzlər
    ('Pomidor 1kq', 'Keyfiyyətli pomidor 1 kq', 3.00, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Tomato%201kg.webp', 98, False, False, 0),
    ('Xiyar 1kq', 'Keyfiyyətli xiyar 1 kq', 2.50, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cucumber%201kg.webp', 15, False, False, 0),
    ('Xiyar 1kq Premium', 'Premium xiyar 1 kq', 3.00, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cucumber%201kg%20Premium.webp', 60, False, False, 0),
    ('Xiyar 1kq Organic', 'Organik xiyar 1 kq', 3.50, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cucumber%201kg%20Organic.webp', 142, True, False, 0),
    ('Soğan 1kq', 'Keyfiyyətli soğan 1 kq', 1.50, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Onion%201kg.webp', 109, True, True, 25),
    ('Soğan 1kq Premium', 'Premium soğan 1 kq', 1.80, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Onion%201kg%20Premium.webp', 154, False, False, 0),
    ('Soğan 1kq Organic', 'Organik soğan 1 kq', 2.10, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Onion%201kg%20Organic.webp', 32, False, True, 10),
    ('Sarımsaq 200q', 'Keyfiyyətli sarımsaq 200 qram', 2.00, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Garlic%20200g.webp', 23, False, True, 25),
    ('Sarımsaq 200q Premium', 'Premium sarımsaq 200 qram', 2.40, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Garlic%20200g%20Premium.webp', 146, False, True, 10),
    ('Sarımsaq 200q Organic', 'Organik sarımsaq 200 qram', 2.80, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Garlic%20200g%20Organic.webp', 30, False, True, 20),
    ('Kartof 1kq', 'Keyfiyyətli kartof 1 kq', 1.20, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Potato%201kg.webp', 49, False, False, 0),
    ('Kartof 1kq Premium', 'Premium kartof 1 kq', 1.44, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Potato%201kg%20Premium.webp', 74, False, False, 0),
    ('Kələm 1kq', 'Keyfiyyətli kələm 1 kq', 1.00, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cabbage%201kg.webp', 31, False, True, 25),
    ('Kələm 1kq Premium', 'Premium kələm 1 kq', 1.20, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cabbage%201kg%20Premium.webp', 107, False, False, 0),
    ('Kələm 1kq Organic', 'Organik kələm 1 kq', 1.40, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cabbage%201kg%20Organic.webp', 116, False, False, 0),
    ('Badımcan 1kq', 'Keyfiyyətli badımcan 1 kq', 2.80, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Eggplant%201kg.webp', 89, False, False, 0),
    ('Badımcan 1kq Premium', 'Premium badımcan 1 kq', 3.36, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Eggplant%201kg%20Premium.webp', 28, False, True, 25),
    ('Bibər 1kq', 'Keyfiyyətli bibər 1 kq', 4.00, 'Vegetables', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Pepper%201kg.webp', 154, False, False, 0),
    # Meat - Ət məhsulları
    ('Mal əti 1kq', 'Keyfiyyətli mal əti 1 kq', 25.00, 'Meat', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Beef%201kg.webp', 195, False, True, 25),
    ('Mal əti 1kq Premium', 'Premium mal əti 1 kq', 30.00, 'Meat', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Beef%201kg%20Premium.webp', 126, False, True, 20),
    ('Quzu əti 1kq', 'Keyfiyyətli quzu əti 1 kq', 28.00, 'Meat', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Lamb%201kg.webp', 144, False, True, 20),
    ('Quzu əti 1kq Premium', 'Premium quzu əti 1 kq', 33.60, 'Meat', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Lamb%201kg%20Premium.webp', 177, False, False, 0),
    ('Toyuq əti 1kq', 'Keyfiyyətli toyuq əti 1 kq', 8.00, 'Meat', 'Ata', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Chicken%201kg.webp', 10, False, False, 0),
    ('Toyuq qanadı 1kq', 'Keyfiyyətli toyuq qanadı 1 kq', 6.50, 'Meat', 'Ata', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Chicken%20Wings%201kg.webp', 165, False, False, 0),
    ('Qiyma 500q', 'Keyfiyyətli qiyma 500 qram', 12.00, 'Meat', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Ground%20Meat%20500g.webp', 65, False, False, 0),
    # Beverages - İçkilər
    ('Su 1.5L', 'Keyfiyyətli su 1.5 litr', 1.50, 'Beverages', 'Sirab', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Water%201.5L.webp', 3, False, False, 0),
    ('Su 0.5L', 'Keyfiyyətli su 0.5 litr', 0.80, 'Beverages', 'Sirab', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Water%200.5L.webp', 56, False, False, 0),
    ('Su 0.5L Premium', 'Premium su 0.5 litr', 0.96, 'Beverages', 'Sirab', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Water%200.5L%20Premium.webp', 191, False, False, 0),
    ('Kola 1L', 'Keyfiyyətli kola 1 litr', 2.50, 'Beverages', 'Coca-Cola', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cola%201L.webp', 104, False, False, 0),
    ('Kola 1L Premium', 'Premium kola 1 litr', 3.00, 'Beverages', 'Coca-Cola', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cola%201L%20Premium.webp', 195, False, False, 0),
    ('Çay qara 100q', 'Keyfiyyətli qara çay 100 qram', 4.00, 'Beverages', 'Azərçay', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Black%20Tea%20100g.webp', 159, False, False, 0),
    ('Çay yaşıl 100q', 'Keyfiyyətli yaşıl çay 100 qram', 4.50, 'Beverages', 'Azərçay', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Green%20Tea%20100g.webp', 4, False, False, 0),
    ('Çay yaşıl 100q Premium', 'Premium yaşıl çay 100 qram', 5.40, 'Beverages', 'Azərçay', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Green%20Tea%20100g%20Premium.webp', 129, True, False, 0),
    ('Çay yaşıl 100q Organic', 'Organik yaşıl çay 100 qram', 6.30, 'Beverages', 'Azərçay', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Green%20Tea%20100g%20Organic.webp', 49, False, True, 15),
    ('Qəhvə 200q', 'Keyfiyyətli qəhvə 200 qram', 12.00, 'Beverages', 'Jacobs', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Coffee%20200g.webp', 42, False, False, 0),
    ('Qəhvə 200q Premium', 'Premium qəhvə 200 qram', 14.40, 'Beverages', 'Jacobs', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Coffee%20200g%20Premium.webp', 64, False, False, 0),
    ('Qəhvə 200q Organic', 'Organik qəhvə 200 qram', 16.80, 'Beverages', 'Jacobs', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Coffee%20200g%20Organic.webp', 72, False, True, 25),
    ('Meyvə şirəsi 1L', 'Keyfiyyətli meyvə şirəsi 1 litr', 3.00, 'Beverages', 'Jaffa', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Fruit%20Juice%201L.webp', 166, False, False, 0),
    # Sweets - Şirniyyatlar
    ('Şokolad 100q', 'Keyfiyyətli şokolad 100 qram', 3.50, 'Sweets', 'Milka', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Chocolate%20100g.webp', 171, False, False, 0),
    ('Şokolad 100q Premium', 'Premium şokolad 100 qram', 4.20, 'Sweets', 'Milka', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Chocolate%20100g%20Premium.webp', 97, False, False, 0),
    ('Peçenye 200q', 'Keyfiyyətli peçenye 200 qram', 2.50, 'Sweets', 'Siemens', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cookies%20200g.webp', 111, False, True, 10),
    ('Tort 1kq', 'Keyfiyyətli tort 1 kq', 15.00, 'Sweets', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Cake%201kg.webp', 26, True, False, 0),
    ('Bal 500q', 'Keyfiyyətli bal 500 qram', 18.00, 'Sweets', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Honey%20500g.webp', 7, False, False, 0),
    ('Halva 300q', 'Keyfiyyətli halva 300 qram', 4.00, 'Sweets', 'Local', 'https://keleythlzrtmvoetixcl.supabase.co/storage/v1/object/public/product-images/Halva%20300g.webp', 93, False, True, 15),
]

def main():
    try:
        print("Connecting to Supabase database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Delete existing products
        print("Deleting existing products...")
        cursor.execute("DELETE FROM products")
        
        # Reset sequence
        print("Resetting sequence...")
        cursor.execute("ALTER SEQUENCE products_id_seq RESTART WITH 1")
        
        # Insert products
        print(f"Inserting {len(products)} products...")
        insert_query = """
            INSERT INTO products (name, description, price, category, brand, image_url, stock_quantity, is_featured, is_deal, discount_percentage, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true)
        """
        
        for i, product in enumerate(products):
            cursor.execute(insert_query, product)
            if (i + 1) % 10 == 0:
                print(f"  Inserted {i + 1}/{len(products)} products...")
        
        # Commit changes
        conn.commit()
        
        # Verify count
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        print(f"\nSuccess! Total products in database: {count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
