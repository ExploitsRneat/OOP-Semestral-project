import customtkinter as ctk
from tkinter import messagebox

AGENT_REGISTRATION_KEY = "AGENT-ACCESS-2025"


# Unified Login Frame
class UnifiedLoginFrame(ctk.CTkFrame):
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

        # 🔴 Red status text
        self.status = ctk.CTkLabel(self, text="", text_color="red", font=("Segoe UI", 12))
        self.status.pack(pady=(5, 0))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=16)

        ctk.CTkButton(btn_frame, text="Login", width=140, command=self.login).grid(row=0, column=0, padx=8)
        ctk.CTkButton(btn_frame, text="Register", width=140, command=self.open_register_dialog).grid(row=0, column=1, padx=8)

    # ---------------- LOGIN ---------------- #
    def login(self):
        self.status.configure(text="")

        u = self.username.get().strip()
        p = self.password.get().strip()

        if not u or not p:
            self.status.configure(text="All fields are required")
            return

        # Attempt login
        user = self.db.login_user(u, p)
        if not user:
            self.status.configure(text="Invalid username or password")
            return

        self.db.current_user = user

        # Close parent toplevel if exists
        try:
            parent = self.winfo_toplevel()
            if isinstance(parent, ctk.CTkToplevel):
                parent.destroy()
        except Exception:
            pass

        self.on_login_success(user)

    # ---------------- REGISTER ---------------- #
    def open_register_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Register Account")
        win.geometry("700x500")
        win.grab_set()

        ctk.CTkLabel(win, text="Register", font=("Segoe UI", 20, "bold")).pack(pady=14)

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
        register_error.pack(pady=6)

        role_holder = {"role": "buyer"}

        def authorize_agent():
            auth = ctk.CTkToplevel(win)
            auth.title("Agent Registration")
            auth.geometry("360x220")
            auth.grab_set()

            ctk.CTkLabel(
                auth,
                text="Agent Registration",
                font=("Segoe UI", 18, "bold")
            ).pack(pady=14)

            ctk.CTkLabel(
                auth,
                text="Enter Registration Key"
            ).pack(pady=(6, 2))

            key_entry = ctk.CTkEntry(
                auth,
                placeholder_text="Registration Key",
                show="*",
                width=260
            )
            key_entry.pack(pady=6)

            auth_error = ctk.CTkLabel(auth, text="", text_color="red")
            auth_error.pack(pady=6)

            def confirm_key():
                auth_error.configure(text="Checking if the key is correct...")

                auth.update_idletasks()

                entered_key = key_entry.get().strip()

                if entered_key != AGENT_REGISTRATION_KEY:
                    auth_error.configure(text="Registration failed")
                    auth.after(1200, auth.destroy)
                    return

                # Key is correct → create agent immediately
                created = self.db.create_user(
                    username=username.get().strip(),
                    password=password.get().strip(),
                    role="agent",
                    display_name=display_name.get().strip(),
                    phone=phone.get().strip()
                )

                if created:
                    auth_error.configure(text="Agent account created")
                    auth.after(1200, lambda: (auth.destroy(), win.destroy()))
                else:
                    auth_error.configure(text="Registration failed")
                    auth.after(1200, auth.destroy)

            ctk.CTkButton(
                auth,
                text="Register Agent",
                width=180,
                command=confirm_key
            ).pack(pady=10)

        def submit():
            if role_holder["role"] == "agent":
                return

            register_error.configure(text="")

            u = username.get().strip()
            p = password.get().strip()
            c = confirm.get().strip()

            if not u or not p or not c:
                register_error.configure(text="All fields are required")
                return

            if p != c:
                register_error.configure(text="Passwords do not match")
                return

            created = self.db.create_user(
                username=u,
                password=p,
                role=role_holder["role"],
                display_name=display_name.get().strip(),
                phone=phone.get().strip(),
            )

            if not created:
                register_error.configure(text="Username already exists")
                return

            messagebox.showinfo(
                "Success",
                "Agent account created" if role_holder["role"] == "agent" else "Buyer account created",
            )
            win.destroy()

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Register Buyer", width=140, command=submit).grid(row=0, column=0, padx=6)
        ctk.CTkButton(btn_frame, text="Register as Agent", width=140, command=authorize_agent).grid(row=0, column=1, padx=6)
