import customtkinter as ctk
from tkinter import messagebox

# ======================================================
# CONFIG
# ======================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

PRIMARY = "#CFA56A"
PRIMARY_HOVER = "#BE955A"

WHITE = "#FFFFFF"
BG = "#F5F5F5"
TEXT = "#1A1A1A"
GRAY = "#666666"
BORDER = "#E6E6E6"

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800


# ======================================================
# AVATAR HELPER
# ======================================================

def create_avatar(parent, initials):

    avatar = ctk.CTkLabel(
        parent,
        text=initials,
        width=40,
        height=40,
        corner_radius=20,
        fg_color=PRIMARY,
        text_color="white",
        font=("Poppins", 12, "bold")
    )

    return avatar


# ======================================================
# DASHBOARD PAGE
# ======================================================

class DashboardPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent, fg_color=BG)

        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="DASHBOARD",
            font=("Poppins", 26, "bold"),
            text_color=TEXT
        )
        title.pack(anchor="w", padx=30, pady=20)

        # ==================================
        # TOP CARDS
        # ==================================

        cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        cards_frame.pack(fill="x", padx=30)

        stats = [
            ("Total Listings", "45"),
            ("Pending Review", "142"),
            ("Total Income", "₱56,456"),
            ("Total Expense", "₱26,456")
        ]

        for i, (label, value) in enumerate(stats):

            card = ctk.CTkFrame(
                cards_frame,
                width=250,
                height=110,
                corner_radius=12,
                fg_color=PRIMARY if i == 0 else WHITE,
                border_width=1,
                border_color=BORDER
            )

            card.pack(side="left", padx=10)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=label,
                font=("Poppins", 13),
                text_color="white" if i == 0 else GRAY
            ).pack(anchor="w", padx=15, pady=(18, 5))

            ctk.CTkLabel(
                card,
                text=value,
                font=("Poppins", 22, "bold"),
                text_color="white" if i == 0 else TEXT
            ).pack(anchor="w", padx=15)

        # ==================================
        # LOWER SECTION
        # ==================================

        content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        content.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        # --------------------------
        # PAYMENT HISTORY
        # --------------------------

        payment_frame = ctk.CTkFrame(
            content,
            fg_color=WHITE,
            corner_radius=12,
            border_width=1,
            border_color=BORDER
        )

        payment_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        ctk.CTkLabel(
            payment_frame,
            text="Payment History",
            font=("Poppins", 18, "bold")
        ).pack(anchor="w", padx=20, pady=15)

        payments = [
            ("September 2023", "₱4,568", "Paid"),
            ("October 2023", "₱4,568", "Paid"),
            ("November 2023", "₱4,568", "Paid"),
            ("December 2023", "₱4,568", "Paid")
        ]

        for date, amount, status in payments:

            row = ctk.CTkFrame(
                payment_frame,
                fg_color="transparent"
            )
            row.pack(fill="x", padx=20, pady=8)

            ctk.CTkLabel(
                row,
                text=date,
                width=150,
                anchor="w"
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=amount,
                width=120
            ).pack(side="left")

            badge = ctk.CTkLabel(
                row,
                text=status,
                fg_color="#34C759",
                text_color="white",
                corner_radius=8,
                width=70,
                height=28
            )
            badge.pack(side="right")

        # --------------------------
        # MAINTENANCE
        # --------------------------

        maintenance_frame = ctk.CTkFrame(
            content,
            fg_color=WHITE,
            corner_radius=12,
            border_width=1,
            border_color=BORDER
        )

        maintenance_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        ctk.CTkLabel(
            maintenance_frame,
            text="Maintenance Status",
            font=("Poppins", 18, "bold")
        ).pack(anchor="w", padx=20, pady=15)

        requests = [
            ("Request #001", "In Progress"),
            ("Request #002", "Completed"),
            ("Request #003", "Pending"),
            ("Request #004", "Completed")
        ]

        for req, status in requests:

            row = ctk.CTkFrame(
                maintenance_frame,
                fg_color="transparent"
            )

            row.pack(fill="x", padx=20, pady=8)

            ctk.CTkLabel(
                row,
                text=req
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=status
            ).pack(side="right")

        ctk.CTkLabel(
            maintenance_frame,
            text="🔧",
            font=("Arial", 80)
        ).pack(expand=True)


# ======================================================
# MAIN APP
# ======================================================

class PropertyManagementSystem(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Property Management System")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color=BG)

        # Sidebar

        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color=WHITE,
            corner_radius=0
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        # Main Content

        self.main = ctk.CTkFrame(
            self,
            fg_color=BG
        )

        self.main.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.pages = {}

        self.build_sidebar()

    def build_sidebar(self):

        logo = ctk.CTkLabel(
            self.sidebar,
            text="🏠 BHF",
            font=("Poppins", 22, "bold"),
            text_color=PRIMARY
        )

        logo.pack(pady=(30, 30))

        self.menu_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        self.menu_frame.pack(fill="x")

        # Buttons added in Part 4

        self.logout_btn = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="transparent",
            text_color=TEXT,
            hover_color="#F0F0F0",
            command=self.logout
        )

        self.logout_btn.pack(
            side="bottom",
            pady=25
        )

    def logout(self):

        if messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?"
        ):
            self.destroy()
# ======================================================
# TENANTS PAGE
# ======================================================

class TenantsPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent, fg_color=BG)

        self.tenants = [
            ("JD", "Juan Dela Cruz", "A-101", "09123456789", "Jan 15, 2025", "Paid"),
            ("MS", "Maria Santos", "B-204", "09178901234", "Mar 10, 2025", "Paid"),
            ("PR", "Pedro Reyes", "C-301", "09152223344", "Feb 05, 2025", "Overdue"),
            ("LM", "Liza Morales", "A-202", "09165556677", "May 20, 2025", "Pending")
        ]

        self.build_ui()

    # ==================================================
    # UI
    # ==================================================

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="TENANTS",
            font=("Poppins", 26, "bold")
        )

        title.pack(anchor="w", padx=30, pady=(20, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Manage all tenant records and payment status",
            font=("Poppins", 12),
            text_color=GRAY
        )

        subtitle.pack(anchor="w", padx=30)

        # ----------------------------
        # SEARCH BAR
        # ----------------------------

        topbar = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        topbar.pack(fill="x", padx=30, pady=20)

        self.search_entry = ctk.CTkEntry(
            topbar,
            width=700,
            height=42,
            placeholder_text="Search tenant..."
        )

        self.search_entry.pack(
            side="left",
            padx=(0, 10)
        )

        search_btn = ctk.CTkButton(
            topbar,
            text="Search",
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            width=100,
            command=self.search_tenant
        )

        search_btn.pack(side="left")

        add_btn = ctk.CTkButton(
            topbar,
            text="+ Add Tenant",
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            width=150,
            command=self.open_add_tenant
        )

        add_btn.pack(side="right")

        # ----------------------------
        # TABLE
        # ----------------------------

        self.table = ctk.CTkScrollableFrame(
            self,
            fg_color=WHITE,
            corner_radius=12,
            border_width=1,
            border_color=BORDER
        )

        self.table.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 20)
        )

        self.refresh_table()

    # ==================================================
    # REFRESH TABLE
    # ==================================================

    def refresh_table(self):

        for widget in self.table.winfo_children():
            widget.destroy()

        headers = ctk.CTkFrame(
            self.table,
            fg_color="transparent"
        )

        headers.pack(fill="x", pady=(5, 10))

        header_titles = [
            "Tenant",
            "Unit",
            "Contact",
            "Move-in Date",
            "Status",
            "Action"
        ]

        widths = [250, 120, 180, 180, 120, 120]

        for text, width in zip(header_titles, widths):

            ctk.CTkLabel(
                headers,
                text=text,
                width=width,
                anchor="w",
                font=("Poppins", 13, "bold")
            ).pack(side="left")

        # ----------------------------------

        for tenant in self.tenants:

            initials, name, unit, contact, move_in, status = tenant

            row = ctk.CTkFrame(
                self.table,
                fg_color="transparent",
                height=70
            )

            row.pack(fill="x", pady=5)

            # Tenant Section

            tenant_frame = ctk.CTkFrame(
                row,
                fg_color="transparent",
                width=250
            )

            tenant_frame.pack(side="left")

            create_avatar(
                tenant_frame,
                initials
            ).pack(side="left", padx=(0, 10))

            ctk.CTkLabel(
                tenant_frame,
                text=name,
                font=("Poppins", 12)
            ).pack(side="left")

            # Unit

            ctk.CTkLabel(
                row,
                text=unit,
                width=120
            ).pack(side="left")

            # Contact

            ctk.CTkLabel(
                row,
                text=contact,
                width=180
            ).pack(side="left")

            # Date

            ctk.CTkLabel(
                row,
                text=move_in,
                width=180
            ).pack(side="left")

            # Status

            colors = {
                "Paid": "#34C759",
                "Pending": "#FFCC00",
                "Overdue": "#FF3B30"
            }

            badge = ctk.CTkLabel(
                row,
                text=status,
                width=100,
                height=30,
                corner_radius=8,
                fg_color=colors[status],
                text_color="white"
            )

            badge.pack(side="left", padx=5)

            # View Button

            view_btn = ctk.CTkButton(
                row,
                text="View",
                width=70,
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
                command=lambda n=name: self.view_tenant(n)
            )

            view_btn.pack(side="right")

    # ==================================================
    # SEARCH
    # ==================================================

    def search_tenant(self):

        query = self.search_entry.get().lower()

        if not query:

            self.refresh_table()
            return

        for widget in self.table.winfo_children():
            widget.destroy()

        for tenant in self.tenants:

            if query in tenant[1].lower():

                row = ctk.CTkFrame(
                    self.table,
                    fg_color="transparent"
                )

                row.pack(fill="x", pady=5)

                ctk.CTkLabel(
                    row,
                    text=tenant[1]
                ).pack(side="left", padx=20)

    # ==================================================
    # VIEW TENANT
    # ==================================================

    def view_tenant(self, name):

        messagebox.showinfo(
            "Tenant Information",
            f"Viewing profile of:\n\n{name}"
        )

    # ==================================================
    # ADD TENANT POPUP
    # ==================================================

    def open_add_tenant(self):

        popup = ctk.CTkToplevel(self)

        popup.title("Add Tenant")
        popup.geometry("450x500")
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text="Add New Tenant",
            font=("Poppins", 20, "bold")
        ).pack(pady=20)

        name_entry = ctk.CTkEntry(
            popup,
            placeholder_text="Full Name"
        )
        name_entry.pack(fill="x", padx=25, pady=10)

        unit_entry = ctk.CTkEntry(
            popup,
            placeholder_text="Unit Number"
        )
        unit_entry.pack(fill="x", padx=25, pady=10)

        contact_entry = ctk.CTkEntry(
            popup,
            placeholder_text="Contact Number"
        )
        contact_entry.pack(fill="x", padx=25, pady=10)

        movein_entry = ctk.CTkEntry(
            popup,
            placeholder_text="Move-in Date"
        )
        movein_entry.pack(fill="x", padx=25, pady=10)

        status_menu = ctk.CTkOptionMenu(
            popup,
            values=[
                "Paid",
                "Pending",
                "Overdue"
            ]
        )

        status_menu.pack(
            fill="x",
            padx=25,
            pady=10
        )

        def save_tenant():

            name = name_entry.get()

            if not name:
                return

            initials = ""

            words = name.split()

            for word in words[:2]:
                initials += word[0]

            initials = initials.upper()

            self.tenants.append(
                (
                    initials,
                    name,
                    unit_entry.get(),
                    contact_entry.get(),
                    movein_entry.get(),
                    status_menu.get()
                )
            )

            self.refresh_table()

            popup.destroy()

        save_btn = ctk.CTkButton(
            popup,
            text="Save Tenant",
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=save_tenant
        )

        save_btn.pack(
            pady=25
        )
# ======================================================
# MESSAGES PAGE
# ======================================================

class MessagePage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent, fg_color=BG)

        self.contacts = [
            ("JD", "Jhay Del Socorro", "Tenant"),
            ("MS", "Maria Santos", "Tenant"),
            ("PR", "Pedro Reyes", "Tenant"),
            ("LM", "Liza Morales", "Tenant")
        ]

        self.build_ui()

    # ==================================================
    # UI
    # ==================================================

    def build_ui(self):

        # ----------------------------------
        # TITLE
        # ----------------------------------

        title = ctk.CTkLabel(
            self,
            text="MESSAGES",
            font=("Poppins", 26, "bold"),
            text_color=TEXT
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(20, 5)
        )

        subtitle = ctk.CTkLabel(
            self,
            text="Communicate with your tenants",
            font=("Poppins", 12),
            text_color=GRAY
        )

        subtitle.pack(
            anchor="w",
            padx=30
        )

        # ----------------------------------
        # MAIN CONTAINER
        # ----------------------------------

        container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        # ==================================================
        # LEFT CONTACT PANEL
        # ==================================================

        contacts_frame = ctk.CTkFrame(
            container,
            width=320,
            fg_color=WHITE,
            corner_radius=15,
            border_width=1,
            border_color=BORDER
        )

        contacts_frame.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )

        contacts_frame.pack_propagate(False)

        ctk.CTkLabel(
            contacts_frame,
            text="Contacts",
            font=("Poppins", 18, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=20
        )

        self.selected_contact = "Jhay Del Socorro"

        for initials, name, role in self.contacts:

            card = ctk.CTkButton(
                contacts_frame,
                text="",
                fg_color="transparent",
                hover_color="#F5F5F5",
                height=70,
                corner_radius=10,
                command=lambda n=name: self.select_contact(n)
            )

            card.pack(
                fill="x",
                padx=10,
                pady=5
            )

            avatar = create_avatar(card, initials)

            avatar.place(
                x=15,
                y=15
            )

            name_lbl = ctk.CTkLabel(
                card,
                text=name,
                font=("Poppins", 13, "bold")
            )

            name_lbl.place(
                x=70,
                y=15
            )

            role_lbl = ctk.CTkLabel(
                card,
                text=role,
                text_color=GRAY,
                font=("Poppins", 11)
            )

            role_lbl.place(
                x=70,
                y=40
            )

        # ==================================================
        # CHAT PANEL
        # ==================================================

        self.chat_panel = ctk.CTkFrame(
            container,
            fg_color=WHITE,
            corner_radius=15,
            border_width=1,
            border_color=BORDER
        )

        self.chat_panel.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ----------------------------------
        # CHAT HEADER
        # ----------------------------------

        header = ctk.CTkFrame(
            self.chat_panel,
            fg_color="#FAFAFA",
            height=70,
            corner_radius=0
        )

        header.pack(fill="x")

        header.pack_propagate(False)

        self.header_avatar = create_avatar(
            header,
            "JD"
        )

        self.header_avatar.pack(
            side="left",
            padx=15,
            pady=15
        )

        self.header_name = ctk.CTkLabel(
            header,
            text=self.selected_contact,
            font=("Poppins", 15, "bold")
        )

        self.header_name.pack(
            side="left"
        )

        phone_btn = ctk.CTkButton(
            header,
            text="📞",
            width=40,
            fg_color="transparent",
            text_color=TEXT
        )

        phone_btn.pack(
            side="right",
            padx=10
        )

        dots_btn = ctk.CTkButton(
            header,
            text="⋮",
            width=40,
            fg_color="transparent",
            text_color=TEXT
        )

        dots_btn.pack(
            side="right"
        )

        # ----------------------------------
        # CHAT AREA
        # ----------------------------------

        self.chat_box = ctk.CTkTextbox(
            self.chat_panel,
            fg_color="#FCFCFC",
            border_width=0
        )

        self.chat_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.chat_box.insert(
            "end",
            "Jhay: Good morning!\n\n"
        )

        self.chat_box.insert(
            "end",
            "You: Good morning too.\n\n"
        )

        self.chat_box.configure(
            state="disabled"
        )

        # ----------------------------------
        # MESSAGE INPUT
        # ----------------------------------

        bottom = ctk.CTkFrame(
            self.chat_panel,
            fg_color="transparent"
        )

        bottom.pack(
            fill="x",
            padx=20,
            pady=15
        )

        self.message_entry = ctk.CTkEntry(
            bottom,
            placeholder_text="Type a message..."
        )

        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        send_btn = ctk.CTkButton(
            bottom,
            text="Send",
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            width=100,
            command=self.send_message
        )

        send_btn.pack(
            side="right"
        )

        # ----------------------------------
        # FLOATING ADD BUTTON
        # ----------------------------------

        add_chat_btn = ctk.CTkButton(
            self,
            text="+",
            width=60,
            height=60,
            corner_radius=30,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            font=("Arial", 30, "bold")
        )

        add_chat_btn.place(
            relx=0.95,
            rely=0.90,
            anchor="center"
        )

    # ==================================================
    # SEND MESSAGE
    # ==================================================

    def send_message(self):

        msg = self.message_entry.get().strip()

        if not msg:
            return

        self.chat_box.configure(
            state="normal"
        )

        self.chat_box.insert(
            "end",
            f"You: {msg}\n\n"
        )

        self.chat_box.see("end")

        self.chat_box.configure(
            state="disabled"
        )

        self.message_entry.delete(
            0,
            "end"
        )

    # ==================================================
    # SELECT CONTACT
    # ==================================================

    def select_contact(self, name):

        self.selected_contact = name

        self.header_name.configure(
            text=name
        )

        self.chat_box.configure(
            state="normal"
        )

        self.chat_box.delete(
            "1.0",
            "end"
        )

        self.chat_box.insert(
            "end",
            f"{name}: Hello!\n\n"
        )

        self.chat_box.insert(
            "end",
            "You: Hi there.\n\n"
        )

        self.chat_box.configure(
            state="disabled"
        )

class PropertyManagementSystem(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Property Management System")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color=BG)

        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color=WHITE,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Main container
        self.main = ctk.CTkFrame(
            self,
            fg_color=BG
        )
        self.main.pack(side="left", fill="both", expand=True)

        # Pages storage
        self.pages = {}

        self.build_sidebar()
        self.register_pages()
        self.show_page("Dashboard")

    # ==================================================
    # SIDEBAR
    # ==================================================

    def build_sidebar(self):

        logo = ctk.CTkLabel(
            self.sidebar,
            text="🏠 BHF SYSTEM",
            font=("Poppins", 20, "bold"),
            text_color=PRIMARY
        )
        logo.pack(pady=(30, 20))

        self.menu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.menu_frame.pack(fill="x", pady=10)

        # Navigation buttons
        self.add_nav_button("Dashboard", "Dashboard")
        self.add_nav_button("Tenants", "Tenants")
        self.add_nav_button("Messages", "Messages")

        # Logout button (BOTTOM)
        self.logout_btn = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="transparent",
            text_color=TEXT,
            hover_color="#F0F0F0",
            command=self.logout
        )
        self.logout_btn.pack(side="bottom", pady=25)

    # helper for nav buttons
    def add_nav_button(self, text, page_name):

        btn = ctk.CTkButton(
            self.menu_frame,
            text=text,
            fg_color="transparent",
            text_color=TEXT,
            hover_color="#F0F0F0",
            anchor="w",
            command=lambda: self.show_page(page_name)
        )
        btn.pack(fill="x", padx=15, pady=5)

    # ==================================================
    # PAGE REGISTRATION
    # ==================================================

    def register_pages(self):

        self.pages["Dashboard"] = DashboardPage(self.main)
        self.pages["Tenants"] = TenantsPage(self.main)
        self.pages["Messages"] = MessagePage(self.main)

    # ==================================================
    # PAGE SWITCHING
    # ==================================================

    def show_page(self, page_name):

        # hide all pages
        for page in self.pages.values():
            page.pack_forget()

        # show selected page
        page = self.pages[page_name]
        page.pack(fill="both", expand=True)

    # ==================================================
    # LOGOUT
    # ==================================================

    def logout(self):

        if messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?"
        ):
            self.destroy()


# ======================================================
# RUN APP
# ======================================================

if __name__ == "__main__":

    app = PropertyManagementSystem()
    app.mainloop()