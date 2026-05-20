import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image, ImageTk
import os

ctk.set_appearance_mode("Light")

class BoardingHouseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Boarding House Finder")
        
        # 1. The New "Sleek Card" Dimensions
        self.geometry("450x600")
        self.resizable(False, False)

        # --- FONT SETUP ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_files = [
            os.path.join(current_dir, "assets", "Novecentosanswide-Light.otf"),
            os.path.join(current_dir, "assets", "Novecentosanswide-Normal.otf")
        ]

        for file_path in font_files:
            if os.path.exists(file_path):
                try:
                    ctk.FontManager.load_font(file_path)
                except Exception as e:
                    print(f"Warning: Could not load {file_path}. Error: {e}")

        self.logo = ctk.CTkImage(Image.open("assets/logo.png"), size=(140, 32))

        self.title_font = ctk.CTkFont(family="Novecento sans wide Normal", size=30, weight="bold")
        self.body_font = ctk.CTkFont(family="Novecento sans wide Normal", size=18)
        self.body_bold_font = ctk.CTkFont(family="Novecento sans wide Normal", size=24, weight="bold")
        self.body_light_font = ctk.CTkFont(family="Novecento sans wide Normal", size=16)

        # --- COLORS ---
        self.primary_color = "#D6B588"
        self.entry_border = "#E0E0E0" 
        self.hover_color = "#C5A376"
        self.text_color = "#3E362A"
        self.error_red = "#D9534F"
        
        # Pure White Background
        self.configure(fg_color="#FFFFFF")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)

        self.show_login_page()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_page(self):
        self.clear_container()

        # Exact Logo Dimensions (204x32)
        logo_label = ctk.CTkLabel(self.container,
                                  text=None,
                                  image=self.logo,
                                  width=140,
                                  height=32
                                  )
        logo_label.pack(pady=(15, 15))

        welcome_label = ctk.CTkLabel(self.container,
                                    text="Welcome To",
                                    width=121,
                                    height=5,
                                    font=self.body_light_font,
                                    text_color="#4D4D4D"
                                    )
        welcome_label.pack(pady=(0, 10))

        title_label = ctk.CTkLabel(self.container,
                                   text="Boarding House Finder",
                                   width=273,
                                   height=20,
                                   font=self.body_bold_font,
                                   text_color="#4D4D4D"
                                   )
        title_label.pack(pady=(0, 10))

        notes_label = ctk.CTkLabel(self.container,
                                   text="Please Login your Login",
                                   width=213,
                                   height=5,
                                   font=self.body_light_font,
                                   text_color="#4D4D4D"
                                   )
        notes_label.pack(pady=(0, 7))

        # Adjusted Email Entry (Width changed to 320 to fit the 450 window perfectly)  
        self.email_entry = ctk.CTkEntry(self.container,
                                        placeholder_text="Email Address",
                                        width=320, 
                                        height=45,
                                        font=self.body_font,
                                        fg_color="#F8F8F8",
                                        border_color=self.entry_border,
                                        border_width=1,
                                        text_color=self.text_color)
        self.email_entry.pack(pady=(0, 15))

        # Adjusted Password Entry
        self.password_entry = ctk.CTkEntry(self.container,
                                           placeholder_text="Password",
                                           width=320,
                                           height=45,
                                           show="*",
                                           font=self.body_font,
                                           fg_color="#F8F8F8",
                                           border_color=self.entry_border,
                                           border_width=1,
                                           text_color=self.text_color)
        self.password_entry.pack(pady=(0, 10))

        # Error Label
        self.error_label = ctk.CTkLabel(self.container,
                                        text="",
                                        text_color=self.error_red,
                                        font=self.body_light_font)
        self.error_label.pack(pady=(0, 15))

        # Login Button
        login_btn = ctk.CTkButton(self.container,
                                  text="Log In",
                                  width=320,
                                  height=45,
                                  corner_radius=6,
                                  font=self.body_bold_font,
                                  fg_color=self.primary_color,
                                  hover_color=self.hover_color,
                                  text_color="#FFFFFF", 
                                  command=self.attempt_login)
        login_btn.pack(pady=(0, 20))

    def attempt_login(self):
        # We will connect this to the FastAPI backend soon!
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email and password:
            self.error_label.configure(text="Connecting to database...")
        else:
            self.error_label.configure(text="Please fill in both fields.")

if __name__ == "__main__":
    app = BoardingHouseApp()
    app.mainloop()