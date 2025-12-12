#Full CustomTkinter windows instead of tkinter dialogs

import customtkinter as ctk
from tkinter import messagebox

class RoleSelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Role")
        self.geometry("300x200")
        self.resizable(False, False)
        self.grab_set()
        self.choice = None

        ctk.CTkLabel(self, text="Continue as:", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        ctk.CTkButton(self, text="Buyer", command=lambda: self.finish("buyer"), width=200).pack(pady=10)
        ctk.CTkButton(self, text="Agent", command=lambda: self.finish("agent"), width=200).pack(pady=10)

    def finish(self, choice):
        self.choice = choice
        self.destroy()

    def ask(self):
        self.wait_window()
        return self.choice


class LoginWindow(ctk.CTkToplevel):
    def __init__(self, parent, title="Login"):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x300")
        self.resizable(False, False)
        self.grab_set()

        self.username = None
        self.password = None

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.pass_entry.pack(pady=10)

        ctk.CTkButton(self, text="Login", command=self._submit, width=200).pack(pady=15)

    def _submit(self):
        self.username = self.user_entry.get()
        self.password = self.pass_entry.get()
        self.destroy()

    def get(self):
        self.wait_window()
        return self.username, self.password


class RegisterWindow(ctk.CTkToplevel):
    def __init__(self, parent, title="Register Agent"):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x350")
        self.resizable(False, False)
        self.grab_set()

        self.username = None
        self.password = None

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Choose Username", width=250)
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Password (min 6)", show="*", width=250)
        self.pass_entry.pack(pady=10)

        self.conf_entry = ctk.CTkEntry(self, placeholder_text="Confirm Password", show="*", width=250)
        self.conf_entry.pack(pady=10)

        ctk.CTkButton(self, text="Create Account", command=self._submit, width=200).pack(pady=15)

    def _submit(self):
        u = self.user_entry.get()
        p = self.pass_entry.get()
        c = self.conf_entry.get()

        if not u or not p:
            messagebox.showerror("Error", "All fields required.")
            return
        if p != c:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        if len(p) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters.")
            return

        self.username = u
        self.password = p
        self.destroy()

    def get(self):
        self.wait_window()
        return self.username, self.password


class LoginRegisterHelper:
    def __init__(self, db_interface, parent):
        self.db = db_interface
        self.parent = parent

    def login_agent(self):
        win = LoginWindow(self.parent, title="Agent Login")
        username, password = win.get()
        if not username:
            return False

        user = self.db.login_user(username, password)
        if not user or user.get("role") != "agent":
            messagebox.showerror("Login Failed", "Invalid credentials or not an agent.")
            return False

        self.db.current_user = user
        messagebox.showinfo("Welcome", f"Welcome, {user.get('display_name') or user.get('username')}")
        return True

    def register_agent(self):
        win = RegisterWindow(self.parent)
        username, password = win.get()
        if not username:
            return False

        uid = self.db.create_user(username, password, role="agent", display_name=username)
        if not uid:
            messagebox.showerror("Register Failed", "Username already exists.")
            return False

        messagebox.showinfo("Success", "Account created. Please log in.")
        return True
