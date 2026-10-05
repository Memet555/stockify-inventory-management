import os
import webbrowser
from datetime import datetime

def generate_html_invoice(product_name, quantity, unit_price, total_price, cashier_name="Kasiyer"):
    os.makedirs("exports", exist_ok=True)
    
    invoice_id = datetime.now().strftime("%Y%m%d%H%M%S")
    date_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    file_path = os.path.join("exports", f"fatura_{invoice_id}.html")
    
    html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Satış Faturası - #{invoice_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f3f4f6;
            margin: 0;
            padding: 40px;
            color: #333;
        }}
        .invoice-card {{
            background: #ffffff;
            max-width: 600px;
            margin: 0 auto;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            padding: 40px;
            border: 1px solid #e5e7eb;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #10b981;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 24px;
            font-weight: bold;
            color: #10b981;
        }}
        .title {{
            font-size: 18px;
            color: #6b7280;
            text-align: right;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        .meta-item strong {{
            color: #4b5563;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        .table th {{
            background-color: #f9fafb;
            color: #374151;
            font-weight: 600;
            text-align: left;
            padding: 12px;
            border-bottom: 2px solid #e5e7eb;
        }}
        .table td {{
            padding: 12px;
            border-bottom: 1px solid #f3f4f6;
        }}
        .total-section {{
            text-align: right;
            font-size: 18px;
            font-weight: bold;
            color: #111827;
            padding-top: 15px;
            border-top: 2px solid #e5e7eb;
        }}
        .footer {{
            text-align: center;
            font-size: 12px;
            color: #9ca3af;
            margin-top: 40px;
        }}
        .print-btn {{
            display: block;
            width: 100%;
            background-color: #10b981;
            color: white;
            border: none;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            margin-top: 20px;
            text-align: center;
            text-decoration: none;
        }}
        .print-btn:hover {{
            background-color: #059669;
        }}
        @media print {{
            body {{
                background-color: white;
                padding: 0;
            }}
            .invoice-card {{
                box-shadow: none;
                border: none;
                padding: 0;
            }}
            .print-btn {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="invoice-card">
        <div class="header">
            <div class="logo">✨ Stockify</div>
            <div class="title">SATIŞ FATURASI</div>
        </div>
        
        <div class="meta-grid">
            <div class="meta-item">
                <strong>Fatura No:</strong> #{invoice_id}<br>
                <strong>Tarih:</strong> {date_str}
            </div>
            <div class="meta-item" style="text-align: right;">
                <strong>İşlemi Yapan:</strong> {cashier_name}<br>
                <strong>Durum:</strong> Ödendi
            </div>
        </div>
        
        <table class="table">
            <thead>
                <tr>
                    <th>Ürün Adı</th>
                    <th style="text-align: center;">Adet</th>
                    <th style="text-align: right;">Birim Fiyat</th>
                    <th style="text-align: right;">Toplam Tutar</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{product_name}</td>
                    <td style="text-align: center;">{quantity}</td>
                    <td style="text-align: right;">{unit_price:.2f} TL</td>
                    <td style="text-align: right;">{total_price:.2f} TL</td>
                </tr>
            </tbody>
        </table>
        
        <div class="total-section">
            Genel Toplam: {total_price:.2f} TL
        </div>
        
        <button class="print-btn" onclick="window.print()">Yazdır / PDF Olarak Kaydet</button>
        
        <div class="footer">
            Stockify Envanter & Satış Sistemi aracılığıyla oluşturulmuştur.<br>
            Bizi tercih ettiğiniz için teşekkür ederiz!
        </div>
    </div>
</body>
</html>
"""
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    webbrowser.open(os.path.abspath(file_path))
    return file_path
