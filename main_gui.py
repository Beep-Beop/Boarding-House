import customtkinter as ctk
import tkinter as tk
import requests
import os

ctk.set_appearance_mode("Light")

class BoardingHouseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Boarding House Finder")
        self.geometry("800x600")

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
            else:
                print(f"Warning: Missing font file - {file_path}")

        self.title_font = ctk.CTkFont(family="Novecento sans wide Normal", size=28, weight="bold")
        self.body_font = ctk.CTkFont(family="Novecento sans wide Normal", size=14)
        self.body_bold_font = ctk.CTkFont(family="Novecento sans wide Normal", size=14, weight="bold")
        self.body_light_font = ctk.CTkFont(family="Novecento sans wide Light", size=12, weight="normal")

        self.primary_color = "#D6B588"
        self.secondary_color = "#F6F1E8"
        self.bg_color = self.secondary_color
        self.card_color = "#FFFFFF"
        self.entry_border = self.primary_color
        self.hover_color = "#C5A376"
        self.text_color = "#3E362A"
        self.error_red = "#D9534F"

        self.configure(fg_color=self.bg_color)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)

        self.show_login_page()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_page(self):
        self.clear_container()
        

        logo_label = ctk.CTkLabel(self.container,
                                  text="[Wala Pang Logo]",
                                  text_color=self.text_color,
                                  font=self.body_light_font)
        logo_label.pack(pady=(40, 20), padx=40)

        title_label = ctk.CTkLabel(self.container,
                                   text="Boarding House Finder",
                                   text_color=self.text_color,
                                   font=self.title_font)
        title_label.pack(pady=(10, 30), padx=40)

        self.email_entry = ctk.CTkEntry(self.container,
                                        placeholder_text="Email",
                                        width=519,
                                        height=50,
                                        font=self.body_font,
                                        fg_color="#FFFFFF",
                                        border_color=self.entry_border,
                                        text_color=self.text_color)
        self.email_entry.pack(pady=12, padx=50)

        self.password_entry = ctk.CTkEntry(self.container,
                                           placeholder_text="Password",
                                           width=519,
                                           height=50,
                                           show="*",
                                           font=self.body_font,
                                           fg_color="#FFFFFF",
                                           border_color=self.entry_border,
                                           text_color=self.text_color)
        self.password_entry.pack(pady=12, padx=50)

        self.error_label = ctk.CTkLabel(self.container,
                                        text="",
                                        text_color=self.error_red,
                                        font=self.body_light_font)
        self.error_label.pack(pady=(0, 5))

        login_btn = ctk.CTkButton(self.container,
                                  text="Log In",
                                  width=519,
                                  height=50,
                                  corner_radius=6,
                                  font=self.body_bold_font,
                                  fg_color=self.primary_color,
                                  hover_color=self.hover_color,
                                  text_color="#3E362A",
                                  command=self.attempt_login)
        login_btn.pack(pady=(10, 40), padx=50)

    def attempt_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email and password:
            self.error_label.configure(text="")
            if True:
                self.show_dashboard_page()
        else:
            self.error_label.configure(text="Please fill in both email and password.")

    def show_dashboard_page(self):
        self.clear_container()

        welcome = ctk.CTkLabel(self.container,
                               text="Welcome",
                               text_color=self.text_color,
                               font=self.title_font)
        welcome.pack(pady=100)

        btn_logout = ctk.CTkButton(self.container,
                                   text="Log Out",
                                   command=self.show_login_page,
                                   fg_color="#A94442",
                                   hover_color="#8F3937",
                                   font=self.body_bold_font)
        btn_logout.pack()


if __name__ == "__main__":
    app = BoardingHouseApp()
    app.mainloop()