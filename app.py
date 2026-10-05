import ttkbootstrap as ttk
from database.db import initialize_database
from ui.login_frame import LoginFrame
from ui.main_window import MainWindow

def main():
    # Veri tabanını initialize et ve örnek verileri doldur
    initialize_database()

    app = ttk.Window(themename="darkly")
    app.title("Envanter & Satış Takip Sistemi")
    app.geometry("1400x800")
    
    # Oturum bilgilerini tutmak için nesne tanımla
    app.current_user = None

    def on_login_success(user):
        app.current_user = user
        # Giriş ekranındaki tüm bileşenleri temizle
        for widget in app.winfo_children():
            widget.destroy()
        # Ana yönetim panelini yükle
        MainWindow(app)

    # İlk olarak giriş panelini yükle
    LoginFrame(app, on_login_success)
    app.mainloop()

if __name__ == "__main__":
    main()