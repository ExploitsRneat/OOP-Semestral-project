import customtkinter as ctk
from tkinter import messagebox


# =========================================================
# FULL LOGIN + REGISTER FRAME
# =========================================================
class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, db, on_login_success, role="buyer"):
        super().__init__(master)
        self.db = db
        self.on_login_success = on_login_success
        self.role = role

        self.pack(fill="both", expand=True)
        self.build_ui()

    # ---------------- UI ---------------- #

    def build_ui(self):
        self.columnconfigure(0, weight=1)

        title = "Buyer Login" if self.role == "buyer" else "Agent Login"
        ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 24, "bold")
        ).pack(pady=40)

        self.username = ctk.CTkEntry(self, placeholder_text="Username", width=300)
        self.username.pack(pady=10)

        self.password = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*",
            width=300
        )
        self.password.pack(pady=10)

        # Red field text
        self.login_error = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            font=("Segoe UI", 12)
        )
        self.login_error.pack(pady=(5, 0))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Login",
            width=140,
            command=self.login
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Register",
            width=140,
            command=self.open_register_dialog
        ).grid(row=0, column=1, padx=10)


        switch_text = (
            "Switch to Agent Login"
            if self.role == "buyer"
            else "Switch to Buyer Login"
        )
        ctk.CTkButton(
            self,
            text=switch_text,
            fg_color="transparent",
            text_color="#4ea1ff",
            hover=False,
            command=self.switch_role
        ).pack(pady=10)

    # ---------------- LOGIN ---------------- #

    def login(self):
        self.login_error.configure(text="")

        if not self.username.get() or not self.password.get():
            self.login_error.configure(text="All fields are required")
            return

        user = self.db.login_user(
            self.username.get().strip(),
            self.password.get().strip()
        )

        if not user:
            self.login_error.configure(text="Invalid username or password")
            return

        if user["role"] != self.role:
            self.login_error.configure(text=f"This account is not a {self.role}")
            return

        # Database user
        self.db.current_user = user
        self.destroy()
        self.on_login_success(user)

    # ---------------- REGISTER ---------------- #

    def open_register_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Register Account")
        win.geometry("420x520")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text=f"Register as {self.role.capitalize()}",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=20)

        username = ctk.CTkEntry(win, placeholder_text="Username", width=300)
        username.pack(pady=8)

        password = ctk.CTkEntry(win, placeholder_text="Password", show="*", width=300)
        password.pack(pady=8)

        confirm = ctk.CTkEntry(win, placeholder_text="Confirm Password", show="*", width=300)
        confirm.pack(pady=8)

        display_name = ctk.CTkEntry(win, placeholder_text="Display Name (optional)", width=300)
        display_name.pack(pady=8)

        phone = ctk.CTkEntry(win, placeholder_text="Phone (optional)", width=300)
        phone.pack(pady=8)

        register_error = ctk.CTkLabel(win, text="", text_color="red")
        register_error.pack(pady=5)

        def submit():
            register_error.configure(text="")

            if not username.get() or not password.get() or not confirm.get():
                register_error.configure(text="All fields are required")
                return

            if password.get() != confirm.get():
                register_error.configure(text="Passwords do not match")
                return

            user_id = self.db.create_user(
                username=username.get().strip(),
                password=password.get().strip(),
                role=self.role,
                display_name=display_name.get().strip(),
                phone=phone.get().strip()
            )

            if not user_id:
                register_error.configure(text="Username already exists")
                return

            messagebox.showinfo("Success", "Account created successfully")
            win.destroy()

        ctk.CTkButton(win, text="Register", width=200, command=submit).pack(pady=20)

    # ---------------- SWITCH ROLE ---------------- #

    def switch_role(self):
        self.destroy()
        new_role = "agent" if self.role == "buyer" else "buyer"
        LoginFrame(self.master, self.db, self.on_login_success, new_role)


# =========================================================
# INLINE AGENT LOGIN HELPER (USED BY gui_main.py)
# =========================================================
class LoginRegisterHelper:
    def __init__(self, db, parent):
        self.db = db
        self.parent = parent

    def login_agent(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Agent Login")
        win.geometry("360x320")
        win.grab_set()

        ctk.CTkLabel(win, text="Agent Login", font=("Segoe UI", 20, "bold")).pack(pady=20)

        username = ctk.CTkEntry(win, placeholder_text="Username", width=260)
        username.pack(pady=8)

        password = ctk.CTkEntry(win, placeholder_text="Password", show="*", width=260)
        password.pack(pady=8)

        error = ctk.CTkLabel(win, text="", text_color="red")
        error.pack(pady=5)

        def submit():
            user = self.db.login_user(username.get().strip(), password.get().strip())

            if not user:
                error.configure(text="Invalid credentials")
                return

            if user["role"] != "agent":
                error.configure(text="Not an agent account")
                return

            self.db.current_user = user
            win.destroy()

        ctk.CTkButton(win, text="Login", width=200, command=submit).pack(pady=20)

        win.wait_window()
        return self.db.current_user is not None


# =========================================================
# Unified Login Frame (NEW - keeps LoginFrame for compatibility)
# =========================================================
class UnifiedLoginFrame(ctk.CTkFrame):
    """Single login screen for both buyers and agents.

    Shows a red status label underneath the password field (space reserved).
    Register button creates buyers by default. Special admin credentials
    open an admin agent registration placeholder and do NOT log in admin.
    """
    def __init__(self, master, db, on_login_success):
        super().__init__(master)
        self.db = db
        self.on_login_success = on_login_success

        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Login", font=("Segoe UI", 24, "bold")).pack(pady=24)

        self.username = ctk.CTkEntry(self, placeholder_text="Username", width=300)
        self.username.pack(pady=8)

        self.password = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=300)
        self.password.pack(pady=8)

        # Red status/error text (space reserved)
        self.status = ctk.CTkLabel(self, text="", text_color="red", font=("Segoe UI", 12))
        self.status.pack(pady=(5, 0))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=16)

        ctk.CTkButton(btn_frame, text="Login", width=140, command=self.login).grid(row=0, column=0, padx=8)
        ctk.CTkButton(btn_frame, text="Register", width=140, command=self.open_register_dialog).grid(row=0, column=1, padx=8)

    def login(self):
        # Clear status
        self.status.configure(text="")

        if not self.username.get() or not self.password.get():
            self.status.configure(text="All fields are required")
            return

        user = self.db.login_user(self.username.get().strip(), self.password.get().strip())

        if not user:
            self.status.configure(text="Invalid username or password")
            return

        # Success: set current user and call callback
        self.db.current_user = user
        self.status.configure(text="")
        # If this frame is in a Toplevel, destroy the Toplevel parent
        try:
            parent = self.winfo_toplevel()
            if parent and isinstance(parent, ctk.CTkToplevel):
                parent.destroy()
        except Exception:
            pass

        self.on_login_success(user)

    def open_register_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Register Account")
        win.geometry("420x320")
        win.grab_set()

        ctk.CTkLabel(win, text="Register", font=("Segoe UI", 20, "bold")).pack(pady=14)

        username = ctk.CTkEntry(win, placeholder_text="Username", width=300)
        username.pack(pady=8)

        password = ctk.CTkEntry(win, placeholder_text="Password", show="*", width=300)
        password.pack(pady=8)

        confirm = ctk.CTkEntry(win, placeholder_text="Confirm Password", show="*", width=300)
        confirm.pack(pady=8)

        register_error = ctk.CTkLabel(win, text="", text_color="red")
        register_error.pack(pady=5)

        def submit():
            register_error.configure(text="")

            if not username.get() or not password.get() or not confirm.get():
                register_error.configure(text="All fields are required")
                return

            if password.get() != confirm.get():
                register_error.configure(text="Passwords do not match")
                return

            # Admin gate: special credentials open admin agent registration placeholder
            if username.get().strip() == "Admin" and password.get().strip() == "root_password":
                win.destroy()
                admin_win = ctk.CTkToplevel(self)
                admin_win.title("Admin Agent Registration")
                admin_win.geometry("420x240")
                ctk.CTkLabel(admin_win, text="Admin Agent Registration window (not implemented)", wraplength=380).pack(pady=40)
                return

            # Default: register as buyer
            created = self.db.create_user(username.get().strip(), password.get().strip(), "buyer")
            if not created:
                register_error.configure(text="Username already exists")
                return

            messagebox.showinfo("Success", "Account created successfully")
            win.destroy()

        ctk.CTkButton(win, text="Register", width=200, command=submit).pack(pady=16)
