from PyQt5 import QtCore, QtGui, QtWidgets
import sys
# Dependencies: PyQt5 and sys (standard application system module).

# --- Configuration and Exit Codes ---
EXIT_CODE_REBOOT = 100 
EXIT_CODE_LOGIN_FAIL = 101

# --- Utility Class for Integer ID Generation (Replaced UUID) ---

class PropertyCounter:
    """Generates sequential integer IDs based on the highest existing ID."""
    current_id = 0

    @classmethod
    def initialize(cls, properties_list):
        """Sets the initial counter value based on existing property IDs."""
        max_id = 0
        for prop in properties_list:
            try:
                # We assume 'id' is an integer for counter tracking
                if isinstance(prop.get('id'), int):
                    max_id = max(max_id, prop['id'])
            except:
                pass # Should not happen with clean data
        cls.current_id = max_id

    @classmethod
    def get_next_id(cls):
        """Increments and returns the next ID."""
        cls.current_id += 1
        return cls.current_id

# ----------------------------------------------------------------------------------------------------------------------
# --- Global Hard-Coded Pre-Database (In-Memory) ---

AGENT_DATABASE = {"alice": "pass123", "ben": "pass456"}

INITIAL_PROPERTIES = [
    {'id': 1, 'title': '990 Skyline Penthouse', 'price': '$1,200,000', 'info': 'Stunning city views from this luxury high-rise. Includes smart home features and concierge service.', 
     'agent': 'alice', 'agent_phone': '+63 912 345 6789', 'type': 'Condominium', 'rooms': 5, 'bathrooms': 3.5, 'bedrooms': 3, 'listing_type': 'Sale',
     'image_path': 'images/condo_skyline.jpg'},
    
    {'id': 2, 'title': '78 Oak Lane, Countryside', 'price': '$320,000', 'info': 'Quiet suburban family home with large backyard and newly renovated kitchen.', 
     'agent': 'ben', 'agent_phone': '+63 917 555 1234', 'type': 'Single-Family House', 'rooms': 8, 'bathrooms': 3.0, 'bedrooms': 4, 'listing_type': 'Sale',
     'image_path': 'images/family_house.jpg'},
    
    {'id': 3, 'title': '123 Maple Drive, Suburbia', 'price': '$2,500 / mo', 'info': 'Two-story townhouse available for immediate occupancy. Close to schools and parks.', 
     'agent': 'alice', 'agent_phone': '+63 912 345 6789', 'type': 'Townhouse', 'rooms': 6, 'bathrooms': 2.0, 'bedrooms': 3, 'listing_type': 'Rent',
     'image_path': 'images/townhouse.jpg'},
     
    {'id': 4, 'title': '404 Hidden Valley Lot', 'price': '$80,000', 'info': 'Raw land ready for development. Utilities access nearby.', 
     'agent': '', 'agent_phone': '', 'type': 'Land', 'rooms': 0, 'bathrooms': 0.0, 'bedrooms': 0, 'listing_type': 'Sale',
     'image_path': None},
]

CURRENT_PROPERTIES = INITIAL_PROPERTIES[:] 
# ----------------------------------------------------------------------------------------------------------------------


# --- 1. PropertyCard Class (Widget for sidebar and image generation) ---

class PropertyCard(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal(object)

    def __init__(self, prop: dict, parent=None):
        super(PropertyCard, self).__init__(parent)
        self.prop = prop
        self.setObjectName("PropertyCard")
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.build_ui()

    def build_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        
        thumb = QtWidgets.QLabel(self)
        thumb.setFixedSize(120, 80)
        thumb.setPixmap(self.generate_thumb(self.prop.get('title', ''), thumb.size()))
        layout.addWidget(thumb)

        v = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel(self.prop.get('title', 'Unknown'))
        price_text = f"**{self.prop.get('listing_type', 'SALE').upper()}**: {self.prop.get('price', '')}"
        price = QtWidgets.QLabel(price_text)
        features = f"{self.prop.get('bedrooms', '?')} Beds | {self.prop.get('bathrooms', '?')} Baths | {self.prop.get('type', 'Property')}"
        info = QtWidgets.QLabel(features)
        
        title.setObjectName('pc_title')
        price.setObjectName('pc_price')
        info.setObjectName('pc_info')
        v.addWidget(title)
        v.addWidget(price)
        v.addWidget(info)
        layout.addLayout(v)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.prop)
        super(PropertyCard, self).mousePressEvent(event)

    @staticmethod
    def generate_thumb(text, size):
        w = size.width()
        h = size.height()
        pix = QtGui.QPixmap(w, h)
        painter = QtGui.QPainter(pix)
        color = QtGui.QColor(52, 61, 76)
        painter.fillRect(0, 0, w, h, color)
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200)))
        font = QtGui.QFont('Segoe UI', int(min(w, h) / 5))
        font.setBold(True)
        painter.setFont(font)
        words = text.split()
        initials = ''.join([w[0] for w in words[:2]]).upper() if words else 'P'
        painter.drawText(pix.rect(), QtCore.Qt.AlignCenter, initials)
        painter.end()
        return pix

    @staticmethod
    def generate_image(prop_type, size):
        w = size.width()
        h = size.height()
        pix = QtGui.QPixmap(w, h)
        pix.fill(QtGui.QColor(17, 24, 39))
        painter = QtGui.QPainter(pix)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        if 'House' in prop_type or 'Townhouse' in prop_type:
            house_color = QtGui.QColor(253, 230, 138)
            painter.setBrush(QtGui.QBrush(house_color))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRect(int(w * 0.3), int(h * 0.4), int(w * 0.4), int(h * 0.4))
            roof_color = QtGui.QColor(249, 115, 22)
            painter.setBrush(QtGui.QBrush(roof_color))
            roof = QtGui.QPolygonF([
                QtCore.QPointF(w * 0.25, h * 0.4),
                QtCore.QPointF(w * 0.75, h * 0.4),
                QtCore.QPointF(w * 0.5, h * 0.2)
            ])
            painter.drawPolygon(roof)
        elif 'Condominium' in prop_type:
            building_color = QtGui.QColor(203, 213, 225)
            painter.setBrush(QtGui.QBrush(building_color))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRect(int(w * 0.4), int(h * 0.2), int(w * 0.2), int(h * 0.6))
        
        painter.setPen(QtGui.QPen(QtGui.QColor(156, 163, 175)))
        font = QtGui.QFont('Segoe UI', 10)
        painter.setFont(font)
        painter.drawText(pix.rect(), QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter, prop_type.upper() + " Placeholder")

        painter.end()
        return pix

# ----------------------------------------------------------------------------------------------------------------------
# --- 2. Role Selection Dialog (Initial screen) ---

class RoleSelectionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RoleSelectionDialog, self).__init__(parent)
        self.setWindowTitle("Select Role")
        self.setFixedSize(450, 250)
        
        self.apply_stylesheet()
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QtWidgets.QLabel("Welcome! How would you like to proceed?")
        title_label.setObjectName("selectionTitle")
        layout.addWidget(title_label, alignment=QtCore.Qt.AlignCenter)

        button_layout = QtWidgets.QHBoxLayout()
        self.buyer_btn = QtWidgets.QPushButton("Buyer")
        self.buyer_btn.setObjectName("selectionBuyerBtn")
        self.buyer_btn.clicked.connect(lambda: self.set_role_and_accept("Buyer"))
        self.agent_btn = QtWidgets.QPushButton("Agent")
        self.agent_btn.setObjectName("selectionAgentBtn")
        self.agent_btn.clicked.connect(lambda: self.set_role_and_accept("Agent"))
        button_layout.addWidget(self.buyer_btn)
        button_layout.addWidget(self.agent_btn)
        layout.addLayout(button_layout)
        self.selected_role = None

    def set_role_and_accept(self, role):
        self.selected_role = role
        self.accept()
        
    def get_selected_role(self):
        return self.selected_role

    def apply_stylesheet(self):
        style = """
        QDialog { background-color: #0F172A; color: #E2E8F0; font-family: 'Segoe UI', Arial; }
        QLabel#selectionTitle { 
            font-size: 16px; 
            font-weight: 500; 
            /* 💡 Updated to white text as requested */
            color: #FFFFFF; 
        }
        QPushButton#selectionBuyerBtn, QPushButton#selectionAgentBtn { 
            font-size: 18px; font-weight: bold; padding: 20px 10px; min-height: 80px;
            border-radius: 12px; cursor: pointer;
        }
        QPushButton#selectionBuyerBtn { background-color: #10B981; color: #0F172A; }
        QPushButton#selectionBuyerBtn:hover { background-color: #059669; }
        QPushButton#selectionAgentBtn { background-color: #2563EB; color: #E2E8F0; }
        QPushButton#selectionAgentBtn:hover { background-color: #1D4ED8; }
        """
        self.setStyleSheet(style)

# ----------------------------------------------------------------------------------------------------------------------
# --- 3. Agent Registration Dialog ---

class RegistrationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RegistrationDialog, self).__init__(parent)
        self.setWindowTitle("Agent Registration")
        self.setFixedSize(350, 300) 
        self.apply_stylesheet() 

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        
        title_label = QtWidgets.QLabel("New Agent Sign Up")
        title_label.setObjectName("regTitle")
        layout.addWidget(title_label, alignment=QtCore.Qt.AlignCenter)

        self.user_input = QtWidgets.QLineEdit()
        self.user_input.setPlaceholderText("New Username (e.g., jane)")
        self.user_input.setObjectName("regInput")
        layout.addWidget(self.user_input)

        self.pass_input = QtWidgets.QLineEdit()
        self.pass_input.setPlaceholderText("Password (at least 6 characters)")
        self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pass_input.setObjectName("regInput")
        layout.addWidget(self.pass_input)

        self.confirm_pass_input = QtWidgets.QLineEdit()
        self.confirm_pass_input.setPlaceholderText("Confirm Password")
        self.confirm_pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_pass_input.setObjectName("regInput")
        layout.addWidget(self.confirm_pass_input)
        
        self.register_btn = QtWidgets.QPushButton("Register & Login")
        self.register_btn.setObjectName("registerBtn")
        self.register_btn.clicked.connect(self.handle_registration) 
        layout.addWidget(self.register_btn)
        
        self.confirm_pass_input.returnPressed.connect(self.handle_registration)

        self.registered_username = None

    def handle_registration(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text()
        confirm_password = self.confirm_pass_input.text()

        if not (username and password and confirm_password):
            QtWidgets.QMessageBox.warning(self, "Error", "All fields are required.")
            return
        if password != confirm_password:
            QtWidgets.QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        if len(password) < 6:
            QtWidgets.QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
            return
        global AGENT_DATABASE
        if username in AGENT_DATABASE:
            QtWidgets.QMessageBox.warning(self, "Error", f"Username '{username}' already exists.")
            return

        AGENT_DATABASE[username] = password
        self.registered_username = username
        
        QtWidgets.QMessageBox.information(self, "Success", f"Agent '{username}' registered successfully! Logging in...")
        
        self.accept()

    def get_registered_username(self):
        return self.registered_username

    def apply_stylesheet(self):
        style = """
        QDialog { background-color: #0F172A; color: #E2E8F0; font-family: 'Segoe UI', Arial; }
        QLabel#regTitle { font-size: 18px; font-weight: 600; margin-bottom: 10px; }
        QLineEdit#regInput { 
            background-color: #111827; border: 1px solid #334155; border-radius: 4px; 
            padding: 8px; color: #E2E8F0;
        }
        QPushButton#registerBtn { 
            background-color: #10B981; border-radius: 8px; padding: 10px; 
            color: #0F172A; font-weight: bold; margin-top: 10px; 
        }
        """
        self.setStyleSheet(style)


# ----------------------------------------------------------------------------------------------------------------------
# --- 4. Agent Login Dialog ---

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Agent Login")
        self.setFixedSize(350, 260) 
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        
        title_label = QtWidgets.QLabel("Agent Sign In")
        title_label.setObjectName("loginTitle")
        layout.addWidget(title_label, alignment=QtCore.Qt.AlignCenter)

        self.user_input = QtWidgets.QLineEdit()
        self.user_input.setPlaceholderText("Username (e.g., alice)")
        self.user_input.setObjectName("loginInput")
        layout.addWidget(self.user_input)

        self.pass_input = QtWidgets.QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pass_input.setObjectName("loginInput")
        layout.addWidget(self.pass_input)
        
        button_h_layout = QtWidgets.QHBoxLayout()

        self.login_btn = QtWidgets.QPushButton("Login")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.clicked.connect(self.handle_login) 
        button_h_layout.addWidget(self.login_btn)
        
        self.register_btn = QtWidgets.QPushButton("Register")
        self.register_btn.setObjectName("registerLinkBtn")
        self.register_btn.clicked.connect(self.open_registration_dialog) 
        button_h_layout.addWidget(self.register_btn)

        layout.addLayout(button_h_layout)
        
        self.pass_input.returnPressed.connect(self.handle_login)

        self.username = None
        self.accepted_login = False
        self.accepted_registration = False 
        
        self.apply_stylesheet() 

    def handle_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()

        if not (username and password):
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        global AGENT_DATABASE
        if AGENT_DATABASE.get(username) == password:
            self.username = username
            self.accepted_login = True
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid username or password.")
            
    def open_registration_dialog(self):
        reg_dialog = RegistrationDialog(self)
        
        self.hide() 
        
        if reg_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.accepted_registration = True
            self.username = reg_dialog.get_registered_username()
            self.accept()
        else:
            self.show()

    def get_login_info(self):
        return self.accepted_login or self.accepted_registration, self.username

    def apply_stylesheet(self):
        style = """
        QDialog { background-color: #0F172A; color: #E2E8F0; font-family: 'Segoe UI', Arial; }
        QLabel#loginTitle { font-size: 18px; font-weight: 600; margin-bottom: 10px; }
        QLineEdit#loginInput { 
            background-color: #111827; border: 1px solid #334155; border-radius: 4px; 
            padding: 8px; color: #E2E8F0;
        }
        QPushButton#loginBtn { 
            background-color: #2563EB; border-radius: 8px; padding: 10px; 
            color: #E2E8F0; font-weight: bold; 
        }
        QPushButton#registerLinkBtn { 
            background-color: #334155; border-radius: 8px; padding: 10px; 
            color: #E2E8F0; font-weight: bold; 
        }
        """
        self.setStyleSheet(style)

# ----------------------------------------------------------------------------------------------------------------------
# --- 5. PropertyEditorDialog (Handles Add and Edit) ---

class PropertyEditorDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, property_data=None):
        super(PropertyEditorDialog, self).__init__(parent)
        
        self.is_edit_mode = property_data is not None
        self.original_data = property_data if self.is_edit_mode else {}
        
        self.setWindowTitle("Edit Property Listing" if self.is_edit_mode else "Add New Property Listing")
        self.setFixedSize(500, 550) 
        self.property_data = None
        self.apply_stylesheet()
        
        main_layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()
        
        self.title_input = QtWidgets.QLineEdit(self.original_data.get('title', ''))
        form_layout.addRow("Title:", self.title_input)

        self.listing_type_input = QtWidgets.QComboBox()
        self.listing_type_input.addItems(["Sale", "Rent"])
        if self.is_edit_mode:
             self.listing_type_input.setCurrentText(self.original_data.get('listing_type', 'Sale'))
        form_layout.addRow("Listing Type:", self.listing_type_input)

        self.price_input = QtWidgets.QLineEdit(self.original_data.get('price', ''))
        self.price_input.setPlaceholderText("$ Price or Rent / mo (e.g. $500,000)")
        form_layout.addRow("Price:", self.price_input)

        self.type_input = QtWidgets.QComboBox()
        self.type_input.addItems(["Single-Family House", "Condominium", "Townhouse", "Land"])
        if self.is_edit_mode:
            self.type_input.setCurrentText(self.original_data.get('type', 'Single-Family House'))
        form_layout.addRow("Property Type:", self.type_input)
        
        self.bedrooms_input = QtWidgets.QSpinBox()
        self.bedrooms_input.setRange(0, 10)
        self.bedrooms_input.setValue(self.original_data.get('bedrooms', 0))
        form_layout.addRow("Bedrooms:", self.bedrooms_input)

        self.bathrooms_input = QtWidgets.QDoubleSpinBox()
        self.bathrooms_input.setRange(0, 8)
        self.bathrooms_input.setSingleStep(0.5)
        self.bathrooms_input.setValue(self.original_data.get('bathrooms', 0.0))
        form_layout.addRow("Bathrooms:", self.bathrooms_input)
        
        self.info_input = QtWidgets.QTextEdit(self.original_data.get('info', ''))
        self.info_input.setPlaceholderText("Enter a detailed description of the property...")
        form_layout.addRow("Description:", self.info_input)
        
        self.image_path_input = QtWidgets.QLineEdit(self.original_data.get('image_path', ''))
        self.image_path_input.setPlaceholderText("Optional: path to image file (e.g., images/new_house.jpg)")
        form_layout.addRow("Image Path:", self.image_path_input)

        main_layout.addLayout(form_layout)
        
        # Buttons
        save_text = "Save Changes" if self.is_edit_mode else "Add Listing"
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)
        save_btn = button_box.addButton(save_text, QtWidgets.QDialogButtonBox.AcceptRole)
        save_btn.clicked.connect(self.save_property)
        
        main_layout.addWidget(button_box)
        
    def save_property(self):
        title = self.title_input.text().strip()
        price = self.price_input.text().strip()
        info = self.info_input.toPlainText().strip()
        image_path = self.image_path_input.text().strip()

        if not (title and price and info):
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Title, Price, and Description are required.")
            return

        self.property_data = {
            'title': title,
            'price': price,
            'info': info,
            'listing_type': self.listing_type_input.currentText(),
            'type': self.type_input.currentText(),
            'bedrooms': self.bedrooms_input.value(),
            'bathrooms': self.bathrooms_input.value(),
            'rooms': self.bedrooms_input.value() + 2,
            'image_path': image_path if image_path else None,
        }
        self.accept()

    def get_property_data(self):
        return self.property_data

    def apply_stylesheet(self):
        style = """
        QDialog { background-color: #0F172A; color: #E2E8F0; font-family: 'Segoe UI', Arial; }
        QLabel { color: #A3A3A3; }
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox { 
            background-color: #111827; border: 1px solid #334155; border-radius: 4px; 
            padding: 6px; color: #E2E8F0;
        }
        QDialogButtonBox QPushButton[text^="Save"], QDialogButtonBox QPushButton[text^="Add"] { 
            background-color: #2563EB; color: #E2E8F0; border-radius: 6px; 
            padding: 8px 16px; font-weight: bold;
        }
        """
        self.setStyleSheet(style)


# ----------------------------------------------------------------------------------------------------------------------
# --- 6. Main Window UI (The core application view) ---

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, initial_user=None): 
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)

        global CURRENT_PROPERTIES
        self.properties = CURRENT_PROPERTIES 
        
        # Initialize ID counter based on initial properties
        PropertyCounter.initialize(self.properties)

        if initial_user:
            self.is_agent_logged_in = True
            self.agent_username = initial_user
        else:
            self.is_agent_logged_in = False
            self.agent_username = None
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.verticalLayout_main = QtWidgets.QVBoxLayout(self.centralwidget)

        # Top Bar setup 
        self.TopBar = QtWidgets.QFrame(self.centralwidget)
        self.TopBar.setObjectName('TopBar')
        self.TopBar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.horizontalLayout_topbar = QtWidgets.QHBoxLayout(self.TopBar)

        self.logoLabel = QtWidgets.QLabel("🏠", self.TopBar)
        self.logoLabel.setObjectName('logoLabel')
        self.titleLabel = QtWidgets.QLabel("Real Estate Portal", self.TopBar)
        self.titleLabel.setObjectName('titleLabel')

        self.horizontalLayout_topbar.addWidget(self.logoLabel)
        self.horizontalLayout_topbar.addWidget(self.titleLabel)
        self.horizontalLayout_topbar.addStretch()

        self.buyerBtn = QtWidgets.QPushButton("Buyer View", self.TopBar)
        self.buyerBtn.setObjectName('buyerBtn')
        
        self.agentBtn = QtWidgets.QPushButton(self.TopBar)
        self.agentBtn.setObjectName('agentBtn') 
        
        if self.is_agent_logged_in:
            self.agentBtn.setText(f"Agent Logout ({self.agent_username})")
        else:
            self.agentBtn.setText("Agent Login")
            
        self.horizontalLayout_topbar.addWidget(self.buyerBtn)
        self.horizontalLayout_topbar.addWidget(self.agentBtn)
        self.verticalLayout_main.addWidget(self.TopBar)
        
        # Body and Sidebar setup
        self.horizontalLayout_body = QtWidgets.QHBoxLayout()
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.verticalLayout_sidebar = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)

        # --- Search/Filter Bar (Including Advanced Filters) ---
        self.SidebarContainer = QtWidgets.QVBoxLayout()
        
        self.search_input = QtWidgets.QLineEdit(self.centralwidget)
        self.search_input.setPlaceholderText("Search by title, type, or agent...")
        self.search_input.setObjectName('searchInput')
        
        self.filter_layout = QtWidgets.QHBoxLayout()
        self.price_label = QtWidgets.QLabel("Price Max:")
        self.price_filter = QtWidgets.QLineEdit()
        self.price_filter.setPlaceholderText("$ Max")
        self.price_filter.setFixedWidth(100)
        self.price_filter.setObjectName('filterInput')
        
        # Min Bedrooms Filter (QSpinBox)
        self.beds_label = QtWidgets.QLabel("Min Beds:")
        self.min_beds_filter = QtWidgets.QSpinBox()
        self.min_beds_filter.setRange(0, 10)
        self.min_beds_filter.setFixedWidth(60)
        self.min_beds_filter.setObjectName('filterSpinBox')
        
        # Min Bathrooms Filter (QDoubleSpinBox)
        self.baths_label = QtWidgets.QLabel("Min Baths:")
        self.min_baths_filter = QtWidgets.QDoubleSpinBox()
        self.min_baths_filter.setRange(0, 8)
        self.min_baths_filter.setSingleStep(0.5)
        self.min_baths_filter.setFixedWidth(60)
        self.min_baths_filter.setObjectName('filterSpinBox')
        
        self.type_label = QtWidgets.QLabel("Type:")
        self.type_filter = QtWidgets.QComboBox()
        self.type_filter.addItems(["All", "Single-Family House", "Condominium", "Townhouse", "Land"])
        self.type_filter.setObjectName('filterInput')
        
        self.filter_layout.addWidget(self.price_label)
        self.filter_layout.addWidget(self.price_filter)
        self.filter_layout.addWidget(self.beds_label)
        self.filter_layout.addWidget(self.min_beds_filter)
        self.filter_layout.addWidget(self.baths_label)
        self.filter_layout.addWidget(self.min_baths_filter)
        self.filter_layout.addWidget(self.type_label)
        self.filter_layout.addWidget(self.type_filter)
        self.filter_layout.addStretch()

        self.SidebarContainer.addWidget(self.search_input)
        self.SidebarContainer.addLayout(self.filter_layout)
        self.SidebarContainer.addWidget(self.scrollArea)
        self.horizontalLayout_body.addLayout(self.SidebarContainer, 30)

        # Main Panel setup
        self.MainPanel = QtWidgets.QFrame(self.centralwidget)
        self.MainPanel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.verticalLayout_mainpanel = QtWidgets.QVBoxLayout(self.MainPanel)

        # --- Agent Action Panel (CRUD Buttons) ---
        self.AgentActionFrame = QtWidgets.QFrame(self.MainPanel)
        self.AgentActionFrame.setObjectName('AgentActionFrame')
        self.AgentActionLayout = QtWidgets.QHBoxLayout(self.AgentActionFrame)
        self.AgentActionLayout.setContentsMargins(0, 0, 0, 10) 
        
        self.addPropertyBtn = QtWidgets.QPushButton("➕ Add New Property", self.AgentActionFrame)
        self.addPropertyBtn.setObjectName('addPropertyBtn')
        self.editPropertyBtn = QtWidgets.QPushButton("✎ Edit Details", self.AgentActionFrame)
        self.editPropertyBtn.setObjectName('editPropertyBtn')
        self.deletePropertyBtn = QtWidgets.QPushButton("🗑️ Delete Listing", self.AgentActionFrame)
        self.deletePropertyBtn.setObjectName('deletePropertyBtn')
        
        self.AgentActionLayout.addWidget(self.addPropertyBtn)
        self.AgentActionLayout.addWidget(self.editPropertyBtn)
        self.AgentActionLayout.addWidget(self.deletePropertyBtn)
        self.AgentActionLayout.addStretch()
        
        self.verticalLayout_mainpanel.addWidget(self.AgentActionFrame)
        self.AgentActionFrame.setVisible(self.is_agent_logged_in)
        # --------------------------
        
        self.detailsImage = QtWidgets.QLabel(self.MainPanel)
        self.detailsImage.setFixedSize(480, 300)
        self.detailsImage.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_mainpanel.addWidget(self.detailsImage, alignment=QtCore.Qt.AlignCenter)
        self.detailsTitle = QtWidgets.QLabel("Select a property from the list to view full details.", self.MainPanel)
        self.detailsTitle.setWordWrap(True)
        self.detailsTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.detailsTitle.setObjectName('detailsTitle')
        self.verticalLayout_mainpanel.addWidget(self.detailsTitle)
        self.detailsPrice = QtWidgets.QLabel("", self.MainPanel)
        self.detailsPrice.setAlignment(QtCore.Qt.AlignCenter)
        self.detailsPrice.setObjectName('detailsPrice')
        self.verticalLayout_mainpanel.addWidget(self.detailsPrice)
        
        self.specsGroupBox = QtWidgets.QGroupBox("Specifications", self.MainPanel)
        self.specsLayout = QtWidgets.QFormLayout(self.specsGroupBox)
        self.detailsPropertyType = QtWidgets.QLabel("")
        self.detailsRooms = QtWidgets.QLabel("")
        self.detailsBedrooms = QtWidgets.QLabel("")
        self.detailsBathrooms = QtWidgets.QLabel("")
        self.detailsListingType = QtWidgets.QLabel("")
        self.specsLayout.addRow("Listing For:", self.detailsListingType)
        self.specsLayout.addRow("Property Type:", self.detailsPropertyType)
        self.specsLayout.addRow("Bedrooms:", self.detailsBedrooms)
        self.specsLayout.addRow("Bathrooms:", self.detailsBathrooms)
        self.specsLayout.addRow("Total Rooms:", self.detailsRooms)
        self.verticalLayout_mainpanel.addWidget(self.specsGroupBox)

        self.detailsInfo = QtWidgets.QLabel("", self.MainPanel)
        self.detailsInfo.setAlignment(QtCore.Qt.AlignLeft)
        self.detailsInfo.setWordWrap(True)
        self.detailsInfo.setObjectName('detailsInfo')
        self.verticalLayout_mainpanel.addWidget(self.detailsInfo)

        self.agentBox = QtWidgets.QGroupBox("Agent Handling", self.MainPanel)
        ab_layout = QtWidgets.QHBoxLayout(self.agentBox)
        self.agentName = QtWidgets.QLabel("Name: N/A", self.agentBox)
        self.agentPhone = QtWidgets.QLabel("Phone: N/A", self.agentBox)
        self.agentStatus = QtWidgets.QLabel("Status: Unknown", self.agentBox) 
        self.agentStatus.setObjectName('agentStatus')
        
        ab_layout.addWidget(self.agentName)
        ab_layout.addWidget(self.agentStatus)
        ab_layout.addStretch()
        ab_layout.addWidget(self.agentPhone)
        self.verticalLayout_mainpanel.addWidget(self.agentBox)

        self.contactBtn = QtWidgets.QPushButton("Contact Agent", self.MainPanel)
        self.contactBtn.setObjectName('contactBtn')
        self.verticalLayout_mainpanel.addWidget(self.contactBtn, alignment=QtCore.Qt.AlignCenter)

        self.verticalLayout_mainpanel.addStretch() 

        self.horizontalLayout_body.addWidget(self.MainPanel, 70)
        self.verticalLayout_main.addLayout(self.horizontalLayout_body)
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Wire up signals
        self.card_widgets = []
        self.update_sidebar_listings() # Initial population of the sidebar

        self.contactBtn.clicked.connect(self.on_contact_clicked)
        self.buyerBtn.clicked.connect(self.on_buyer_view)
        self.agentBtn.clicked.connect(self.on_agent_button_clicked) 
        self.addPropertyBtn.clicked.connect(self.open_add_property_dialog)
        self.editPropertyBtn.clicked.connect(self.open_edit_property_dialog)
        self.deletePropertyBtn.clicked.connect(self.delete_property)
        self.search_input.textChanged.connect(self.apply_filters)
        self.price_filter.textChanged.connect(self.apply_filters)
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        self.min_beds_filter.valueChanged.connect(self.apply_filters)
        self.min_baths_filter.valueChanged.connect(self.apply_filters)
        
        self.apply_stylesheet(MainWindow)
        
        self.selected_property = None 


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Real Estate Portal (In-Memory)")

    # --- UI Update Logic ---
    def on_card_clicked(self, prop):
        self.selected_property = prop
        
        self.detailsTitle.setText(prop.get('title', ''))
        self.detailsPrice.setText(prop.get('price', ''))
        self.detailsInfo.setText(prop.get('info', ''))
        
        self.detailsListingType.setText(prop.get('listing_type', 'Sale').capitalize())
        self.detailsPropertyType.setText(prop.get('type', 'Residential'))
        self.detailsBedrooms.setText(str(prop.get('bedrooms', 'N/A')))
        baths = prop.get('bathrooms', 'N/A')
        bath_text = f"{baths} ({int(baths)} Full, {int(baths*2 % 2)} Half)" if isinstance(baths, (int, float)) and baths > 0 else str(baths)
        self.detailsBathrooms.setText(bath_text)
        self.detailsRooms.setText(str(prop.get('rooms', 'N/A')))
        
        agent_name = prop.get('agent', 'N/A')
        agent_phone = prop.get('agent_phone', 'N/A')
        self.agentName.setText(f"Name: {agent_name}")
        self.agentPhone.setText(f"Phone: {agent_phone}")

        if agent_name and agent_phone:
            status = "Status: Available"
            status_style = "color: #34D399; font-weight: bold;"
            self.contactBtn.setEnabled(True)
        else:
            status = "Status: No Agent Assigned"
            status_style = "color: #F87171; font-weight: bold;"
            self.contactBtn.setEnabled(False) 
            
        self.agentStatus.setText(status)
        self.agentStatus.setStyleSheet(status_style)

        image_path = prop.get('image_path')
        pix = QtGui.QPixmap()
        
        if image_path and pix.load(image_path):
            pix = pix.scaled(self.detailsImage.size(), 
                             QtCore.Qt.KeepAspectRatio, 
                             QtCore.Qt.SmoothTransformation)
            self.detailsImage.setText("")
        else:
            self.detailsImage.setText("No Image Found")
            prop_type = prop.get('type', 'Property')
            pix = PropertyCard.generate_image(prop_type, self.detailsImage.size())
            
        self.detailsImage.setPixmap(pix) 

    # --- Agent Management Logic (CRUD) ---

    def open_add_property_dialog(self):
        add_dialog = PropertyEditorDialog(self.centralwidget)
        if add_dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_prop = add_dialog.get_property_data()
            if new_prop:
                new_prop['id'] = PropertyCounter.get_next_id() 
                new_prop['agent'] = self.agent_username
                new_prop['agent_phone'] = '(New Agent Listing)'
                
                self.properties.append(new_prop)
                self.update_sidebar_listings()
                QtWidgets.QMessageBox.information(None, 'Success', f"Property '{new_prop['title']}' added! (Temporary listing)")

    def open_edit_property_dialog(self):
        if not self.selected_property:
            QtWidgets.QMessageBox.warning(None, 'Error', 'Please select a property to edit.')
            return

        agent_name = self.selected_property.get('agent', '').lower()
        if agent_name and agent_name != self.agent_username.lower():
             QtWidgets.QMessageBox.warning(None, 'Unauthorized', 'You can only edit your own listings.')
             return

        edit_dialog = PropertyEditorDialog(self.centralwidget, property_data=self.selected_property)
        if edit_dialog.exec_() == QtWidgets.QDialog.Accepted:
            updated_prop = edit_dialog.get_property_data()
            if updated_prop:
                
                try:
                    index = next(i for i, p in enumerate(self.properties) if p['id'] == self.selected_property['id'])
                    
                    self.properties[index].update(updated_prop)
                    
                    self.update_sidebar_listings()
                    self.on_card_clicked(self.properties[index]) 
                    
                    QtWidgets.QMessageBox.information(None, 'Success', f"Property '{updated_prop['title']}' updated! (Temporary change)")
                except StopIteration:
                    QtWidgets.QMessageBox.warning(None, 'Error', 'Failed to find property ID for update.')


    def delete_property(self):
        if not self.selected_property:
            QtWidgets.QMessageBox.warning(None, 'Error', 'Please select a property to delete.')
            return

        agent_name = self.selected_property.get('agent', '').lower()
        if agent_name and agent_name != self.agent_username.lower():
             QtWidgets.QMessageBox.warning(None, 'Unauthorized', 'You can only delete your own listings.')
             return

        reply = QtWidgets.QMessageBox.question(self.centralwidget, 'Confirm Delete',
            f"Are you sure you want to delete the listing: '{self.selected_property['title']}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            global CURRENT_PROPERTIES
            # Delete the property using its unique integer ID
            CURRENT_PROPERTIES = [p for p in CURRENT_PROPERTIES if p['id'] != self.selected_property['id']]
            self.properties = CURRENT_PROPERTIES # Update local reference

            self.detailsTitle.setText("Listing deleted. Select another property or add a new one.")
            self.detailsImage.clear()
            self.selected_property = None
            
            self.update_sidebar_listings()
            QtWidgets.QMessageBox.information(None, 'Deleted', 'Listing successfully deleted! (Temporary deletion)')

    # --- Filtering and View Logic (Includes Advanced Filters) ---

    def update_sidebar_listings(self):
        """Clears and rebuilds the sidebar based on the view mode (Agent or Buyer)."""
        displayed_properties = []
        all_properties = self.properties

        if self.is_agent_logged_in:
            agent_name = self.agent_username.lower()
            for p in all_properties:
                prop_agent = p.get('agent', '').lower()
                # Agent View: Show only their listings OR unassigned listings
                if prop_agent == agent_name or not prop_agent:
                    displayed_properties.append(p)
        else:
            # Buyer View: Show all properties
            displayed_properties = all_properties
            
        for i in reversed(range(self.verticalLayout_sidebar.count())): 
            widget = self.verticalLayout_sidebar.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
                
        self.card_widgets.clear()
        
        if not displayed_properties:
            msg = QtWidgets.QLabel("No listings match your criteria or agent view.", self.scrollAreaWidgetContents)
            msg.setObjectName('noResultsLabel')
            self.verticalLayout_sidebar.addWidget(msg, alignment=QtCore.Qt.AlignCenter)
        else:
            for p in displayed_properties:
                card = PropertyCard(p, self.scrollAreaWidgetContents)
                self.verticalLayout_sidebar.addWidget(card)
                card.clicked.connect(self.on_card_clicked)
                self.card_widgets.append(card)
            
        self.verticalLayout_sidebar.addStretch()
        self.apply_filters()
        
    def apply_filters(self):
        search_text = self.search_input.text().strip().lower()
        
        # Max Price Filter Logic
        max_price_text = self.price_filter.text().strip().replace('$', '').replace(',', '')
        max_price = float(max_price_text) if max_price_text.replace('.', '', 1).isdigit() and max_price_text.count('.') < 2 else float('inf')
        
        # Read minimum beds/baths from SpinBoxes
        min_beds = self.min_beds_filter.value()
        min_baths = self.min_baths_filter.value()
        
        selected_type = self.type_filter.currentText()

        for card in self.card_widgets:
            prop = card.prop
            
            # --- Text and Type Filtering ---
            prop_string = f"{prop['title']} {prop['type']} {prop['agent']}".lower()
            text_match = search_text in prop_string
            type_match = (selected_type == "All") or (prop['type'] == selected_type)
            
            # --- Price Filtering ---
            price_raw = prop['price'].replace('$', '').replace(',', '').replace(' / mo', '').strip()
            try:
                price_value = float(price_raw)
            except ValueError:
                price_value = float('inf')

            price_match = price_value <= max_price
            
            # --- Min Beds/Baths Filtering ---
            beds_match = prop.get('bedrooms', 0) >= min_beds
            baths_match = prop.get('bathrooms', 0.0) >= min_baths

            # --- Final Visibility Check ---
            is_visible = text_match and type_match and price_match and beds_match and baths_match
            card.setVisible(is_visible)


    # --- Login/Logout Flow Control ---

    def on_agent_login_success(self, username):
        self.is_agent_logged_in = True
        self.agent_username = username
        
        self.agentBtn.setText(f"Agent Logout ({self.agent_username})")
        if hasattr(self, 'AgentActionFrame'):
            self.AgentActionFrame.setVisible(True) 
            
        self.update_sidebar_listings() 
        
        QtWidgets.QMessageBox.information(None, 'Agent Login', f'Welcome, {username}! Showing your assigned listings.')

    def on_agent_logout(self):
        QtWidgets.QMessageBox.information(None, 'Agent Logout', 'Logging out. Returning to Buyer View.')
        
        self.is_agent_logged_in = False
        self.agent_username = None
        
        self.agentBtn.setText("Agent Login")
        if hasattr(self, 'AgentActionFrame'):
            self.AgentActionFrame.setVisible(False)
            
        self.update_sidebar_listings() 
        
        self.detailsTitle.setText("Select a property from the list to view full details.")
        self.detailsImage.clear()
        self.selected_property = None
        
    def on_agent_button_clicked(self):
        if self.is_agent_logged_in:
            self.on_agent_logout()
        else:
            login_dialog = LoginDialog(self.centralwidget)
            if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
                success, username = login_dialog.get_login_info()
                if success:
                    self.on_agent_login_success(username)


    def on_contact_clicked(self):
        if not self.selected_property:
            QtWidgets.QMessageBox.warning(None, 'Error', 'Please select a property first.')
            return

        name = self.selected_property.get('agent', 'N/A')
        phone = self.selected_property.get('agent_phone', 'N/A')
        
        if name == 'N/A' or phone == 'N/A':
             QtWidgets.QMessageBox.information(None, 'Contact Agent', 'This property currently has no assigned agent contact information.')
        else:
            QtWidgets.QMessageBox.information(None, 'Contact Agent', f'Contact {name} at {phone} to schedule a viewing.')


    def on_buyer_view(self):
        if self.is_agent_logged_in:
            # Force log out if agent clicks Buyer View
            self.on_agent_logout()
        else:
            QtWidgets.QMessageBox.information(None, 'Buyer View', 'You are currently in Buyer View (default).')


    def apply_stylesheet(self, MainWindow):
        style = """
        QWidget { background-color: #0F172A; color: #E2E8F0; font-family: 'Segoe UI', Arial; }
        QFrame#TopBar { background-color: #0b1220; padding: 10px; }
        QLabel#logoLabel { font-size: 24px; }
        QLabel#titleLabel { font-size: 18px; font-weight: 600; }
        QFrame#PropertyCard { background-color: #111827; border-radius: 8px; padding: 6px; }
        QLabel#pc_title { font-weight: 600; }
        QLabel#pc_price { color: #34D399; }
        QScrollArea { background: transparent; }
        QFrame#MainPanel { background-color: transparent; }
        QLabel { font-size: 13px; }
        
        QPushButton { 
            background-color: #10B981; border-radius: 8px; padding: 8px 14px; 
            color: #0F172A; font-weight: bold; 
        }
        
        QPushButton#agentBtn { background-color: #2563EB; color: #E2E8F0; }
        QPushButton#addPropertyBtn { background-color: #3B82F6; color: #E2E8F0; }
        QPushButton#editPropertyBtn { background-color: #FBBF24; color: #0F172A; }
        QPushButton#deletePropertyBtn { background-color: #EF4444; color: #E2E8F0; }
        
        QGroupBox { 
            border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; 
            padding: 8px; margin-top: 10px;
        }
        QGroupBox::title { 
            subcontrol-origin: margin; subcontrol-position: top center; 
            padding: 0 5px; color: #A3A3A3;
        }
        QLineEdit#searchInput, QLineEdit#filterInput, QComboBox#filterInput, QSpinBox#filterSpinBox { 
            background-color: #111827; border: 1px solid #334155; border-radius: 4px; 
            padding: 5px; color: #E2E8F0;
        }
        """
        MainWindow.setStyleSheet(style)


# ----------------------------------------------------------------------------------------------------------------------
# --- 7. Main Application Entry Point (Controls Startup) ---

class RealEstateApp:
    def __init__(self):
        self.app = QtWidgets.QApplication.instance()
        if self.app is None:
            self.app = QtWidgets.QApplication(sys.argv)
            
        self.username = None
        self.start_role = None
        
    def start(self):
        
        # 1. Role Selection
        role_dialog = RoleSelectionDialog()
        if role_dialog.exec_() != QtWidgets.QDialog.Accepted:
            sys.exit(0)
            
        self.start_role = role_dialog.get_selected_role()
            
        # 2. Conditional Agent Login
        if self.start_role == "Agent":
            # Pass a valid parent window for the LoginDialog, if available
            login_dialog = LoginDialog(self.app.activeWindow())
            
            if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
                success, self.username = login_dialog.get_login_info()
                if not success:
                    sys.exit(0) 
            else:
                sys.exit(0)
                    
        # 3. Launch Main Window
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow, initial_user=self.username) 
        self.MainWindow.show()
        
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app_runner = RealEstateApp()
    app_runner.start()
