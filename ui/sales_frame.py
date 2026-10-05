import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.product_service import get_all_products
from services.sales_service import create_sale, get_sales_history, get_today_sales_summary
from services.invoice_service import generate_html_invoice


class SalesFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)
        self.pack(fill=BOTH, expand=True)

        self.products = []
        self.product_map = {}

        title = ttk.Label(self, text="Satış Yönetimi", font=("Arial", 20, "bold"))
        title.pack(pady=(0, 15))

        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill=X, pady=(0, 15))

        self.summary_label = ttk.Label(summary_frame, text="", font=("Arial", 11))
        self.summary_label.pack(anchor=W)

        form_frame = ttk.LabelFrame(self, text="Satış Formu")
        form_frame.pack(fill=X, pady=10, padx=10)

        ttk.Label(form_frame, text="Ürün Seç").grid(row=0, column=0, padx=8, pady=8, sticky=W)
        self.product_combo = ttk.Combobox(form_frame, width=40, state="readonly")
        self.product_combo.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(form_frame, text="Satış Adedi").grid(row=1, column=0, padx=8, pady=8, sticky=W)
        self.quantity_entry = ttk.Entry(form_frame, width=20)
        self.quantity_entry.grid(row=1, column=1, padx=8, pady=8, sticky=W)

        ttk.Button(
            self,
            text="Satışı Kaydet",
            bootstyle=SUCCESS,
            command=self.handle_sale
        ).pack(pady=10)

        columns = ("ID", "Ürün", "Adet", "Birim Fiyat", "Toplam", "Kâr", "Tarih")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=CENTER, width=140)

        self.tree.pack(fill=BOTH, expand=True, pady=10)

        self.load_products()
        self.load_sales_history()
        self.load_summary()

    def load_products(self):
        self.products = get_all_products()
        combo_values = []
        self.product_map = {}

        for product in self.products:
            display_text = f'{product["id"]} - {product["name"]} (Stok: {product["stock_quantity"]})'
            combo_values.append(display_text)
            self.product_map[display_text] = product["id"]

        self.product_combo["values"] = combo_values

        if combo_values:
            self.product_combo.current(0)

    def handle_sale(self):
        selected_product = self.product_combo.get().strip()

        if not selected_product:
            messagebox.showerror("Hata", "Lütfen bir ürün seçin.")
            return

        try:
            quantity = int(self.quantity_entry.get())
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir adet girin.")
            return

        product_id = self.product_map[selected_product]
        product = next((p for p in self.products if p["id"] == product_id), None)
        unit_price = product["sale_price"] if product else 0
        product_name = product["name"] if product else "Bilinmeyen Ürün"
        
        result = create_sale(product_id, quantity)

        if result["success"]:
            total_price = unit_price * quantity
            ask_invoice = messagebox.askyesno(
                "Başarılı",
                f"{result['message']}\n\nBu satış için fatura/makbuz oluşturulmasını ve tarayıcıda açılmasını ister misiniz?"
            )
            if ask_invoice:
                cashier_name = "Kasiyer"
                try:
                    app = self.winfo_toplevel()
                    if hasattr(app, "current_user") and app.current_user:
                        cashier_name = app.current_user.get("username", "Kasiyer")
                        role = app.current_user.get("role", "")
                        cashier_name = f"{cashier_name} ({role.upper()})"
                except Exception:
                    pass
                
                generate_html_invoice(product_name, quantity, unit_price, total_price, cashier_name)
                
            self.quantity_entry.delete(0, "end")
            self.load_products()
            self.load_sales_history()
            self.load_summary()
        else:
            messagebox.showerror("Hata", result["message"])

    def load_sales_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        sales = get_sales_history()

        for sale in sales:
            self.tree.insert("", "end", values=(
                sale["id"],
                sale["product_name"],
                sale["quantity"],
                sale["unit_price"],
                sale["total_price"],
                sale["profit"],
                sale["sale_date"]
            ))

    def load_summary(self):
        summary = get_today_sales_summary()
        sales_count = summary["total_sales_count"]
        total_revenue = summary["total_revenue"]

        self.summary_label.config(
            text=f"Bugünkü Satış Sayısı: {sales_count} | Bugünkü Toplam Gelir: {total_revenue:.2f} TL"
        )