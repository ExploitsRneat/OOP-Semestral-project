import customtkinter as ctk
import os
import pymysql
from auth import UnifiedLoginFrame
from gui_main import MainGUI

# Database configuration
DB_CONFIG = { 
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "realestate_db",
    "port": 3306,
}

class DBInterface:
    def __init__(self, config):
        self.config = config
        self.current_user = None
        os.makedirs("images_temp", exist_ok=True)
        self.create_tables_if_missing()

    def connect(self): #Database Connection
        return pymysql.connect(
            host=self.config["host"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            port=self.config["port"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    def create_tables_if_missing(self): #Create Tables if they do not exist
        conn = pymysql.connect(
            host=self.config["host"],
            user=self.config["user"],
            password=self.config["password"],
            port=self.config["port"],
            autocommit=True,
        )
        cur = conn.cursor() #Cursor Object
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{self.config['database']}`")
        cur.close()
        conn.close()

        conn = self.connect()
        cur = conn.cursor()

        # --------- USERS TABLE ----------
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE,
            password_hash CHAR(64),
            role ENUM('buyer','agent'),
            display_name VARCHAR(100),
            phone VARCHAR(40),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # --------- PROPERTIES TABLE ----------
        cur.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            property_type VARCHAR(80),
            sell_method VARCHAR(80),
            payment_type VARCHAR(80),
            price VARCHAR(80),
            beds INT,
            baths FLOAT,
            size_sqm VARCHAR(80),
            land_width VARCHAR(80),
            address TEXT,
            city VARCHAR(80),
            description TEXT,
            image_blob LONGBLOB,
            image_mime VARCHAR(40)
        )
        """)


        # --------- IGNORED PROPERTIES TABLE ---------- 
        # Stores properties that have been ignored(deleted) by the agent, basically an archive
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ignored_properties LIKE properties
        """)

        conn.commit()
        cur.close()
        conn.close()

    # ---------- USERS ----------
    # Create a new user
    def create_user(self, username, password, role, display_name="", phone=""):
        import hashlib
        pw = hashlib.sha256(password.encode()).hexdigest()

        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (username, password_hash, role, display_name, phone)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, pw, role, display_name, phone))
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    def login_user(self, username, password):
        import hashlib
        pw = hashlib.sha256(password.encode()).hexdigest()

        conn = self.connect()
        cur = conn.cursor()
        # Fetch user matching username and password hash
        cur.execute("""
            SELECT id, username, role, display_name, phone
            FROM users
            WHERE username=%s AND password_hash=%s
        """, (username, pw))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user

    # ---------- PROPERTIES ----------
    def fetch_all_properties(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM properties ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def fetch_ignored_properties(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM ignored_properties ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def insert_property(self, prop):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO properties
            (title, property_type, sell_method, payment_type, price, beds, baths,
             size_sqm, land_width, address, city, description, image_blob, image_mime)
            VALUES (%(title)s,%(property_type)s,%(sell_method)s,%(payment_type)s,
                    %(price)s,%(beds)s,%(baths)s,%(size_sqm)s,%(land_width)s,
                    %(address)s,%(city)s,%(description)s,%(image_blob)s,%(image_mime)s)
        """, prop)
        conn.commit()
        cur.close()
        conn.close()

    def ignore_property(self, pid):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO ignored_properties
            (id, title, property_type, sell_method, payment_type, price,
            beds, baths, size_sqm, land_width, address, city,
            description, image_blob, image_mime)
            SELECT
            id, title, property_type, sell_method, payment_type, price,
            beds, baths, size_sqm, land_width, address, city,
            description, image_blob, image_mime
            FROM properties
            WHERE id=%s
        """, (pid,))

        cur.execute("DELETE FROM properties WHERE id=%s", (pid,))
        conn.commit()
        cur.close()
        conn.close()
        return True

    def update_property(self, prop):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            UPDATE properties SET
            title=%s,
            property_type=%s,
            sell_method=%s,
            payment_type=%s,
            price=%s,
            beds=%s,
            baths=%s,
            size_sqm=%s,
            city=%s
            WHERE id=%s
        """, (
            prop["title"],
            prop["property_type"],
            prop["sell_method"],
            prop["payment_type"],
            prop["price"],
            prop["beds"],
            prop["baths"],
            prop["size_sqm"],
            prop["city"],
            prop["id"]
        ))
        conn.commit()
        cur.close()
        conn.close()


    def restore_property(self, pid):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO properties
            (id, title, property_type, sell_method, payment_type, price,
            beds, baths, size_sqm, land_width, address, city,
            description, image_blob, image_mime)
            SELECT
            id, title, property_type, sell_method, payment_type, price,
            beds, baths, size_sqm, land_width, address, city,
            description, image_blob, image_mime
            FROM ignored_properties
            WHERE id=%s
        """, (pid,))

        cur.execute("DELETE FROM ignored_properties WHERE id=%s", (pid,))
        conn.commit()
        cur.close()
        conn.close()
        return True

    def delete_ignored_property(self, pid):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM ignored_properties WHERE id=%s", (pid,))
        conn.commit()
        cur.close()
        conn.close()
        return True


def main(): # Main application entry point
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title("Real Estate Portal")
    root.geometry("700x500")

    db = DBInterface(DB_CONFIG)

    def clear_root(root):
        for widget in root.winfo_children():
            widget.destroy()

    def on_login_success(user):
        clear_root(root)
        root.main_gui = MainGUI(root, db)
        root.main_gui.apply_user(user)
            
    root.on_login_success = on_login_success
    
    login = UnifiedLoginFrame(root, db, on_login_success)
    login.pack(fill="both", expand=True)

    root.mainloop()

main() #Activates the application
