import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
import io


class MainGUI(ctk.CTkFrame):
    def __init__(self, master, db_interface):
        super().__init__(master, fg_color="#0F172A")
        self.db = db_interface
        self.current_mode = "buyer"
        self.view_mode = "active"  # active | ignored
        self.selected_property = None

        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):
        # ===================== TOP BAR =====================
        top = ctk.CTkFrame(self, fg_color="#0b1220")
        top.pack(side="top", fill="x")

        title_frame = ctk.CTkFrame(top, fg_color="transparent")
        title_frame.pack(side="left", padx=6)

        ctk.CTkLabel(
            title_frame,
            text="Welcome!",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w")

        # Display name label 
        self.user_label = ctk.CTkLabel(
            title_frame,
            text="Browsing as Buyer",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8"
        )
        self.user_label.pack(anchor="w")

        self.switch_btn = ctk.CTkButton(
            top, text="Logout", command=self.on_switch_role
        )
        self.switch_btn.pack(side="right", padx=8, pady=8)

        # ===================== CONTENT =====================
        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=12, pady=12)

        # ===================== LEFT PANEL =====================
        left = ctk.CTkFrame(content, width=360, fg_color="#0F172A")
        left.pack(side="left", fill="y", padx=(0, 12))

        self.list_frame = ctk.CTkScrollableFrame(left, width=340)
        self.list_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.card_widgets = []

        # Bottom-left (agent only)
        self.bottom_left = ctk.CTkFrame(left, fg_color="transparent")
        self.bottom_left.pack(fill="x", padx=6, pady=(0, 6))
        self.bottom_left.pack_forget()

        # Swapping Ignored/Active Properties Button(agent only)
        self.ignored_btn = ctk.CTkButton(
            self.bottom_left,
            text="Ignored Properties",
            command=self.toggle_property_view
        )
            
        self.ignored_btn.pack(fill="x")

        # ===================== RIGHT PANEL =====================
        right = ctk.CTkFrame(content, fg_color="#0F172A")
        right.pack(side="left", fill="both", expand=True)
        
        self.details_panel = ctk.CTkFrame(right, fg_color="transparent")
        self.details_panel.pack(fill="both", expand=True)

        self.details_image = ctk.CTkLabel(
            self.details_panel, text="No Image", width=480, height=300
        )
        self.details_image.pack(pady=12)

        self.details_title = ctk.CTkLabel(
            self.details_panel,
            text="Select a property from the list.",
            font=ctk.CTkFont(size=16),
            wraplength=480
        )
        self.details_title.pack(pady=6)

        # ===================== DETAILS INFO =====================        
        self.details_info = ctk.CTkLabel(
            self.details_panel,
            text="",
            justify="left",
            anchor="nw",
            wraplength=480
        )
        self.details_info.pack(pady=10)

        # ===================== CONTACT AGENT BUTTON =====================
        self.contact_btn = ctk.CTkButton(
            right,
            text="📞 Interested? Contact the Agent", # Buyer only
            command=self.open_interest_window,
            width=240
        )
        self.contact_btn.pack(pady=10)
        self.contact_btn.pack_forget()

        # ===================== AGENT ACTIONS =====================
        self.ignore_btn = ctk.CTkButton(
            self.details_panel,
            text="Ignore Property",
            width=200,
            command=self.ignore_selected_property
        )
        self.ignore_btn.pack(pady=10)
        self.ignore_btn.pack_forget()

        self.ignored_action_frame = ctk.CTkFrame(
            self.details_panel, fg_color="transparent"
        )
        self.ignored_action_frame.pack(pady=12)
        self.ignored_action_frame.pack_forget()

        self.restore_btn = ctk.CTkButton(
            self.ignored_action_frame,
            text="Restore",
            width=120,
            command=self.restore_selected_property
        )
        self.restore_btn.grid(row=0, column=0, padx=8)

        self.delete_btn = ctk.CTkButton(
            self.ignored_action_frame,
            text="Delete",
            fg_color="#B22222",
            hover_color="#8B0000",
            width=120,
            command=self.delete_selected_property
        )
        self.delete_btn.grid(row=0, column=1, padx=8)

        self.action_frame = ctk.CTkFrame(self.bottom_left)
        self.add_btn = ctk.CTkButton(
            self.action_frame,
            text="➕ Add New Property",
            command=self.on_add_property
        )
        self.add_btn.pack(side="left", padx=4)
        self.action_frame.pack_forget()

        self.edit_btn = ctk.CTkButton(
            self.action_frame,
            text="✏ Edit Property",
            command=self.on_edit_property
        )
        self.edit_btn.pack(side="left", padx=4)


        self.refresh_list()

    # ===================== PROPERTY LIST =====================
    def refresh_list(self):
        props = (
            self.db.fetch_ignored_properties()
            if self.view_mode == "ignored"
            else self.db.fetch_all_properties()
        )

        for w in self.card_widgets:
            w.destroy()
        self.card_widgets.clear()

        for p in props:
            frame = ctk.CTkFrame(
                self.list_frame, fg_color="#111827", corner_radius=8
            )
            frame.pack(fill="x", pady=6, padx=6)

            thumb = ctk.CTkLabel(frame, text="")
            thumb.grid(row=0, column=0, rowspan=2, padx=6, pady=6)

            title = ctk.CTkLabel(
                frame,
                text=p.get("title", ""),
                anchor="w",
                font=ctk.CTkFont(size=13, weight="bold")
            )
            title.grid(row=0, column=1, sticky="w", padx=6, pady=4)

            info = f"{p.get('beds',0)} Beds | {p.get('baths',0)} Baths | {p.get('property_type','')}"
            ctk.CTkLabel(
                frame, text=info, anchor="w", text_color="#A3A3A3"
            ).grid(row=1, column=1, sticky="w", padx=6, pady=2)

            blob = p.get("image_blob")
            if blob:
                try:
                    im = Image.open(io.BytesIO(blob)).convert("RGB")
                    im.thumbnail((120, 80))
                    photo = ImageTk.PhotoImage(im)
                    thumb.configure(image=photo)
                    thumb.image = photo
                except:
                    thumb.configure(text=p.get("title", "")[:2].upper())
            else:
                thumb.configure(text=p.get("title", "")[:2].upper())

            frame.bind("<Button-1>", lambda e, x=p: self.on_card_click(x))
            for child in frame.winfo_children():
                child.bind("<Button-1>", lambda e, x=p: self.on_card_click(x))

            self.card_widgets.append(frame)

    # ===================== CARD CLICK =====================
    def on_card_click(self, prop):
        self.selected_property = prop
        self.details_title.configure(text=prop.get("title", ""))

        blob = prop.get("image_blob")
        if blob:
            try:
                im = Image.open(io.BytesIO(blob)).convert("RGB")
                im.thumbnail((480, 300))
                photo = ImageTk.PhotoImage(im)
                self.details_image.configure(image=photo, text="")
                self.details_image.image = photo
            except:
                self.details_image.configure(text="No Image")
        else:
            self.details_image.configure(text="No Image")

        info_text = f"""
🏷 Property Type: {prop.get('property_type','')}
📌 Sell Method: {prop.get('sell_method','')}
💳 Payment Type: {prop.get('payment_type','')}

💰 Price: ₱ {prop.get('price','')}

🛏 Beds: {prop.get('beds',0)}
🛁 Baths: {prop.get('baths',0)}

📐 Size: {prop.get('size_sqm','')} sqm
📏 Land Width: {prop.get('land_width','')} sqm

📍 Address: {prop.get('address','')}
🌆 City: {prop.get('city','')}

📝 Description:
{prop.get('description','')}
        """.strip()

        self.details_info.configure(text=info_text)

        if self.current_mode == "agent":
            if self.view_mode == "active":
                self.ignore_btn.pack(pady=10)
                self.ignored_action_frame.pack_forget()
            else:
                self.ignore_btn.pack_forget()
                self.ignored_action_frame.pack(pady=12)
        else:
            self.ignore_btn.pack_forget()
            self.ignored_action_frame.pack_forget()
        
        if self.current_mode == "buyer":
            self.contact_btn.pack(pady=10)
        else:
            self.contact_btn.pack_forget()


    # ===================== ROLE SWITCH =====================
    def on_switch_role(self):
        # Clear session
        self.db.current_user = None

        # Destroy MainGUI cleanly
        self.destroy()

        # Show login again IN THE SAME WINDOW
        from auth import UnifiedLoginFrame
        login = UnifiedLoginFrame(
            self.master,
            self.db,
            self.master.on_login_success
        )
        login.pack(fill="both", expand=True)

        win = ctk.CTkToplevel(self)
        win.title("Login")
        win.geometry("420x240")
        win.grab_set()

        def on_login(user):
            self.db.current_user = user
            self.current_mode = user.get("role", "buyer")
            self.switch_btn.configure(text="Logout")

            display = user.get("display_name") or user.get("username")
            role = user.get("role", "buyer").capitalize()
            self.user_label.configure(text=f"{role}: {display}")


            if self.current_mode == "agent":
                self.action_frame.pack(pady=8)
                self.bottom_left.pack(fill="x", padx=6, pady=(0, 6))
            else:
                self.action_frame.pack_forget()
                self.bottom_left.pack_forget()
                self.refresh_list()


            UnifiedLoginFrame(win, self.db, on_login)
            win.wait_window()
            return

        self.current_mode = "buyer"
        self.switch_btn.configure(text="Login")
        self.action_frame.pack_forget()
        self.bottom_left.pack_forget()
        messagebox.showinfo("Logout", "Buyer mode enabled.")

    def apply_user(self, user):
        self.view_mode = "active"
        self.ignored_btn.configure(text="Ignored Properties")

        self.db.current_user = user
        self.current_mode = user.get("role", "buyer")

        display = user.get("display_name") or user.get("username")
        role = user.get("role", "buyer").capitalize()

        self.user_label.configure(text=f"{role}: {display}")

        # Agent-only UI
        if self.current_mode == "agent":
            self.bottom_left.pack(fill="x", padx=6, pady=(0, 6))
            self.action_frame.pack(pady=6)
        else:
            self.bottom_left.pack_forget()
            self.action_frame.pack_forget()

        self.refresh_list()

    # Buyer only    
    def open_interest_window(self):
        if not self.selected_property:
            messagebox.showwarning("No Property", "Select a property first.")
            return

        # fetch agent (for now: first agent)
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT display_name, phone, username
            FROM users
            WHERE role='agent'
            LIMIT 1
        """)
        agent = cur.fetchone()
        cur.close()
        conn.close()

        if not agent:
            messagebox.showerror("Unavailable", "No agent available.")
            return

        win = ctk.CTkToplevel(self)
        win.title("Contact Agent")
        win.geometry("420x420")
        win.grab_set()

        # ---- Agent Info ----
        ctk.CTkLabel(win, text="Agent Information", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        ctk.CTkLabel(win, text=f"👤 Name: {agent.get('display_name') or 'N/A'}").pack(anchor="w", padx=20)
        ctk.CTkLabel(win, text=f"📧 Email: {agent.get('username')}").pack(anchor="w", padx=20)
        ctk.CTkLabel(win, text=f"📞 Phone: {agent.get('phone') or 'N/A'}").pack(anchor="w", padx=20)

        # ---- Payment Method ----
        ctk.CTkLabel(win, text="Payment Method", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 8))

        payment = ctk.StringVar(value="Full Payment")

        for option in ["Full Payment", "Installment", "Bank Loan"]:
            ctk.CTkRadioButton(
                win,
                text=option,
                variable=payment,
                value=option
            ).pack(anchor="w", padx=30, pady=4)

        def confirm():
            messagebox.showinfo(
                "Interest Sent",
                f"Your interest was sent!\n\nPayment Method: {payment.get()}\n\nAgent will contact you soon."
            )
            win.destroy()

        ctk.CTkButton(win, text="Confirm Interest", command=confirm).pack(pady=25)


    # ===================== AGENT ACTIONS =====================
    def ignore_selected_property(self):
        if not self.selected_property:
            messagebox.showwarning("No Selection", "Select a property first.")
            return

        pid = self.selected_property.get("id")
        if not pid:
            messagebox.showerror("Error", "Property has no ID.")
            return

        if not messagebox.askyesno("Ignore Property", "Move to ignored?"):
            return

        if self.db.ignore_property(pid):
            self.selected_property = None
            self.refresh_list()
            self.details_title.configure(text="Select a property from the list.")
            self.details_info.configure(text="")
            self.details_image.configure(image="", text="No Image")
    


    def toggle_property_view(self): # Toggle between active and ignored properties(agent only)
        if self.view_mode == "active":
            self.view_mode = "ignored"
            self.ignored_btn.configure(text="Active Properties")
            self.refresh_list()
        else:
            self.view_mode = "active"
            self.ignored_btn.configure(text="Ignored Properties")
            self.refresh_list()

    def restore_selected_property(self):
        if not self.selected_property:
            return
        self.db.restore_property(self.selected_property["id"])
        self.show_ignored_properties()

    def delete_selected_property(self):
        if not self.selected_property:
            return
        self.db.delete_ignored_property(self.selected_property["id"])
        self.show_ignored_properties()

    def show_ignored_properties(self):
        self.view_mode = "ignored"
        self.refresh_list()

    def on_edit_property(self):
        if not self.selected_property:
            messagebox.showwarning("No Selection", "Select a property first.")
            return

        p = self.selected_property

        title = simpledialog.askstring("Edit Title", "Property title:", initialvalue=p["title"])
        if not title:
            return

        price = simpledialog.askstring("Edit Price", "Price:", initialvalue=p["price"])
        beds = simpledialog.askinteger("Edit Beds", "Beds:", initialvalue=p["beds"])
        baths = simpledialog.askfloat("Edit Baths", "Baths:", initialvalue=p["baths"])

        self.db.update_property(
            p["id"],
            title=title,
            price=price,
            beds=beds,
            baths=baths
        )

        self.refresh_list()
        messagebox.showinfo("Updated", "Property updated successfully.")


    def on_add_property(self): # Agent only access guard
        if self.current_mode != "agent":
            messagebox.showerror("Access Denied", "Only agents can add properties.")
            return

        win = ctk.CTkToplevel(self)
        win.title("Add New Property")
        win.geometry("500x650")
        win.grab_set()

        entries = {}

        def add_field(label, row):
            ctk.CTkLabel(win, text=label).grid(row=row, column=0, sticky="w", padx=12, pady=6)
            e = ctk.CTkEntry(win, width=280)
            e.grid(row=row, column=1, padx=12, pady=6)
            entries[label] = e

        # ---------- TEXT FIELDS ----------
        add_field("Title", 0)
        add_field("Price", 1)
        add_field("Beds", 2)
        add_field("Baths", 3)
        add_field("Size (sqm)", 4)
        add_field("Land Width", 5)
        add_field("Address", 6)
        add_field("City", 7)

        # ---------- DROPDOWNS ----------
        ctk.CTkLabel(win, text="Property Type").grid(row=8, column=0, sticky="w", padx=12)
        property_type = ctk.CTkOptionMenu(
            win, values=["Condominium", "House", "Apartment", "Empty Lot"]
        )
        property_type.grid(row=8, column=1, padx=12)

        ctk.CTkLabel(win, text="Sell Method").grid(row=9, column=0, sticky="w", padx=12)
        sell_method = ctk.CTkOptionMenu(
            win, values=["For Sale", "For Lease"]
        )
        sell_method.grid(row=9, column=1, padx=12)

        ctk.CTkLabel(win, text="Payment Type").grid(row=10, column=0, sticky="w", padx=12)
        payment_type = ctk.CTkOptionMenu(
            win, values=["Cash", "Loan", "Installment"]
        )
        payment_type.grid(row=10, column=1, padx=12)

        # ---------- DESCRIPTION ----------
        ctk.CTkLabel(win, text="Description").grid(row=11, column=0, sticky="nw", padx=12)
        desc = ctk.CTkTextbox(win, width=280, height=100)
        desc.grid(row=11, column=1, padx=12, pady=6)

        # ---------- IMAGE ----------
        image_blob = {"data": None}

        def choose_image():
            file = filedialog.askopenfilename(
                filetypes=[("Images", "*.png;*.jpg;*.jpeg")]
            )
            if file:
                with open(file, "rb") as f:
                    image_blob["data"] = f.read()
                img_label.configure(text="Image selected ✔")

        img_label = ctk.CTkLabel(win, text="No image selected")
        img_label.grid(row=12, column=1, sticky="w", padx=12)

        ctk.CTkButton(win, text="Choose Image", command=choose_image).grid(
            row=12, column=0, padx=12, pady=8
        )

        # ---------- SAVE ----------
        def save():
            if not entries["Title"].get():
                messagebox.showerror("Error", "Title is required")
                return

            prop = {
                "title": entries["Title"].get(),
                "property_type": property_type.get(),
                "sell_method": sell_method.get(),
                "payment_type": payment_type.get(),
                "price": entries["Price"].get(),
                "beds": int(entries["Beds"].get() or 0),
                "baths": float(entries["Baths"].get() or 0),
                "size_sqm": entries["Size (sqm)"].get(),
                "land_width": entries["Land Width"].get(),
                "address": entries["Address"].get(),
                "city": entries["City"].get(),
                "description": desc.get("1.0", "end").strip(),
                "image_blob": image_blob["data"],
                "image_mime": "image/jpeg",
            }

            self.db.insert_property(prop)
            self.refresh_list()
            win.destroy()

        ctk.CTkButton(win, text="Save Property", command=save).grid(
            row=13, column=0, columnspan=2, pady=20
        )
