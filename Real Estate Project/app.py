# app.py
import os
import sys
import hashlib
import io

from gui_main import MainGUI
from auth import RoleSelectionDialog, LoginRegisterHelper

import pymysql
from pymysql.err import IntegrityError
import customtkinter as ctk
from tkinter import messagebox

# Edit these to match your XAMPP/MySQL settings
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "realestate_db",
    "port": 3306
}


class DBInterface:
    def __init__(self, config):
        self.config = config
        self.current_user = None
        os.makedirs(os.path.join(os.getcwd(), "images_temp"), exist_ok=True)
        self.create_tables_if_missing()

    def connect(self):
        return pymysql.connect(
            host=self.config.get("host", "localhost"),
            user=self.config.get("user", "root"),
            password=self.config.get("password", ""),
            database=self.config.get("database"),
            port=self.config.get("port", 3306),
            cursorclass=pymysql.cursors.Cursor,
            autocommit=False
        )

    def create_tables_if_missing(self):
        # Connect without database to ensure DB exists
        conn = pymysql.connect(
            host=self.config.get("host", "localhost"),
            user=self.config.get("user", "root"),
            password=self.config.get("password", ""),
            port=self.config.get("port", 3306),
            autocommit=True,
            cursorclass=pymysql.cursors.Cursor
        )
        cur = conn.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{self.config['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        cur.close()
        conn.close()

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
          id INT AUTO_INCREMENT PRIMARY KEY,
          username VARCHAR(80) NOT NULL UNIQUE,
          password_hash CHAR(64) NOT NULL,
          role ENUM('buyer','agent') NOT NULL,
          display_name VARCHAR(120),
          phone VARCHAR(40),
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        )
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS properties (
          id INT AUTO_INCREMENT PRIMARY KEY,
          title VARCHAR(255) NOT NULL,
          property_type VARCHAR(60),
          sell_method VARCHAR(60),
          payment_type VARCHAR(60),
          price VARCHAR(80),
          beds INT DEFAULT 0,
          baths DOUBLE DEFAULT 0,
          size_sqm VARCHAR(80),
          land_width VARCHAR(80) NOT NULL,
          address VARCHAR(255),
          city VARCHAR(120),
          description TEXT,
          image_blob LONGBLOB,
          image_mime VARCHAR(80),
          agent_id INT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (agent_id) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        )
        conn.commit()
        cur.close()
        conn.close()

    def hash_pwd(self, pw):
        return hashlib.sha256(pw.encode("utf-8")).hexdigest()

    def create_user(self, username, password, role="buyer", display_name=None):
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash, role, display_name) VALUES (%s,%s,%s,%s)",
                (username, self.hash_pwd(password), role, display_name or username),
            )
            conn.commit()
            uid = cur.lastrowid
        except IntegrityError:
            conn.rollback()
            uid = None
        finally:
            cur.close()
            conn.close()
        return uid

    def login_user(self, username, password):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash, role, display_name FROM users WHERE username=%s",
            (username,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return None
        if row[2] != self.hash_pwd(password):
            return None
        return {"id": row[0], "username": row[1], "role": row[3], "display_name": row[4]}

    def fetch_all_properties(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT p.id, p.title, p.property_type, p.sell_method, p.payment_type,
                   p.price, p.beds, p.baths, p.size_sqm, p.land_width, p.address, p.city, p.description, p.image_blob, p.image_mime,
                   u.id AS agent_id, u.username AS agent_username, u.display_name
            FROM properties p LEFT JOIN users u ON p.agent_id = u.id
            ORDER BY p.id DESC
        """
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        results = []
        for r in rows:
            results.append(
                {
                    "id": r[0],
                    "title": r[1],
                    "property_type": r[2],
                    "sell_method": r[3],
                    "payment_type": r[4],
                    "price": r[5],
                    "beds": r[6],
                    "baths": r[7],
                    "size_sqm": r[8],
                    "land_width": r[9],
                    "address": r[10],
                    "city": r[11],
                    "description": r[12],
                    "image_blob": r[13],
                    "image_mime": r[14],
                    "agent_id": r[15],
                    "agent_username": r[16],
                    "agent_name": r[17],
                }
            )
        return results

    def insert_property(self, prop):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO properties (title, property_type, sell_method, payment_type, price, beds, baths, size_sqm, land_width, address, city, description, image_blob, image_mime, agent_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
            (
                prop["title"],
                prop["property_type"],
                prop["sell_method"],
                prop["payment_type"],
                prop["price"],
                prop["beds"],
                prop["baths"],
                prop["size_sqm"],
                prop["land_width"],
                prop["address"],
                prop["city"],
                prop["description"],
                prop.get("image_blob", None),
                prop.get("image_mime", None),
                self.current_user.get("id") if self.current_user else None,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()

    def update_property(self, prop_id, prop):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE properties SET title=%s, property_type=%s, sell_method=%s, payment_type=%s, price=%s,
                                  beds=%s, baths=%s, size_sqm=%s, land_width=%s, address=%s, city=%s, description=%s, image_blob=%s, image_mime=%s
            WHERE id=%s
        """,
            (
                prop["title"],
                prop["property_type"],
                prop["sell_method"],
                prop["payment_type"],
                prop["price"],
                prop["beds"],
                prop["baths"],
                prop["size_sqm"],
                prop["land_width"],
                prop["address"],
                prop["city"],
                prop["description"],
                prop.get("image_blob", None),
                prop.get("image_mime", None),
                prop_id,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()

    def delete_property(self, prop_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM properties WHERE id=%s", (prop_id,))
        conn.commit()
        cur.close()
        conn.close()


def main():
    ctk.set_appearance_mode("dark")
    db = DBInterface(DB_CONFIG)
    # Launch GUI
    gui = MainGUI(db)
    auth = LoginRegisterHelper(db, gui)
    # Ask role (simple dialog)
    role = RoleSelectionDialog(gui).ask()
    if role == "Agent":
        ok = auth.login_agent()
        if not ok:
            if messagebox.askyesno("Register?", "Register a new agent account?"):
                if auth.register_agent():
                    auth.login_agent()
                else:
                    sys.exit(1)
            else:
                sys.exit(0)
        gui.action_frame.pack(pady=8)
        gui.agent_btn.configure(text=f"Agent Logout ({db.current_user.get('display_name')})")
    gui.refresh_list()
    gui.mainloop()


if __name__ == "__main__":
    main()
