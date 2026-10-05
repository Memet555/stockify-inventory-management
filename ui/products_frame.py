import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.product_service import (
    add_product,
    get_all_products,
    search_products,
    update_product,
    delete_product,
    get_low_stock_products
)

class ProductsFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)
        self.pack(fill=BOTH, expand=True)

        self.selected_product_id = None

        title = ttk.Label(self, text="Ürün Yönetimi", font=("Arial", 20, "bold"))
        title.pack(pady=(0, 15))

        top_frame = ttk.Frame(self)
        top_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(top_frame, text="Ara:").pack(side=LEFT, padx=(0, 8))
        self.search_entry = ttk.Entry(top_frame, width=30)
        self.search_entry.pack(side=LEFT, padx=(0, 8))

        ttk.Button(top_frame, text="Ara", bootstyle=INFO, command=self.handle_search).pack(side=LEFT, padx=(0, 8))
        ttk.Button(top_frame, text="Tümünü Göster", bootstyle=SECONDARY, command=self.load_products).pack(side=LEFT, padx=(0, 8))
        ttk.Button(top_frame, text="Düşük Stok", bootstyle=WARNING, command=self.show_low_stock).pack(side=LEFT)

        form_frame = ttk.LabelFrame(self, text="Ürün Formu")
        form_frame.pack(fill=X, pady=10, padx=15)
        form_frame.pack(fill=X, pady=10)

        ttk.Label(form_frame, text="Ürün Adı").grid(row=0, column=0, padx=8, pady=8, sticky=W)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(form_frame, text="Kategori").grid(row=0, column=2, padx=8, pady=8, sticky=W)
        self.category_entry = ttk.Entry(form_frame, width=30)
        self.category_entry.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(form_frame, text="Stok").grid(row=1, column=0, padx=8, pady=8, sticky=W)
        self.stock_entry = ttk.Entry(form_frame, width=30)
        self.stock_entry.grid(row=1, column=1, padx=8, pady=8)

        ttk.Label(form_frame, text="Alış Fiyatı").grid(row=1, column=2, padx=8, pady=8, sticky=W)
        self.purchase_entry = ttk.Entry(form_frame, width=30)
        self.purchase_entry.grid(row=1, column=3, padx=8, pady=8)

        ttk.Label(form_frame, text="Satış Fiyatı").grid(row=2, column=0, padx=8, pady=8, sticky=W)
        self.sale_entry = ttk.Entry(form_frame, width=30)
        self.sale_entry.grid(row=2, column=1, padx=8, pady=8)

        ttk.Label(form_frame, text="Min Stok Seviyesi").grid(row=2, column=2, padx=8, pady=8, sticky=W)
        self.min_stock_entry = ttk.Entry(form_frame, width=30)
        self.min_stock_entry.grid(row=2, column=3, padx=8, pady=8)
        self.min_stock_entry.insert(0, "5")

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=X, pady=10)

        ttk.Button(button_frame, text="Kaydet", bootstyle=SUCCESS, command=self.save_product).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Güncelle", bootstyle=PRIMARY, command=self.edit_product).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Sil", bootstyle=DANGER, command=self.remove_product).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Formu Temizle", bootstyle=SECONDARY, command=self.clear_form).pack(side=LEFT, padx=5)

        # Kasiyer yetki kontrolü: Kasiyer ise ürün ekleme, silme ve güncellemeyi engelle
        user_role = "kasiyer"
        try:
            app = self.winfo_toplevel()
            if hasattr(app, "current_user") and app.current_user:
                user_role = app.current_user.get("role", "kasiyer")
        except Exception:
            pass

        if user_role == "kasiyer":
            for child in form_frame.winfo_children():
                if isinstance(child, ttk.Entry):
                    child.config(state=DISABLED)
            for child in button_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state=DISABLED)

        columns = ("ID", "Ad", "Kategori", "Stok", "Alış", "Satış", "Min Stok")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=CENTER, width=130)

        self.tree.pack(fill=BOTH, expand=True, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.load_products()

    def validate_form(self):
        name = self.name_entry.get().strip()
        category = self.category_entry.get().strip()

        if not name:
            messagebox.showerror("Hata", "Ürün adı boş olamaz.")
            return None

        try:
            stock_quantity = int(self.stock_entry.get())
            purchase_price = float(self.purchase_entry.get())
            sale_price = float(self.sale_entry.get())
            min_stock_level = int(self.min_stock_entry.get())

            if stock_quantity < 0 or purchase_price < 0 or sale_price < 0 or min_stock_level < 0:
                messagebox.showerror("Hata", "Stok, fiyatlar ve minimum stok seviyesi 0 veya daha büyük olmalıdır.")
                return None
        except ValueError:
            messagebox.showerror("Hata", "Stok ve fiyat alanlarını doğru girin.")
            return None

        return {
            "name": name,
            "category": category,
            "stock_quantity": stock_quantity,
            "purchase_price": purchase_price,
            "sale_price": sale_price,
            "min_stock_level": min_stock_level
        }

    def save_product(self):
        data = self.validate_form()
        if not data:
            return

        add_product(
            data["name"],
            data["category"],
            data["stock_quantity"],
            data["purchase_price"],
            data["sale_price"],
            data["min_stock_level"]
        )

        messagebox.showinfo("Başarılı", "Ürün başarıyla eklendi.")
        self.clear_form()
        self.load_products()

    def edit_product(self):
        if not self.selected_product_id:
            messagebox.showwarning("Uyarı", "Lütfen güncellenecek bir ürün seçin.")
            return

        data = self.validate_form()
        if not data:
            return

        update_product(
            self.selected_product_id,
            data["name"],
            data["category"],
            data["stock_quantity"],
            data["purchase_price"],
            data["sale_price"],
            data["min_stock_level"]
        )

        messagebox.showinfo("Başarılı", "Ürün güncellendi.")
        self.clear_form()
        self.load_products()

    def remove_product(self):
        if not self.selected_product_id:
            messagebox.showwarning("Uyarı", "Lütfen silinecek bir ürün seçin.")
            return

        confirm = messagebox.askyesno("Onay", "Seçili ürünü silmek istediğine emin misin?")
        if not confirm:
            return

        delete_product(self.selected_product_id)
        messagebox.showinfo("Başarılı", "Ürün silindi.")
        self.clear_form()
        self.load_products()

    def handle_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_products()
            return

        products = search_products(keyword)
        self.populate_tree(products)

    def show_low_stock(self):
        products = get_low_stock_products()
        self.populate_tree(products)

        if not products:
            messagebox.showinfo("Bilgi", "Düşük stokta ürün bulunamadı.")

    def load_products(self):
        products = get_all_products()
        self.populate_tree(products)

    def populate_tree(self, products):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for product in products:
            self.tree.insert("", "end", values=(
                product["id"],
                product["name"],
                product["category"],
                product["stock_quantity"],
                product["purchase_price"],
                product["sale_price"],
                product["min_stock_level"]
            ))

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_product_id = int(values[0])

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, values[1])

        self.category_entry.delete(0, "end")
        self.category_entry.insert(0, values[2])

        self.stock_entry.delete(0, "end")
        self.stock_entry.insert(0, values[3])

        self.purchase_entry.delete(0, "end")
        self.purchase_entry.insert(0, values[4])

        self.sale_entry.delete(0, "end")
        self.sale_entry.insert(0, values[5])

        self.min_stock_entry.delete(0, "end")
        self.min_stock_entry.insert(0, values[6])

    def clear_form(self):
        self.selected_product_id = None

        self.name_entry.delete(0, "end")
        self.category_entry.delete(0, "end")
        self.stock_entry.delete(0, "end")
        self.purchase_entry.delete(0, "end")
        self.sale_entry.delete(0, "end")
        self.min_stock_entry.delete(0, "end")
        self.min_stock_entry.insert(0, "5")