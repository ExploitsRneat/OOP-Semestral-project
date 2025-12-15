import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
import io, os

'''
class MainGUI(ctk.CTk):
    def __init__(self, db_interface):
        super().__init__()
        self.db = db_interface
        self.title("Real Estate Portal")
        self.geometry("1200x800")
        self.configure(fg_color="#0F172A")
        self.current_mode = "buyer"
        self.build_ui()
'''

class MainGUI(ctk.CTkFrame):
    def __init__(self, master, db_interface):
        super().__init__(master, fg_color="#0F172A")
        self.db = db_interface
        self.current_mode = "buyer"
        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):
        top = ctk.CTkFrame(self, fg_color="#0b1220")
        top.pack(side="top", fill="x")

        ctk.CTkLabel(top, text="🏠", font=ctk.CTkFont(size=18)).pack(side="left", padx=12, pady=10)
        ctk.CTkLabel(top, text="Real Estate Portal", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=6)

        self.switch_btn = ctk.CTkButton(top, text="Login", command=self.on_switch_role)
        self.switch_btn.pack(side="right", padx=8, pady=8)

        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=12, pady=12)

        left = ctk.CTkFrame(content, width=360, fg_color="#0F172A")
        left.pack(side="left", fill="y", padx=(0, 12))

        self.list_frame = ctk.CTkScrollableFrame(left, width=340)
        self.list_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.card_widgets = []

        right = ctk.CTkFrame(content, fg_color="#0F172A")
        right.pack(side="left", fill="both", expand=True)

        self.details_image = ctk.CTkLabel(right, text="No Image", width=480, height=300)
        self.details_image.pack(pady=12)

        self.details_title = ctk.CTkLabel(right, text="Select a property from the list.", font=ctk.CTkFont(size=16), wraplength=480)
        self.details_title.pack(pady=6)

        self.details_info = ctk.CTkLabel(right, text="", justify="left", anchor="nw", wraplength=480)
        self.details_info.pack(pady=10)

        self.action_frame = ctk.CTkFrame(right)
        self.add_btn = ctk.CTkButton(self.action_frame, text="➕ Add New Property", command=self.on_add_property)
        self.add_btn.pack(side="left", padx=6)
        self.action_frame.pack_forget()

        self.refresh_list()

    def refresh_list(self):
        props = self.db.fetch_all_properties()

        for w in self.card_widgets:
            w.destroy()
        self.card_widgets.clear()

        for p in props:
            frame = ctk.CTkFrame(self.list_frame, fg_color="#111827", corner_radius=8)
            frame.pack(fill="x", pady=6, padx=6)

            title = ctk.CTkLabel(frame, text=p.get("title", ""), anchor="w", font=ctk.CTkFont(size=13, weight="bold"))
            title.grid(row=0, column=1, sticky="w", padx=6, pady=4)

            info = f"{p.get('beds',0)} Beds | {p.get('baths',0)} Baths | {p.get('property_type','')}"
            ctk.CTkLabel(frame, text=info, anchor="w", text_color="#A3A3A3").grid(row=1, column=1, sticky="w", padx=6, pady=2)

            thumb = ctk.CTkLabel(frame, text="")
            thumb.grid(row=0, column=0, rowspan=2, padx=6, pady=6)

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

    def on_card_click(self, prop):
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

💰 Price: $ {prop.get('price','')}

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

    def on_switch_role(self):
        if self.current_mode == "buyer":
            # Open unified login Toplevel
            from auth import UnifiedLoginFrame

            win = ctk.CTkToplevel(self)
            win.title("Login")
            win.geometry("420x240")
            win.grab_set()

            def on_login(user):
                # Set mode according to role
                self.db.current_user = user
                self.current_mode = user.get("role", "buyer")
                self.switch_btn.configure(text=f"Logout ({self.db.current_user.get('display_name') or self.db.current_user.get('username')})")
                if self.current_mode == "agent":
                    self.action_frame.pack(pady=8)
                else:
                    self.action_frame.pack_forget()

            UnifiedLoginFrame(win, self.db, on_login)
            win.wait_window()
            return

        self.db.current_user = None
        self.current_mode = "buyer"
        self.switch_btn.configure(text="Login")
        self.action_frame.pack_forget()
        messagebox.showinfo("Logout", "You are now in Buyer mode.")

    def on_add_property(self):
        if self.current_mode != "agent":
            messagebox.showerror("Access Denied", "Only agents can add properties.")
            return

        title = simpledialog.askstring("Title", "Property title:", parent=self)
        if not title:
            return

        file = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")])
        blob = open(file, "rb").read() if file else None

        prop = {
            "title": title,
            "property_type": "Condominium",
            "sell_method": "For Sale",
            "payment_type": "Cash",
            "price": "0",
            "beds": 0,
            "baths": 0.0,
            "size_sqm": "",
            "land_width": "0",
            "address": "",
            "city": "",
            "description": "",
            "image_blob": blob,
            "image_mime": "image/jpeg",
        }

        self.db.insert_property(prop)
        self.refresh_list()
