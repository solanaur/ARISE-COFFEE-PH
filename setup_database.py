import sqlite3

def setup_database():
   conn = sqlite3.connect('pos_database.db')
   c = conn.cursor()


   c.execute('''CREATE TABLE IF NOT EXISTS Inventory (
                   id INTEGER PRIMARY KEY,
                   code TEXT UNIQUE,
                   name TEXT,
                   price REAL,
                   stock INTEGER,
                   category TEXT
               )''')


   c.execute('''CREATE TABLE IF NOT EXISTS Orders (
                   id INTEGER PRIMARY KEY,
                   total REAL,
                   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
               )''')


   c.execute('''CREATE TABLE IF NOT EXISTS OrderItems (
                   id INTEGER PRIMARY KEY,
                   order_id INTEGER,
                   item_code TEXT,
                   quantity INTEGER,
                   cost REAL,
                   FOREIGN KEY(order_id) REFERENCES Orders(id),
                   FOREIGN KEY(item_code) REFERENCES Inventory(code)
               )''')


   inventory_items = [
       ('SIG', 'Signature Iced Coffee', 150, 50, 'Coffee'),
       ('MLT', 'Matcha Latte', 170, 40, 'Coffee'),
       ('BLT', 'Biscoff Latte', 160, 30, 'Coffee'),
       ('IAM', 'Iced Americano', 130, 20, 'Coffee'),
       ('CMT', 'Caramel Macchiato', 150, 25, 'Coffee'),
       ('CBW', 'Cold Brew', 110, 30, 'Coffee'),
       ('HOR', 'Horchata', 150, 40, 'Non-Coffee'),
       ('SMM', 'Strawberry Milkshake', 140, 25, 'Non-Coffee'),
       ('CHM', 'Chocolate Milkshake', 140, 25, 'Non-Coffee'),
       ('MGM', 'Mango Milkshake', 140, 20, 'Non-Coffee'),
       ('WMT', 'Wintermelon Milktea', 115, 30, 'Non-Coffee'),
       ('OKM', 'Okinawa Milktea', 115, 30, 'Non-Coffee'),
       ('CRF', 'Croffle', 95, 50, 'Pastry'),
       ('CRC', 'Regular Croissant', 80, 30, 'Pastry'),
       ('CCC', 'Chocolate Chip Cookie', 60, 40, 'Pastry'),
       ('MCC', 'Matcha Cookie', 70, 35, 'Pastry'),
       ('RVC', 'Red Velvet Crinkles', 30, 45, 'Pastry'),
       ('OGD', 'Original Glazed Donut', 65, 50, 'Pastry'),
       ('CGD', 'Chocolate Glazed Donut', 65, 50, 'Pastry')
   ]


   c.executemany('''INSERT OR IGNORE INTO Inventory (code, name, price, stock, category) VALUES (?, ?, ?, ?, ?)''',
                 inventory_items)


   conn.commit()
   conn.close()


setup_database()
