import sqlite3
from tkinter import END, Button, Entry, Frame, Label, Text, Scrollbar, Tk, messagebox


class POSApplication(Tk):
    def __init__(self):
        super().__init__()

        self.title("Arise Coffee PH POS")
        self.geometry("800x600")
        self.configure(bg="#f8f1e5")

        self.order = []
        self.total = 0
        self.reset_stock = {}

        self.setup_ui()
        self.load_inventory()

    def setup_ui(self):
        title_label = Label(self, text="Welcome to Arise Coffee PH!", font=("Arial", 24), bg="#f8f1e5")
        title_label.pack(pady=10)

        self.inventory_frame = Frame(self, bg="#f8f1e5")
        self.inventory_frame.pack(pady=10)

        inventory_label = Label(self.inventory_frame, text="Menu", font=("Arial", 20), bg="#f8f1e5")
        inventory_label.pack()

        self.inventory_listbox = Text(self.inventory_frame, width=80, height=10)
        self.inventory_listbox.pack(side="left")

        inventory_scrollbar = Scrollbar(self.inventory_frame)
        inventory_scrollbar.pack(side="right", fill="y")

        self.inventory_listbox.config(yscrollcommand=inventory_scrollbar.set)
        inventory_scrollbar.config(command=self.inventory_listbox.yview)

        order_entry_frame = Frame(self, bg="#f8f1e5")
        order_entry_frame.pack(pady=10)

        order_entry_label = Label(order_entry_frame, text="Add to Order", font=("Arial", 20), bg="#f8f1e5")
        order_entry_label.grid(row=0, columnspan=2, pady=10)

        Label(order_entry_frame, text="Item Code", font=("Arial", 14)).grid(row=1, column=0, padx=5, pady=10, sticky='w')
        self.item_code_entry = Entry(order_entry_frame, font=("Arial", 14))
        self.item_code_entry.grid(row=1, column=1, padx=5, pady=10)

        # Label and Entry for Quantity
        Label(order_entry_frame, text="Quantity", font=("Arial", 14)).grid(row=2, column=0, padx=5, pady=10, sticky='w')
        self.quantity_entry = Entry(order_entry_frame, font=("Arial", 14))
        self.quantity_entry.grid(row=2, column=1, padx=5, pady=10)

        add_button = Button(order_entry_frame, text="Add to Order", font=("Arial", 14), command=self.add_to_order, bg="#4caf50", fg="white")
        add_button.grid(row=3, columnspan=2, pady=5)

        order_frame = Frame(self, bg="#f8f1e5")
        order_frame.pack(pady=10)

        order_label = Label(order_frame, text="Current Order", font=("Arial", 20), bg="#f8f1e5")
        order_label.pack()

        self.order_listbox = Text(order_frame, width=80, height=10)
        self.order_listbox.pack()

        action_buttons_frame = Frame(self, bg="#f8f1e5")
        action_buttons_frame.pack(pady=10)

        finalize_order_button = Button(action_buttons_frame, text="Finalize Order", font=("Arial", 14), command=self.finalize_order, bg="#2196f3", fg="white")
        finalize_order_button.grid(row=0, column=0, padx=5)

        reset_order_button = Button(action_buttons_frame, text="Reset Order", font=("Arial", 14), command=self.reset_order, bg="#f44336", fg="white")
        reset_order_button.grid(row=0, column=1, padx=5)

        sign_out_button = Button(action_buttons_frame, text="Sign Out", font=("Arial", 14), command=self.sign_out, bg="#9e9e9e", fg="white")
        sign_out_button.grid(row=0, column=2, padx=5)

    def load_inventory(self):
        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute('SELECT code, name, price, stock, category FROM Inventory')
        self.inventory = {row[0]: {'name': row[1], 'price': row[2], 'stock': row[3], 'category': row[4]} for row in c.fetchall()}
        conn.close()
        self.update_inventory_display()

    def update_inventory_display(self):
        self.inventory_listbox.delete(1.0, END)
        self.inventory_listbox.insert(END, f"{'ID':<5}{'Code':<10}{'Name':<30}{'Price':<10}{'Stock':<10}{'Category':<15}\n")
        self.inventory_listbox.insert(END, "-" * 90 + "\n")

        for idx, (code, details) in enumerate(self.inventory.items(), start=1):
            id_display = f"{idx:<5}"  # Assuming you want a running ID displayed
            name_display = f"{details['name']:<30}"
            price_display = f"₱{details['price']:<8.2f}"
            stock_display = f"{details['stock']:<10}"
            category_display = f"{details['category']:<15}"

            self.inventory_listbox.insert(END, f"{id_display}{code:<10}{name_display}{price_display}{stock_display}{category_display}\n")

        self.inventory_listbox.insert(END, "-" * 90 + "\n")

    def add_to_order(self):
        code = self.item_code_entry.get().upper().strip()
        try:
            quantity = int(self.quantity_entry.get().strip())
            if code in self.inventory and self.inventory[code]['stock'] >= quantity:
                cost = self.inventory[code]['price'] * quantity
                self.order.append((code, self.inventory[code]['name'], quantity, cost))
                self.reset_stock[code] = self.reset_stock.get(code, 0) + quantity
                self.inventory[code]['stock'] -= quantity
                self.total += cost
                self.update_order_display()
                self.update_inventory_display()
            else:
                messagebox.showerror("Error", "Item code not found or insufficient stock")
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity")

    def update_order_display(self):
        self.order_listbox.delete(1.0, END)
        self.order_listbox.insert(END, f"{'Code':<10}{'Item':<30}{'Qty':<10}{'Cost':<10}\n")
        self.order_listbox.insert(END, "-" * 60 + "\n")
        for code, name, quantity, cost in self.order:
            self.order_listbox.insert(END, f"{code:<10}{name:<30}{quantity:<10}₱{cost:.2f}\n")
        self.order_listbox.insert(END, "-" * 60 + "\n")
        self.order_listbox.insert(END, f"{'Total:':<50}₱{self.total:.2f}\n")

    def finalize_order(self):
        if not self.order:
            messagebox.showerror("Error", "No items in order.")
            return

        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()

        c.execute('INSERT INTO Orders (total) VALUES (?)', (self.total,))
        order_id = c.lastrowid

        for code, item, quantity, cost in self.order:
            c.execute('INSERT INTO OrderItems (order_id, item_code, quantity, cost) VALUES (?, ?, ?, ?)', (order_id, code, quantity, cost))
            c.execute('UPDATE Inventory SET stock = stock - ? WHERE code = ?', (quantity, code))

        conn.commit()
        conn.close()

        messagebox.showinfo("Order Finalized", f"Order finalized. Total: ₱{self.total:.2f}")
        self.reset_order()

    def reset_order(self):
        self.order = []
        self.total = 0
        self.update_order_display()
        for code, quantity in self.reset_stock.items():
            self.inventory[code]['stock'] += quantity
        self.reset_stock.clear()
        self.update_inventory_display()

    def sign_out(self):
        self.destroy()
        LoginApp().mainloop()


class LoginApp(Tk):
    def __init__(self):
        super().__init__()

        self.title("Login - Arise Coffee PH")
        self.geometry("400x300")
        self.configure(bg="#f8f1e5")

        business_name_label = Label(self, text="Arise Coffee PH", font=("Arial", 24), bg="#f8f1e5")
        business_name_label.pack(pady=20)

        username_label = Label(self, text="Username:", font=("Arial", 14), bg="#f8f1e5")
        username_label.pack(pady=5)
        self.username_entry = Entry(self, font=("Arial", 14))
        self.username_entry.pack(pady=5)

        password_label = Label(self, text="Password:", font=("Arial", 14), bg="#f8f1e5")
        password_label.pack(pady=5)
        self.password_entry = Entry(self, show="*", font=("Arial", 14))
        self.password_entry.pack(pady=5)

        login_button = Button(self, text="Login", font=("Arial", 14), command=self.check_login, bg="#4caf50", fg="white")
        login_button.pack(pady=20)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "password":
            self.destroy()
            POSApplication().mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")


if __name__ == "__main__":
    LoginApp().mainloop()
