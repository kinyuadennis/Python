import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime


class Product:
    def __init__(self, id, name, price, stock, category="General"):
        self.id = id
        self.name = name
        self.price = float(price)
        self.stock = int(stock)
        self.category = category

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'category': self.category
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['name'], data['price'], data['stock'], data['category'])


class GroceryShop:
    def __init__(self):
        self.products = {}
        self.sales_history = []
        self.data_file = "grocery_data.json"
        self.load_data()

    def add_product(self, product):
        self.products[product.id] = product
        self.save_data()

    def update_stock(self, product_id, new_stock):
        if product_id in self.products:
            self.products[product_id].stock = new_stock
            self.save_data()
            return True
        return False

    def process_sale(self, items):
        # items is a list of tuples: (product_id, quantity)
        sale_total = 0
        sale_items = []

        for product_id, quantity in items:
            if product_id in self.products:
                product = self.products[product_id]
                if product.stock >= quantity:
                    product.stock -= quantity
                    item_total = product.price * quantity
                    sale_total += item_total
                    sale_items.append({
                        'name': product.name,
                        'quantity': quantity,
                        'price': product.price,
                        'total': item_total
                    })
                else:
                    raise ValueError(f"Insufficient stock for {product.name}")
            else:
                raise ValueError(f"Product {product_id} not found")

        sale_record = {
            'timestamp': datetime.now().isoformat(),
            'items': sale_items,
            'total': sale_total
        }
        self.sales_history.append(sale_record)
        self.save_data()
        return sale_record

    def save_data(self):
        data = {
            'products': {k: v.to_dict() for k, v in self.products.items()},
            'sales_history': self.sales_history
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                self.products = {k: Product.from_dict(v) for k, v in data.get('products', {}).items()}
                self.sales_history = data.get('sales_history', [])
            except:
                self.products = {}
                self.sales_history = []


class GroceryShopGUI:
    def __init__(self):
        self.shop = GroceryShop()
        self.root = tk.Tk()
        self.root.title("Grocery Shop Management System")
        self.root.geometry("800x600")
        self.cart = []  # For sales: list of (product_id, quantity)

        self.setup_ui()

    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Products tab
        self.products_frame = ttk.Frame(notebook)
        notebook.add(self.products_frame, text="Products")
        self.setup_products_tab()

        # Sales tab
        self.sales_frame = ttk.Frame(notebook)
        notebook.add(self.sales_frame, text="Sales")
        self.setup_sales_tab()

        # Reports tab
        self.reports_frame = ttk.Frame(notebook)
        notebook.add(self.reports_frame, text="Reports")
        self.setup_reports_tab()

    def setup_products_tab(self):
        # Add product section
        add_frame = ttk.LabelFrame(self.products_frame, text="Add Product")
        add_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(add_frame, text="ID:").grid(row=0, column=0, padx=5, pady=5)
        self.product_id_entry = ttk.Entry(add_frame)
        self.product_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Name:").grid(row=0, column=2, padx=5, pady=5)
        self.product_name_entry = ttk.Entry(add_frame)
        self.product_name_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(add_frame, text="Price:").grid(row=1, column=0, padx=5, pady=5)
        self.product_price_entry = ttk.Entry(add_frame)
        self.product_price_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Stock:").grid(row=1, column=2, padx=5, pady=5)
        self.product_stock_entry = ttk.Entry(add_frame)
        self.product_stock_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(add_frame, text="Category:").grid(row=2, column=0, padx=5, pady=5)
        self.product_category_entry = ttk.Entry(add_frame)
        self.product_category_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(add_frame, text="Add Product", command=self.add_product).grid(row=2, column=3, padx=5, pady=5)

        # Products list
        list_frame = ttk.LabelFrame(self.products_frame, text="Product Inventory")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview for products
        columns = ("ID", "Name", "Price", "Stock", "Category")
        self.products_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)

        self.products_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons
        button_frame = ttk.Frame(self.products_frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(button_frame, text="Refresh", command=self.refresh_products).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Stock", command=self.update_stock).pack(side="left", padx=5)

        self.refresh_products()

    def setup_sales_tab(self):
        # Cart section
        cart_frame = ttk.LabelFrame(self.sales_frame, text="Shopping Cart")
        cart_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Add to cart
        add_cart_frame = ttk.Frame(cart_frame)
        add_cart_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(add_cart_frame, text="Product ID:").grid(row=0, column=0, padx=5, pady=5)
        self.cart_product_id = ttk.Entry(add_cart_frame)
        self.cart_product_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_cart_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5)
        self.cart_quantity = ttk.Entry(add_cart_frame)
        self.cart_quantity.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(add_cart_frame, text="Add to Cart", command=self.add_to_cart).grid(row=0, column=4, padx=5, pady=5)

        # Cart display
        cart_columns = ("Product ID", "Name", "Quantity", "Price", "Total")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show="headings", height=6)

        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100)

        self.cart_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Cart buttons
        cart_button_frame = ttk.Frame(cart_frame)
        cart_button_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(cart_button_frame, text="Clear Cart", command=self.clear_cart).pack(side="left", padx=5)
        ttk.Button(cart_button_frame, text="Process Sale", command=self.process_sale).pack(side="right", padx=5)

        # Total label
        self.total_label = ttk.Label(cart_button_frame, text="Total: $0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(side="right", padx=20)

    def setup_reports_tab(self):
        # Sales history
        history_frame = ttk.LabelFrame(self.reports_frame, text="Sales History")
        history_frame.pack(fill="both", expand=True, padx=5, pady=5)

        history_columns = ("Date", "Items", "Total")
        self.history_tree = ttk.Treeview(history_frame, columns=history_columns, show="headings")

        for col in history_columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)

        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True)
        history_scrollbar.pack(side="right", fill="y")

        ttk.Button(self.reports_frame, text="Refresh History", command=self.refresh_sales_history).pack(pady=5)

        self.refresh_sales_history()

    def add_product(self):
        try:
            product_id = self.product_id_entry.get().strip()
            name = self.product_name_entry.get().strip()
            price = float(self.product_price_entry.get())
            stock = int(self.product_stock_entry.get())
            category = self.product_category_entry.get().strip() or "General"

            if not product_id or not name:
                messagebox.showerror("Error", "Product ID and Name are required")
                return

            if product_id in self.shop.products:
                messagebox.showerror("Error", "Product ID already exists")
                return

            product = Product(product_id, name, price, stock, category)
            self.shop.add_product(product)

            # Clear entries
            for entry in [self.product_id_entry, self.product_name_entry,
                          self.product_price_entry, self.product_stock_entry,
                          self.product_category_entry]:
                entry.delete(0, tk.END)

            self.refresh_products()
            messagebox.showinfo("Success", "Product added successfully")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def refresh_products(self):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        for product in self.shop.products.values():
            self.products_tree.insert("", "end", values=(
                product.id, product.name, f"${product.price:.2f}",
                product.stock, product.category
            ))

    def update_stock(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to update")
            return

        item = self.products_tree.item(selected[0])
        product_id = item['values'][0]

        new_stock = simpledialog.askinteger("Update Stock",
                                            f"Enter new stock for {item['values'][1]}:")
        if new_stock is not None:
            if self.shop.update_stock(product_id, new_stock):
                self.refresh_products()
                messagebox.showinfo("Success", "Stock updated successfully")

    def add_to_cart(self):
        try:
            product_id = self.cart_product_id.get().strip()
            quantity = int(self.cart_quantity.get())

            if product_id not in self.shop.products:
                messagebox.showerror("Error", "Product not found")
                return

            product = self.shop.products[product_id]
            if product.stock < quantity:
                messagebox.showerror("Error", f"Insufficient stock. Available: {product.stock}")
                return

            # Add to cart
            self.cart.append((product_id, quantity))

            # Update cart display
            total = product.price * quantity
            self.cart_tree.insert("", "end", values=(
                product_id, product.name, quantity, f"${product.price:.2f}", f"${total:.2f}"
            ))

            # Clear entries
            self.cart_product_id.delete(0, tk.END)
            self.cart_quantity.delete(0, tk.END)

            self.update_cart_total()

        except ValueError:
            messagebox.showerror("Error", "Invalid quantity")

    def clear_cart(self):
        self.cart.clear()
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        self.update_cart_total()

    def update_cart_total(self):
        total = 0
        for product_id, quantity in self.cart:
            if product_id in self.shop.products:
                total += self.shop.products[product_id].price * quantity
        self.total_label.config(text=f"Total: ${total:.2f}")

    def process_sale(self):
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty")
            return

        try:
            sale_record = self.shop.process_sale(self.cart)

            # Show receipt
            receipt = "RECEIPT\n" + "=" * 30 + "\n"
            for item in sale_record['items']:
                receipt += f"{item['name']} x{item['quantity']} @ ${item['price']:.2f} = ${item['total']:.2f}\n"
            receipt += "=" * 30 + f"\nTOTAL: ${sale_record['total']:.2f}\n"
            receipt += f"Date: {datetime.fromisoformat(sale_record['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}"

            messagebox.showinfo("Sale Completed", receipt)

            self.clear_cart()
            self.refresh_products()
            self.refresh_sales_history()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def refresh_sales_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for sale in self.shop.sales_history:
            date = datetime.fromisoformat(sale['timestamp']).strftime('%Y-%m-%d %H:%M')
            items_count = len(sale['items'])
            total = f"${sale['total']:.2f}"

            self.history_tree.insert("", "end", values=(date, f"{items_count} items", total))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = GroceryShopGUI()
    app.run()