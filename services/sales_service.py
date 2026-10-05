from database.db import get_connection
from datetime import datetime, timedelta


def create_sale(product_id, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        return {"success": False, "message": "Ürün bulunamadı."}

    current_stock = product["stock_quantity"]
    sale_price = product["sale_price"]
    purchase_price = product["purchase_price"]

    if quantity <= 0:
        conn.close()
        return {"success": False, "message": "Satış adedi 0'dan büyük olmalıdır."}

    if current_stock < quantity:
        conn.close()
        return {"success": False, "message": "Yetersiz stok."}

    total_price = sale_price * quantity
    profit = (sale_price - purchase_price) * quantity
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO sales (product_id, quantity, unit_price, total_price, profit, sale_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (product_id, quantity, sale_price, total_price, profit, now))

    new_stock = current_stock - quantity

    cursor.execute("""
        UPDATE products
        SET stock_quantity = ?, updated_at = ?
        WHERE id = ?
    """, (new_stock, now, product_id))

    conn.commit()
    conn.close()

    return {"success": True, "message": "Satış başarıyla kaydedildi."}


def get_sales_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sales.id,
            products.name AS product_name,
            sales.quantity,
            sales.unit_price,
            sales.total_price,
            sales.profit,
            sales.sale_date
        FROM sales
        INNER JOIN products ON sales.product_id = products.id
        ORDER BY sales.id DESC
    """)

    sales = cursor.fetchall()
    conn.close()
    return sales


def get_today_sales_summary():
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT 
            COUNT(*) as total_sales_count,
            COALESCE(SUM(total_price), 0) as total_revenue
        FROM sales
        WHERE DATE(sale_date) = ?
    """, (today,))

    summary = cursor.fetchone()
    conn.close()
    return summary


def get_total_profit():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(profit), 0) as total_profit FROM sales")
    result = cursor.fetchone()

    conn.close()
    return result["total_profit"]


def get_top_selling_product():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT products.name, SUM(sales.quantity) as total_sold
        FROM sales
        JOIN products ON sales.product_id = products.id
        GROUP BY products.id
        ORDER BY total_sold DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()
    return result


def get_last_7_days_revenue():
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().date()
    labels = []
    revenues = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        short_label = day.strftime("%d.%m")

        cursor.execute("""
            SELECT COALESCE(SUM(total_price), 0) as daily_revenue
            FROM sales
            WHERE DATE(sale_date) = ?
        """, (day_str,))

        result = cursor.fetchone()
        labels.append(short_label)
        revenues.append(float(result["daily_revenue"]))

    conn.close()
    return labels, revenues


def get_top_5_products_chart_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT products.name, COALESCE(SUM(sales.quantity), 0) as total_sold
        FROM sales
        JOIN products ON sales.product_id = products.id
        GROUP BY products.id
        ORDER BY total_sold DESC
        LIMIT 5
    """)

    results = cursor.fetchall()
    conn.close()

    labels = [row["name"] for row in results]
    values = [row["total_sold"] for row in results]

    return labels, values
def get_sales_summary_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) as total_sales,
            COALESCE(SUM(total_price), 0) as total_revenue,
            COALESCE(SUM(profit), 0) as total_profit
        FROM sales
    """)

    result = cursor.fetchone()
    conn.close()
    return result


def get_sales_by_date_range(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sales.id,
            products.name AS product_name,
            sales.quantity,
            sales.unit_price,
            sales.total_price,
            sales.profit,
            sales.sale_date
        FROM sales
        INNER JOIN products ON sales.product_id = products.id
        WHERE DATE(sale_date) BETWEEN ? AND ?
        ORDER BY sales.id DESC
    """, (start_date, end_date))

    sales = cursor.fetchall()
    conn.close()
    return sales


def get_sales_summary_by_date_range(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) as total_sales,
            COALESCE(SUM(total_price), 0) as total_revenue,
            COALESCE(SUM(profit), 0) as total_profit
        FROM sales
        WHERE DATE(sale_date) BETWEEN ? AND ?
    """, (start_date, end_date))

    result = cursor.fetchone()
    conn.close()
    return result


def get_ai_sales_forecast():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tüm ürünlerin stok durumunu çek
    cursor.execute("SELECT id, name, stock_quantity, min_stock_level FROM products")
    products = cursor.fetchall()
    
    forecasts = []
    
    # Son 10 günün satış hızını referans alarak doğrusal tahminleme yap
    ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    
    for p in products:
        p_id = p["id"]
        p_name = p["name"]
        stock = p["stock_quantity"]
        min_level = p["min_stock_level"]
        
        # Son 10 gündeki toplam satış adedini getir
        cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0) as sold_qty
            FROM sales
            WHERE product_id = ? AND DATE(sale_date) >= ?
        """, (p_id, ten_days_ago))
        
        sold_qty = cursor.fetchone()["sold_qty"]
        
        # Günlük satış hızı (Hız = Toplam Satış / Gün Sayısı)
        daily_velocity = sold_qty / 10.0
        
        # Yapay Zeka Önümüzdeki 7 Günlük Satış Tahmini (Doğrusal Ekstrapolasyon)
        next_7_days_forecast = round(daily_velocity * 7, 1)
        
        # Stoğun kaç günde tükeneceğinin tahmini (Stok / Hız)
        if daily_velocity > 0:
            days_until_out = round(stock / daily_velocity, 1)
            if days_until_out == 0:
                status_desc = "Stok Tükendi!"
            elif days_until_out <= 3:
                status_desc = "Kritik Risk"
            elif days_until_out <= 7:
                status_desc = "Düşük Risk"
            else:
                status_desc = "Güvenli"
        else:
            days_until_out = 999.0
            status_desc = "Satış Yok"
            
        forecasts.append({
            "product_id": p_id,
            "product_name": p_name,
            "stock_quantity": stock,
            "min_stock_level": min_level,
            "daily_velocity": daily_velocity,
            "forecast_7_days": next_7_days_forecast,
            "days_until_out": days_until_out,
            "status": status_desc
        })
        
    conn.close()
    # En acil tükenme riski olandan güvenli olana göre sırala
    forecasts.sort(key=lambda x: x["days_until_out"])
    return forecasts