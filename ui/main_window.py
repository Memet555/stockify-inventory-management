import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ui.dashboard_frame import DashboardFrame
from ui.products_frame import ProductsFrame
from ui.sales_frame import SalesFrame
from ui.reports_frame import ReportsFrame

class MainWindow:
    def __init__(self, app):
        self.app = app
        self.app.title("Envanter & Satış Takip Sistemi")
        self.app.geometry("1400x800")

        self.main_container = ttk.Frame(app)
        self.main_container.pack(fill=BOTH, expand=True)

        self.sidebar = ttk.Frame(self.main_container, width=220)
        self.sidebar.pack(side=LEFT, fill=Y)

        self.content = ttk.Frame(self.main_container)
        self.content.pack(side=LEFT, fill=BOTH, expand=True)

        self.sidebar.pack_propagate(False)

        # Kullanıcı bilgilerini al
        user_role = "kasiyer"
        username = "Kasiyer"
        if hasattr(app, "current_user") and app.current_user:
            username = app.current_user.get("username", "Kasiyer")
            user_role = app.current_user.get("role", "kasiyer")

        title = ttk.Label(
            self.sidebar,
            text="✨ Stockify",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=15)
        
        role_title = "Yönetici" if user_role == "admin" else "Kasiyer"
        user_label = ttk.Label(
            self.sidebar,
            text=f"👤 {username} ({role_title})",
            font=("Arial", 10, "italic"),
            bootstyle=LIGHT
        )
        user_label.pack(pady=(0, 20))

        # Sidebar navigation buttons with Unicode Icons
        ttk.Button(self.sidebar, text="📊 Panel", bootstyle=PRIMARY, width=20,
                   command=lambda: self.show_frame("dashboard")).pack(pady=8)

        ttk.Button(self.sidebar, text="📦 Ürünler", bootstyle=INFO, width=20,
                   command=lambda: self.show_frame("products")).pack(pady=8)

        ttk.Button(self.sidebar, text="🛒 Satışlar", bootstyle=SUCCESS, width=20,
                   command=lambda: self.show_frame("sales")).pack(pady=8)

        reports_btn = ttk.Button(self.sidebar, text="📄 Raporlar", bootstyle=WARNING, width=20,
                   command=lambda: self.show_frame("reports"))
        reports_btn.pack(pady=8)
        
        if user_role == "kasiyer":
            reports_btn.config(state=DISABLED)

        # Theme toggle button packed at the bottom of the sidebar
        self.theme_btn = ttk.Button(
            self.sidebar,
            text="☀️ Aydınlık Mod",
            bootstyle=LIGHT,
            width=20,
            command=self.toggle_theme
        )
        self.theme_btn.pack(side=BOTTOM, pady=(0, 20))

        # Oturumu Kapat butonu
        self.logout_btn = ttk.Button(
            self.sidebar,
            text="🚪 Oturumu Kapat",
            bootstyle=DANGER,
            width=20,
            command=self.logout
        )
        self.logout_btn.pack(side=BOTTOM, pady=10)

        self.current_frame = None
        self.show_frame("dashboard")

    def logout(self):
        from tkinter import messagebox
        confirm = messagebox.askyesno("Oturumu Kapat", "Hesabınızdan çıkış yapmak istediğinize emin misiniz?")
        if confirm:
            self.app.current_user = None
            for widget in self.app.winfo_children():
                widget.destroy()
            
            from ui.login_frame import LoginFrame
            
            def on_login_success(user):
                self.app.current_user = user
                for widget in self.app.winfo_children():
                    widget.destroy()
                MainWindow(self.app)
                
            LoginFrame(self.app, on_login_success)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_frame(self, frame_name):
        self.clear_content()

        if frame_name == "dashboard":
            self.current_frame = DashboardFrame(self.content)
        elif frame_name == "products":
            self.current_frame = ProductsFrame(self.content)
        elif frame_name == "sales":
            self.current_frame = SalesFrame(self.content)
        elif frame_name == "reports":
            self.current_frame = ReportsFrame(self.content)

        self.current_frame.pack(fill=BOTH, expand=True)

    def toggle_theme(self):
        # Toggle theme between darkly (dark) and flatly (light)
        style = ttk.Style()
        current_theme = style.theme_use()
        
        if current_theme == "darkly":
            style.theme_use("flatly")
            self.theme_btn.config(text="🌙 Karanlık Mod", bootstyle=SECONDARY)
        else:
            style.theme_use("darkly")
            self.theme_btn.config(text="☀️ Aydınlık Mod", bootstyle=LIGHT)
            
        # Re-render the current frame to reload Matplotlib chart colors
        if self.current_frame:
            frame_name = "dashboard"
            if isinstance(self.current_frame, ProductsFrame):
                frame_name = "products"
            elif isinstance(self.current_frame, SalesFrame):
                frame_name = "sales"
            elif isinstance(self.current_frame, ReportsFrame):
                frame_name = "reports"
            self.show_frame(frame_name)