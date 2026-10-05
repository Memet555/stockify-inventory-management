import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.sales_service import (
    get_sales_history,
    get_sales_summary_data,
    get_sales_by_date_range,
    get_sales_summary_by_date_range
)
import csv
from pathlib import Path
from datetime import datetime


class ReportsFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)

        title = ttk.Label(self, text="Raporlar", font=("Arial", 22, "bold"))
        title.pack(anchor=W, pady=(0, 20))

        filter_frame = ttk.LabelFrame(self, text="Filtreleme")
        filter_frame.pack(fill=X, pady=(0, 15))

        ttk.Label(filter_frame, text="Başlangıç Tarihi (YYYY-MM-DD)").grid(row=0, column=0, padx=8, pady=8, sticky=W)
        self.start_date_entry = ttk.Entry(filter_frame, width=20)
        self.start_date_entry.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(filter_frame, text="Bitiş Tarihi (YYYY-MM-DD)").grid(row=0, column=2, padx=8, pady=8, sticky=W)
        self.end_date_entry = ttk.Entry(filter_frame, width=20)
        self.end_date_entry.grid(row=0, column=3, padx=8, pady=8)

        today = datetime.now().strftime("%Y-%m-%d")
        self.start_date_entry.insert(0, today)
        self.end_date_entry.insert(0, today)

        ttk.Button(filter_frame, text="Filtrele", bootstyle=INFO, command=self.apply_filter).grid(row=0, column=4, padx=8, pady=8)
        ttk.Button(filter_frame, text="Tümünü Göster", bootstyle=SECONDARY, command=self.load_reports).grid(row=0, column=5, padx=8, pady=8)

        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill=X, pady=(0, 15))

        self.total_sales_label = ttk.Label(summary_frame, text="", font=("Arial", 11, "bold"))
        self.total_sales_label.pack(anchor=W, pady=2)

        self.total_revenue_label = ttk.Label(summary_frame, text="", font=("Arial", 11, "bold"))
        self.total_revenue_label.pack(anchor=W, pady=2)

        self.total_profit_label = ttk.Label(summary_frame, text="", font=("Arial", 11, "bold"))
        self.total_profit_label.pack(anchor=W, pady=2)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=X, pady=(0, 10))

        ttk.Button(
            button_frame,
            text="CSV Olarak Dışa Aktar",
            bootstyle=SUCCESS,
            command=self.export_csv
        ).pack(side=LEFT)

        columns = ("ID", "Ürün", "Adet", "Birim Fiyat", "Toplam", "Kâr", "Tarih")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=18)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=CENTER, width=140)

        self.tree.pack(fill=BOTH, expand=True, pady=10)

        self.current_data = []
        self.load_reports()

    def load_reports(self):
        sales = get_sales_history()
        summary = get_sales_summary_data()
        self.current_data = sales

        self.populate_tree(sales)
        self.update_summary(summary)

    def apply_filter(self):
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()

        if not self.validate_date(start_date) or not self.validate_date(end_date):
            messagebox.showerror("Hata", "Tarih formatı YYYY-MM-DD olmalıdır.")
            return

        if datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d"):
            messagebox.showerror("Hata", "Başlangıç tarihi bitiş tarihinden sonra olamaz.")
            return

        sales = get_sales_by_date_range(start_date, end_date)
        summary = get_sales_summary_by_date_range(start_date, end_date)
        self.current_data = sales

        self.populate_tree(sales)
        self.update_summary(summary)

    def populate_tree(self, sales):
        for item in self.tree.get_children():
            self.tree.delete(item)

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

    def update_summary(self, summary):
        self.total_sales_label.config(text=f"Toplam Satış Kaydı: {summary['total_sales']}")
        self.total_revenue_label.config(text=f"Toplam Gelir: {summary['total_revenue']:.2f} TL")
        self.total_profit_label.config(text=f"Toplam Kâr: {summary['total_profit']:.2f} TL")

    def export_csv(self):
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)

        file_path = export_dir / "sales_report.csv"

        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Ürün", "Adet", "Birim Fiyat", "Toplam", "Kâr", "Tarih"])

            for sale in self.current_data:
                writer.writerow([
                    sale["id"],
                    sale["product_name"],
                    sale["quantity"],
                    sale["unit_price"],
                    sale["total_price"],
                    sale["profit"],
                    sale["sale_date"]
                ])

        messagebox.showinfo("Başarılı", f"Rapor dışa aktarıldı:\n{file_path}")

    def validate_date(self, date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False