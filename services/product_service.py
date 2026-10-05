from database.db import get_connection
from datetime import datetime

def add_product(name, category, stock_quantity, purchase_price, sale_price, min_stock_level):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO products (
            name, category, stock_quantity, purchase_price, sale_price, min_stock_level, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        category,
        stock_quantity,
        purchase_price,
        sale_price,
        min_stock_level,
        now,
        now
    ))

    conn.commit()
    conn.close()

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    products = cursor.fetchall()

    conn.close()
    return products

def search_products(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE name LIKE ? OR category LIKE ?
        ORDER BY id DESC
    """, (f"%{keyword}%", f"%{keyword}%"))

    products = cursor.fetchall()
    conn.close()
    return products

def update_product(product_id, name, category, stock_quantity, purchase_price, sale_price, min_stock_level):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE products
        SET name = ?, category = ?, stock_quantity = ?, purchase_price = ?, sale_price = ?, min_stock_level = ?, updated_at = ?
        WHERE id = ?
    """, (
        name,
        category,
        stock_quantity,
        purchase_price,
        sale_price,
        min_stock_level,
        now,
        product_id
    ))

    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

    conn.commit()
    conn.close()

def get_low_stock_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE stock_quantity <= min_stock_level
        ORDER BY stock_quantity ASC
    """)

    products = cursor.fetchall()
    conn.close()
    return products