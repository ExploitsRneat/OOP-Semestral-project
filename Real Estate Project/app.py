import customtkinter as ctk
import os
import pymysql
from auth import LoginFrame, UnifiedLoginFrame
from gui_main import MainGUI

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

    def connect(self):
        return pymysql.connect(
            host=self.config["host"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            port=self.config["port"],
            cursorclass=pymysql.cursors.DictCursor,  # ← THIS LINE FIXES IT
            autocommit=False,
        )

    def create_tables_if_missing(self):
        conn = pymysql.connect(
            host=self.config["host"],
            user=self.config["user"],
            password=self.config["password"],
            port=self.config["port"],
            autocommit=True,
        )
        cur = conn.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{self.config['database']}`"
        )
        cur.close()
        conn.close()

        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE,
            password_hash CHAR(64),
            role ENUM('buyer','agent'),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        cur.close()
        conn.close()

    def create_user(self, username, password, role):
        import hashlib
        pw = hashlib.sha256(password.encode()).hexdigest()
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s,%s,%s)",
                (username, pw, role),
            )
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
        cur.execute(
            "SELECT id, role FROM users WHERE username=%s AND password_hash=%s",
            (username, pw),
        )
        row = cur.fetchone()  # now returns a DICT
        cur.close()
        conn.close()
        return row
    
    def fetch_all_properties(self):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                title,
                property_type,
                sell_method,
                payment_type,
                price,
                beds,
                baths,
                size_sqm,
                land_width,
                address,
                city,
                description,
                image_blob,
                image_mime
            FROM properties
            ORDER BY id DESC
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    
def main():
    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.title("Real Estate Portal")
    root.geometry("1200x800")

    db = DBInterface(DB_CONFIG)

    def on_login_success(user):
        db.current_user = user
        login.destroy()
        MainGUI(root, db)


    login = UnifiedLoginFrame(root, db, on_login_success)
    login.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
