import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

PRIMARY = "#AC7F5E"
WHITE = "#FFFFFF"
BG = "#F5F5F5"
TEXT = "#1A1A1A"
GRAY = "#666666"
BORDER = "#E6E6E6"

app = ctk.CTk()
app.title("Property Management System")
app.geometry("1200x700")
app.configure(fg_color=BG)

sidebar = ctk.CTkFrame(
    app,
    width=220,
    corner_radius=0,
    fg_color=WHITE
)
sidebar.pack(side="left", fill="y")

logo = ctk.CTkLabel(
    sidebar,
    text="🏠 BHF",
    font=("Poppins", 20, "bold"),
    text_color=PRIMARY
)
logo.pack(pady=(30, 30))

menu_items = [
    "Dashboard",
    "Tenants",
    "Message",
    "Favorites"
]

for item in menu_items:
    btn = ctk.CTkButton(
        sidebar,
        text=item,
        width=180,
        height=40,
        fg_color=PRIMARY if item == "Dashboard" else "transparent",
        text_color="white" if item == "Dashboard" else TEXT,
        hover_color="#BE955A",
        corner_radius=8
    )
    btn.pack(pady=8)

# -----------------------------
# MAIN CONTENT
# -----------------------------
main = ctk.CTkFrame(
    app,
    fg_color=BG,
    corner_radius=0
)
main.pack(fill="both", expand=True)

title = ctk.CTkLabel(
    main,
    text="DASHBOARD",
    font=("Poppins", 24, "bold"),
    text_color=TEXT
)
title.pack(anchor="w", padx=30, pady=20)

# -----------------------------
# TOP CARDS
# -----------------------------
cards_frame = ctk.CTkFrame(
    main,
    fg_color="transparent"
)
cards_frame.pack(fill="x", padx=30)

stats = [
    ("Total Listings", "45"),
    ("Pending Review", "142"),
    ("Total Income", "$56,456.00"),
    ("Total Expense", "$26,456.00")
]

for i, (label, value) in enumerate(stats):
    card = ctk.CTkFrame(
        cards_frame,
        width=220,
        height=100,
        fg_color=PRIMARY if i == 0 else WHITE,
        border_width=1,
        border_color=BORDER,
        corner_radius=10
    )
    card.pack(side="left", padx=10)

    ctk.CTkLabel(
        card,
        text=label,
        font=("Poppins", 12),
        text_color="white" if i == 0 else GRAY
    ).pack(anchor="w", padx=15, pady=(15, 5))

    ctk.CTkLabel(
        card,
        text=value,
        font=("Poppins", 20, "bold"),
        text_color="white" if i == 0 else TEXT
    ).pack(anchor="w", padx=15)

# -----------------------------
# BOTTOM SECTION
# -----------------------------
content = ctk.CTkFrame(
    main,
    fg_color="transparent"
)
content.pack(fill="both", expand=True, padx=30, pady=20)

# Payment History
payment_frame = ctk.CTkFrame(
    content,
    fg_color=WHITE,
    border_width=1,
    border_color=BORDER
)
payment_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

ctk.CTkLabel(
    payment_frame,
    text="Payment History",
    font=("Poppins", 16, "bold")
).pack(anchor="w", padx=20, pady=15)

payments = [
    ("September 2023", "$4568.00", "Paid"),
    ("October 2023", "$4568.00", "Paid"),
    ("November 2023", "$4568.00", "Paid")
]

for date, amount, status in payments:
    row = ctk.CTkFrame(payment_frame, fg_color="transparent")
    row.pack(fill="x", padx=20, pady=5)

    ctk.CTkLabel(row, text=date).pack(side="left")
    ctk.CTkLabel(row, text=amount).pack(side="left", padx=50)
    ctk.CTkLabel(row, text=status).pack(side="right")

# Maintenance
maintenance_frame = ctk.CTkFrame(
    content,
    fg_color=WHITE,
    border_width=1,
    border_color=BORDER
)
maintenance_frame.pack(side="left", fill="both", expand=True)

ctk.CTkLabel(
    maintenance_frame,
    text="Maintenance Status",
    font=("Poppins", 16, "bold")
).pack(anchor="w", padx=20, pady=15)

requests = [
    ("Request #001", "In Progress"),
    ("Request #002", "Completed"),
    ("Request #003", "Pending")
]

for req, status in requests:
    row = ctk.CTkFrame(maintenance_frame, fg_color="transparent")
    row.pack(fill="x", padx=20, pady=5)

    ctk.CTkLabel(row, text=req).pack(side="left")
    ctk.CTkLabel(row, text=status).pack(side="right")

ctk.CTkLabel(
    maintenance_frame,
    text="🔧",
    font=("Arial", 70)
).pack(expand=True)

app.mainloop()