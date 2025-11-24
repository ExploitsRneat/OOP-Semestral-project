import sqlite3
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

DB_FILE = "realestate_simple.db"
DEFAULT_COMMISSION = 0.03  # 3%

# -------------------------
# Database helper (sqlite3)
# -------------------------
class DB:
    def __init__(self, path=DB_FILE):
        need_init = not os.path.exists(path)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()  # Always try to create tables for robustness

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                commission_rate REAL NOT NULL DEFAULT 0.03
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                prop_type TEXT NOT NULL,
                price REAL NOT NULL,
                extras TEXT,
                owner TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS commissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                property_id INTEGER,
                amount REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    # user methods (plaintext password)
    def create_user(self, username, password, commission_rate=DEFAULT_COMMISSION):
        # Username and password validations to safeguard against empty or short credentials
        if not username or not password or len(username.strip()) < 3 or len(password) < 4:
            return None # better to show a warning at UI level
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO users (username, password, commission_rate) VALUES (?, ?, ?)",
                      (username, password, commission_rate))
            self.conn.commit()
            return c.lastrowid
        except sqlite3.IntegrityError:
            return None

    def authenticate_user(self, username, password):
        if not username or not password:
            return None
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        row = c.fetchone()
        return dict(row) if row else None

    def get_user(self, user_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        r = c.fetchone()
        return dict(r) if r else None

    # property methods
    def add_property(self, name, prop_type, price, extras_text):
        if not name.strip() or not prop_type.strip():
            return None
        # Prevent properties with negative or zero price
        if price <= 0:
            return None
        c = self.conn.cursor()
        c.execute("INSERT INTO properties (name, prop_type, price, extras, owner) VALUES (?, ?, ?, ?, ?)",
                  (name, prop_type, price, extras_text, None))
        self.conn.commit()
        return c.lastrowid

    def list_properties(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM properties ORDER BY id")
        return [dict(r) for r in c.fetchall()]

    def get_property(self, prop_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM properties WHERE id=?", (prop_id,))
        r = c.fetchone()
        return dict(r) if r else None

    def sell_property(self, prop_id, buyer_name, agent_user):
        p = self.get_property(prop_id)
        if not p:
            return False, "Property not found."
        if not buyer_name or not buyer_name.strip():
            return False, "Buyer name is required."
        if p["owner"] and p["owner"].strip().lower() == buyer_name.strip().lower():
            return False, "Buyer already owner."
        if p["owner"]:
            return False, "Property already has an owner."
        c = self.conn.cursor()
        c.execute("UPDATE properties SET owner=? WHERE id=?", (buyer_name, prop_id))
        commission = float(p["price"]) * float(agent_user.get("commission_rate", DEFAULT_COMMISSION))
        if commission <= 0:
            commission = 0.0
        c.execute("INSERT INTO commissions (user_id, property_id, amount) VALUES (?, ?, ?)",
                  (agent_user["id"], prop_id, commission))
        self.conn.commit()
        return True, commission

    def total_commission_for_user(self, user_id):
        c = self.conn.cursor()
        c.execute("SELECT SUM(amount) as total FROM commissions WHERE user_id=?", (user_id,))
        r = c.fetchone()
        return float(r["total"] or 0.0)

# -------------------------
# GUI (tkinter)
# -------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.db = DB()
        self.current_user = None
        self.root.title("RealEstate Simple")
        self._login_screen()

    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # Login / Register
    def _login_screen(self):
        self._clear()
        frm = tk.Frame(self.root, padx=20, pady=20)
        frm.pack()

        tk.Label(frm, text="Login", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=(0,10))
        tk.Label(frm, text="Username").grid(row=1, column=0, sticky="e")
        e_user = tk.Entry(frm)
        e_user.grid(row=1, column=1)
        tk.Label(frm, text="Password").grid(row=2, column=0, sticky="e")
        e_pass = tk.Entry(frm, show="*")
        e_pass.grid(row=2, column=1)

        def do_login():
            u = e_user.get().strip()
            u.capitalize()
            p = e_pass.get().strip()
            p.capitalize()
            if not (u and p):
                messagebox.showwarning("Missing", "Enter both username and password.")
                return
            user = self.db.authenticate_user(u, p)
            if user:
                self.current_user = user
                messagebox.showinfo("Welcome", f"Hello {u}!")
                self._main_screen()
            else:
                messagebox.showerror("Failed", "Invalid credentials.")

        def go_register():
            self._register_screen()

        tk.Button(frm, text="Login", width=12, command=do_login).grid(row=3, column=0, pady=10)
        tk.Button(frm, text="Register", width=12, command=go_register).grid(row=3, column=1, pady=10)

    def _register_screen(self):
        self._clear()
        frm = tk.Frame(self.root, padx=20, pady=20)
        frm.pack()
        tk.Label(frm, text="Register", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=(0,10))
        tk.Label(frm, text="Username").grid(row=1, column=0, sticky="e")
        e_user = tk.Entry(frm)
        e_user.grid(row=1, column=1)
        tk.Label(frm, text="Password").grid(row=2, column=0, sticky="e")
        e_pass = tk.Entry(frm, show="*")
        e_pass.grid(row=2, column=1)
        tk.Label(frm, text="Commission (0.03 = 3%)").grid(row=3, column=0, sticky="e")
        e_comm = tk.Entry(frm)
        e_comm.insert(0, str(DEFAULT_COMMISSION))
        e_comm.grid(row=3, column=1)

        def do_create():
            u = e_user.get().strip()
            p = e_pass.get().strip()
            if not (u and p):
                messagebox.showwarning("Missing", "Enter username and password.")
                return
            if len(u) < 3 or len(p) < 4:
                messagebox.showwarning("Weak", "Username must be at least 3 chars, password at least 4.")
                return
            try:
                comm = float(e_comm.get().strip())
                if comm < 0 or comm > 1:
                    raise ValueError
            except:
                messagebox.showwarning("Invalid", "Commission must be a decimal between 0 and 1 (e.g. 0.03)")
                return
            uid = self.db.create_user(u, p, comm)
            if uid:
                messagebox.showinfo("Done", "Account created. Please login.")
                self._login_screen()
            else:
                messagebox.showerror("Exists", "Username already taken, or entry invalid.")

        tk.Button(frm, text="Create", width=12, command=do_create).grid(row=4, column=0, pady=10)
        tk.Button(frm, text="Back", width=12, command=self._login_screen).grid(row=4, column=1, pady=10)

    # Main
    def _main_screen(self):
        self._clear()
        top = tk.Frame(self.root, pady=6)
        top.pack(fill="x")
        tk.Label(top, text=f"Logged in as: {self.current_user['username']}", font=("Arial", 12)).pack(side="left", padx=8)
        tk.Button(top, text="Logout", command=self._logout).pack(side="right", padx=8)

        body = tk.Frame(self.root, padx=12, pady=12)
        body.pack(fill="both", expand=True)

        left = tk.Frame(body)
        left.pack(side="left", anchor="n", padx=(0,10))

        tk.Button(left, text="Add Property", width=18, command=self._add_property).pack(pady=4)
        tk.Button(left, text="View All Properties", width=18, command=self._view_properties).pack(pady=4)
        tk.Button(left, text="Sell Property", width=18, command=self._sell_property).pack(pady=4)
        tk.Button(left, text="My Earnings", width=18, command=self._show_earnings).pack(pady=4)

        right = tk.Frame(body)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="Properties:", font=("Arial", 12)).pack(anchor="w")
        self.tree = ttk.Treeview(right, columns=("type","price","owner"), show="headings", height=14)
        self.tree.heading("type", text="Type")
        self.tree.heading("price", text="Price")
        self.tree.heading("owner", text="Owner")
        self.tree.pack(fill="both", expand=True)
        self._refresh_tree()

    def _logout(self):
        self.current_user = None
        self._login_screen()

    # actions
    def _add_property(self):
        ptype = simpledialog.askstring("Type", "Enter type (house, car, land):", parent=self.root)
        if not ptype:
            return
        ptype = ptype.strip().capitalize()
        if ptype not in ("House","Car","Land"):
            messagebox.showwarning("Invalid", "Allowed: House, Car, Lzand")
            return
        name = simpledialog.askstring("Name", "Enter name/title:", parent=self.root)
        if not name or len(name.strip()) < 2:
            messagebox.showwarning("Invalid", "Property name must not be empty or too short.")
            return
        price_s = simpledialog.askstring("Price", "Enter price (number):", parent=self.root)
        try:
            price = float(price_s)
            if price <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Invalid", "Price must be a positive number.")
            return

        extras = []
        if ptype == "House":
            rooms = simpledialog.askstring("Rooms", "Number of rooms:", parent=self.root) or ""
            try:
                if rooms and int(rooms) < 1:
                    messagebox.showwarning("Invalid", "Rooms must be 1 or more.")
                    return
            except:
                if rooms: # filled but invalid
                    messagebox.showwarning("Invalid", "Number of rooms must be a positive integer.")
                    return
            garage = simpledialog.askstring("Garage", "Has garage? yes/no:", parent=self.root) or ""
            if garage.lower() not in ("yes", "no", ""):
                messagebox.showwarning("Invalid", "Garage must be 'yes', 'no' or left blank.")
                return
            extras.append(f"rooms={rooms}")
            extras.append(f"garage={garage}")
        elif ptype == "Car":
            brand = simpledialog.askstring("Brand", "Brand:", parent=self.root) or ""
            year = simpledialog.askstring("Year", "Model year:", parent=self.root) or ""
            if year and (len(year) != 4 or not year.isdigit()):
                messagebox.showwarning("Invalid", "Year must be a 4-digit number.")
                return
            extras.append(f"brand={brand}")
            extras.append(f"year={year}")
        elif ptype == "Land":
            size = simpledialog.askstring("Size", "Size (sqm):", parent=self.root) or ""
            try:
                if size and float(size) <= 0:
                    messagebox.showwarning("Invalid", "Size must be positive (sqm).")
                    return
            except:
                if size:
                    messagebox.showwarning("Invalid", "Size (sqm) must be numeric.")
                    return
            zoning = simpledialog.askstring("Zoning", "Zoning type:", parent=self.root) or ""
            extras.append(f"size={size}")
            extras.append(f"zoning={zoning}")

        extras_text = ";".join(extras)
        result = self.db.add_property(name, ptype, price, extras_text)
        if result is not None:
            messagebox.showinfo("Added", f"{ptype.title()} '{name}' added.")
            self._refresh_tree()
        else:
            messagebox.showerror("Error", "Failed to add property. Please check your entries.")

    def _view_properties(self):
        win = tk.Toplevel(self.root)
        win.title("All Properties")
        tree = ttk.Treeview(win, columns=("id","name","type","price","owner","extras"), show="headings")
        for col, title in [("id","ID"),("name","Name"),("type","Type"),("price","Price"),("owner","Owner"),("extras","Extras")]:
            tree.heading(col, text=title)
        tree.pack(fill="both", expand=True)
        for p in self.db.list_properties():
            tree.insert("", "end", values=(p["id"], p["name"], p["prop_type"], f"₱{p['price']:,.2f}", p["owner"] or "-", p["extras"] or "-"))
        tk.Button(win, text="Close", command=win.destroy).pack(pady=6)

    def _sell_property(self):
        props = self.db.list_properties()
        if not props:
            messagebox.showinfo("None", "No properties.")
            return
        # Only display properties not yet owned
        ids = [str(p["id"]) for p in props if not p["owner"]]
        if not ids:
            messagebox.showinfo("None", "All properties already sold.")
            return
        prop_id = simpledialog.askstring("Sell", f"Enter property ID to sell (available: {', '.join(ids)}):", parent=self.root)
        if not prop_id or prop_id not in ids:
            messagebox.showwarning("Invalid", "Provide a valid unsold ID.")
            return
        buyer = simpledialog.askstring("Buyer", "Enter buyer name:", parent=self.root)
        if not buyer or not buyer.strip():
            messagebox.showwarning("Invalid", "Buyer name can't be empty.")
            return
        ok, res = self.db.sell_property(int(prop_id), buyer, self.current_user)
        if ok:
            messagebox.showinfo("Sold", f"Sold. Commission earned: ₱{res:,.2f}")
            self._refresh_tree()
        else:
            messagebox.showerror("Error", res)

    def _show_earnings(self):
        total = self.db.total_commission_for_user(self.current_user["id"])
        messagebox.showinfo("Earnings", f"Total commissions: ₱{total:,.2f}")

    def _refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for p in self.db.list_properties():
            self.tree.insert("", "end", values=(p["prop_type"], f"₱{p['price']:,.2f}", p["owner"] or "-"))

# -------------------------
# Run app
# -------------------------
def main():
    root = tk.Tk()
    root.geometry("720x440")
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
