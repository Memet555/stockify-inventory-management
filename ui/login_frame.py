import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.auth_service import login_user

class LoginFrame(ttk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, padding=20)
        self.master = master
        self.on_success = on_success
        self.pack(fill=BOTH, expand=True)
        
        # Center container
        center_container = ttk.Frame(self)
        center_container.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        card = ttk.LabelFrame(center_container, text="🔑 Kullanıcı Girişi")
        card.pack()
        
        inner = ttk.Frame(card, padding=30)
        inner.pack()
        
        ttk.Label(inner, text="✨ Stockify Sistem Girişi", font=("Arial", 16, "bold"), bootstyle=PRIMARY).pack(pady=(0, 20))
        
        # Username
        ttk.Label(inner, text="Kullanıcı Adı:").pack(anchor=W, pady=(5, 2))
        self.username_entry = ttk.Entry(inner, width=30)
        self.username_entry.pack(pady=(0, 10))
        self.username_entry.focus()
        
        # Password
        ttk.Label(inner, text="Şifre:").pack(anchor=W, pady=(5, 2))
        self.password_entry = ttk.Entry(inner, show="*", width=30)
        self.password_entry.pack(pady=(0, 20))
        
        # Bind enter key
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        
        # Login button
        login_btn = ttk.Button(inner, text="Giriş Yap", bootstyle=SUCCESS, width=28, command=self.handle_login)
        login_btn.pack(pady=5)
        
        # Help label
        help_label = ttk.Label(inner, text="Varsayılan: admin/admin123 veya kasiyer/kasiyer123", font=("Arial", 8), bootstyle=SECONDARY)
        help_label.pack(pady=(15, 0))
        
    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Giriş Hatası", "Lütfen tüm alanları doldurun.")
            return
            
        user = login_user(username, password)
        if user:
            self.on_success(user)
        else:
            messagebox.showerror("Hata", "Geçersiz kullanıcı adı veya şifre!")
