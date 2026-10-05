import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random
import hashlib

DB_PATH = Path("database/app.db")

def get_connection():
    # Veri tabanı klasörü yoksa otomatik oluştur (Derlenmiş EXE'nin hata vermemesi için kritik)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def seed_sample_data(conn):
    cursor = conn.cursor()
    
    # Varsayılan kullanıcıları ekle (Giriş yetkilendirmesi için)
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()["count"] == 0:
        admin_hash = hash_password("admin123")
        cashier_hash = hash_password("kasiyer123")
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", ("admin", admin_hash, "admin"))
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", ("kasiyer", cashier_hash, "kasiyer"))
    
    # Veri tabanında zaten ürün olup olmadığını kontrol et
    cursor.execute("SELECT COUNT(*) as count FROM products")
    if cursor.fetchone()["count"] > 0:
        return
        
    # Örnek ürünler: (ad, kategori, stok_miktarı, alış_fiyatı, satış_fiyatı, min_stok_seviyesi)
    products = [
        ("iPhone 15 Pro", "Elektronik", 15, 45000.0, 55000.0, 3),
        ("MacBook Pro M3", "Elektronik", 8, 65000.0, 80000.0, 2),
        ("Sony WH-1000XM5", "Aksesuar", 20, 8000.0, 11000.0, 5),
        ("Logitech MX Master 3S", "Aksesuar", 25, 2500.0, 3500.0, 5),
        ("Ergonomik Ofis Koltuğu", "Ofis Mobilyası", 3, 4000.0, 6000.0, 5),  # Düşük stok
        ("Yüksekliği Ayarlanabilir Masa", "Ofis Mobilyası", 2, 8000.0, 12000.0, 3)  # Düşük stok
    ]
    
    now = datetime.now()
    product_ids = []
    
    for p in products:
        created_at = (now - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO products (name, category, stock_quantity, purchase_price, sale_price, min_stock_level, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (p[0], p[1], p[2], p[3], p[4], p[5], created_at, created_at))
        product_ids.append(cursor.lastrowid)
        
    # Grafikleri doldurmak için son 10 günlük satış geçmişi ekle
    for i in range(9, -1, -1):
        sale_date = (now - timedelta(days=i, hours=random.randint(1, 8), minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M:%S")
        
        # Her gün için rastgele 1-2 satış oluştur
        num_sales = random.randint(1, 2)
        for _ in range(num_sales):
            p_idx = random.randint(0, len(products) - 1)
            p_id = product_ids[p_idx]
            p_name, p_cat, p_stock, p_purchase, p_sale, p_min = products[p_idx]
            
            quantity = random.randint(1, 2)
            total_price = p_sale * quantity
            profit = (p_sale - p_purchase) * quantity
            
            cursor.execute("""
                INSERT INTO sales (product_id, quantity, unit_price, total_price, profit, sale_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (p_id, quantity, p_sale, total_price, profit, sale_date))

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    import sys
    import os
    schema_path = os.path.join(sys._MEIPASS, "database/schema.sql") if hasattr(sys, '_MEIPASS') else "database/schema.sql"
    
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    seed_sample_data(conn)

    conn.commit()
    conn.close()