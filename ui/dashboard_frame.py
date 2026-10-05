import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from services.product_service import get_all_products, get_low_stock_products
from services.sales_service import (
    get_today_sales_summary,
    get_sales_history,
    get_total_profit,
    get_top_selling_product,
    get_last_7_days_revenue,
    get_top_5_products_chart_data,
    get_ai_sales_forecast,
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DashboardFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)

        title = ttk.Label(self, text="Dashboard", font=("Arial", 18, "bold"))
        title.pack(anchor=W, pady=(0, 10))

        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=X, pady=(0, 10))

        products = get_all_products()
        low_stock_products = get_low_stock_products()
        today_summary = get_today_sales_summary()
        sales_history = get_sales_history()
        total_profit = get_total_profit()
        top_product = get_top_selling_product()

        total_products = len(products)
        low_stock_count = len(low_stock_products)
        today_sales_count = today_summary["total_sales_count"]
        today_revenue = today_summary["total_revenue"]
        total_sales_records = len(sales_history)
        top_product_name = top_product["name"] if top_product else "Yok"

        # Ürün adı kart tasarımı için çok uzunsa kısalt
        display_top_product = top_product_name[:18] + "..." if len(top_product_name) > 18 else top_product_name

        self.create_stat_card(stats_frame, "Toplam Ürün", total_products, 0, 0)
        self.create_stat_card(stats_frame, "Düşük Stok", low_stock_count, 0, 1)
        self.create_stat_card(stats_frame, "Bugünkü Satış", today_sales_count, 0, 2)
        self.create_stat_card(stats_frame, "Bugünkü Gelir", f"{today_revenue:.2f} TL", 0, 3)
        self.create_stat_card(stats_frame, "Toplam Kâr", f"{total_profit:.2f} TL", 0, 4)
        self.create_stat_card(stats_frame, "En Çok Satılan", display_top_product, 0, 5)

        charts_frame = ttk.Frame(self)
        charts_frame.pack(fill=BOTH, expand=False, pady=(0, 10))

        revenue_chart_frame = ttk.LabelFrame(charts_frame, text="Son 7 Gün Gelir Grafiği")
        revenue_chart_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        top_products_chart_frame = ttk.LabelFrame(charts_frame, text="En Çok Satılan 5 Ürün")
        top_products_chart_frame.pack(side=LEFT, fill=BOTH, expand=True)

        self.create_revenue_chart(revenue_chart_frame)
        self.create_top_products_chart(top_products_chart_frame)

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=BOTH, expand=True)

        low_stock_frame = ttk.LabelFrame(bottom_frame, text="Düşük Stokta Olan Ürünler")
        low_stock_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        low_stock_list = ttk.Treeview(
            low_stock_frame,
            columns=("ID", "Ad", "Stok", "Min"),
            show="headings",
            height=5
        )
        low_stock_list.pack(fill=BOTH, expand=True, padx=8, pady=5)

        # Configure warning/critical alert colors based on light/dark mode
        style = ttk.Style()
        current_theme = style.theme_use()
        if current_theme == "darkly":
            low_stock_list.tag_configure("critical", background="#5c2020", foreground="#f8d7da")
            low_stock_list.tag_configure("warning", background="#5c4315", foreground="#fff3cd")
        else:
            low_stock_list.tag_configure("critical", background="#f8d7da", foreground="#721c24")
            low_stock_list.tag_configure("warning", background="#fff3cd", foreground="#856404")

        low_stock_list.column("ID", anchor=CENTER, width=40)
        low_stock_list.column("Ad", anchor=W, width=160)
        low_stock_list.column("Stok", anchor=CENTER, width=80)
        low_stock_list.column("Min", anchor=CENTER, width=80)

        for col in ("ID", "Ad", "Stok", "Min"):
            low_stock_list.heading(col, text=col)

        for product in low_stock_products:
            stock = product["stock_quantity"]
            # Tag critical if completely out of stock, warning if below min level
            tag = "critical" if stock == 0 else "warning"
            low_stock_list.insert("", "end", values=(
                product["id"],
                product["name"],
                product["stock_quantity"],
                product["min_stock_level"]
            ), tags=(tag,))

        ai_frame = ttk.LabelFrame(bottom_frame, text="🤖 Yapay Zeka Satış & Stok Analizi")
        ai_frame.pack(side=LEFT, fill=BOTH, expand=True)

        ai_list = ttk.Treeview(
            ai_frame,
            columns=("Ürün", "Tahmin", "Tükenme", "Durum"),
            show="headings",
            height=5
        )
        ai_list.pack(fill=BOTH, expand=True, padx=8, pady=5)

        # Configure warning/critical alert colors based on light/dark mode
        if current_theme == "darkly":
            ai_list.tag_configure("critical", background="#5c2020", foreground="#f8d7da")
            ai_list.tag_configure("warning", background="#5c4315", foreground="#fff3cd")
        else:
            ai_list.tag_configure("critical", background="#f8d7da", foreground="#721c24")
            ai_list.tag_configure("warning", background="#fff3cd", foreground="#856404")

        for col in ("Ürün", "Tahmin", "Tükenme", "Durum"):
            ai_list.heading(col, text=col)
            
        ai_list.column("Ürün", anchor=W, width=160)
        ai_list.column("Tahmin", anchor=CENTER, width=80)
        ai_list.column("Tükenme", anchor=CENTER, width=80)
        ai_list.column("Durum", anchor=CENTER, width=100)

        ai_forecasts = get_ai_sales_forecast()
        # Display top 5 urgent forecasts
        for f in ai_forecasts[:5]:
            days_out = f"{f['days_until_out']} gün" if f['days_until_out'] < 900 else "Süresiz"
            forecast_text = f"{f['forecast_7_days']} adet"
            
            # Decide tag based on days remaining
            if f['days_until_out'] <= 3.0:
                tag = "critical"
            elif f['days_until_out'] <= 7.0:
                tag = "warning"
            else:
                tag = ""
                
            ai_list.insert("", "end", values=(
                f["product_name"],
                forecast_text,
                days_out,
                f["status"]
            ), tags=(tag,) if tag else ())

    def create_stat_card(self, parent, title, value, row, column):
        card = ttk.LabelFrame(parent, text=title)
        card.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")

        label = ttk.Label(card, text=str(value), font=("Arial", 12, "bold"))
        label.pack(padx=10, pady=12)

        parent.grid_columnconfigure(column, weight=1)

    def style_chart(self, fig, ax):
        # Grafik arka planını ve renk paletini aktif temayla uyumlu hale getir
        style = ttk.Style()
        current_theme = style.theme_use()
        
        if current_theme == "darkly":
            bg_color = "#222222"
            ax_color = "#2b2b2b"
            text_color = "#ffffff"
            tick_color = "#adb5bd"
            grid_color = "#ffffff"
            spine_color = "#444444"
        else:
            bg_color = "#ffffff"
            ax_color = "#f8f9fa"
            text_color = "#212529"
            tick_color = "#495057"
            grid_color = "#000000"
            spine_color = "#dee2e6"
            
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(ax_color)
        
        # Izgara çizgileri
        ax.grid(True, linestyle="--", alpha=0.15, color=grid_color)
        ax.set_axisbelow(True) # Izgaranın barların/çizgilerin arkasında kalmasını sağla
        
        # Eksen işaretleri, etiketler, başlıklar ve kenarlık renklerini ayarla
        ax.tick_params(colors=tick_color, which="both", labelsize=9)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.title.set_color(text_color)
        
        # Kenarlık çizgilerini stilize et
        for spine in ax.spines.values():
            spine.set_color(spine_color)

    def create_revenue_chart(self, parent):
        labels, revenues = get_last_7_days_revenue()

        fig = Figure(figsize=(5, 2.3), dpi=100)
        ax = fig.add_subplot(111)
        # Modern alan grafiği (Area Chart) çizimi
        ax.plot(labels, revenues, marker="o", color="#17a2b8", linewidth=2.5, markersize=6)
        ax.fill_between(labels, revenues, color="#17a2b8", alpha=0.15)
        ax.set_title("7 Günlük Gelir")
        ax.set_xlabel("Tarih")
        ax.set_ylabel("Gelir (TL)")
        
        self.style_chart(fig, ax)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=5, pady=5)

    def create_top_products_chart(self, parent):
        labels, values = get_top_5_products_chart_data()

        fig = Figure(figsize=(5, 2.3), dpi=100)
        ax = fig.add_subplot(111)

        if labels and values:
            ax.bar(labels, values, color="#28a745", width=0.4)
            ax.set_title("En Çok Satılan Ürünler")
            ax.set_xlabel("Ürün")
            ax.set_ylabel("Satış Adedi")
            # Etiketleri ayarla ve üst üste binmelerini önlemek için döndür
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=15, ha="right")
        else:
            ax.text(0.5, 0.5, "Henüz satış verisi yok", ha="center", va="center", color="#ffffff")
            ax.set_title("En Çok Satılan Ürünler")

        self.style_chart(fig, ax)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=5, pady=5)