import customtkinter as ctk
from PIL import Image
import os

ctk.set_appearance_mode("Light")

class BoardingHouseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Boarding House Finder")
        self.geometry("600x650")
        self.resizable(False, False)

        # --- Font Setup ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_files = [
            os.path.join(current_dir, "assets", "Novecentosanswide-Light.otf"),
            os.path.join(current_dir, "assets", "Novecentosanswide-Normal.otf"),
            os.path.join(current_dir, "assets", "Poppins-Regular.ttf"),
            os.path.join(current_dir, "assets", "Poppins-Light.ttf")
        ]

        for file_path in font_files:
            if os.path.exists(file_path):
                try:
                    ctk.FontManager.load_font(file_path)
                except Exception as e:
                    print(f"Warning: Could not load {file_path}. Error: {e}")

        self.logo = ctk.CTkImage(Image.open("assets/logo.png"), size=(140, 32))
        raw_google = Image.open("assets/google.png")
        orig_w, orig_h = raw_google.size
        padded_google = Image.new("RGBA", (orig_w + 40, orig_h + 40), (255, 255, 255, 0))
        padded_google.paste(raw_google, (20, 20))
        pad_w, pad_h = padded_google.size
        target_width = 110
        target_height = int((pad_h / pad_w) * target_width)
        self.google_icon = ctk.CTkImage(padded_google, size=(target_width, target_height))

        self.title_font = ctk.CTkFont(family="Novecento sans wide Normal", size=32, weight="bold")
        self.alt_title_font = ctk.CTkFont(family="Novecento sans wide Normal", size=24, weight="bold")
        self.body_bold_font = ctk.CTkFont(family="Novecento sans wide Normal", size=20, weight="bold")
        
        self.body_paragraph_font = ctk.CTkFont(family="Poppins", size=15, weight="normal")
        self.body_light_font = ctk.CTkFont(family="Poppins Light", size=16, weight="normal") 

        self.primary_color = "#AC7F5E"
        self.entry_border = "#E0E0E0" 
        self.hover_color = "#C5A376"
        self.text_color = "#3E362A"
        self.error_red = "#D9534F"
        
        self.configure(fg_color="#FFFFFF")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)
        
        # --- Notification State Variables  ---
        self.current_toast = None
        self.toast_timer = None

        self.show_login_page()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
    
    def show_toast(self, message, is_error=True):
        """Displays a sleek notification and prevents spam-clicking bugs."""
        
        if self.toast_timer is not None:
            self.after_cancel(self.toast_timer)
            self.toast_timer = None
            
        if self.current_toast is not None:
            try:
                self.current_toast.destroy()
            except:
                pass

        bg_color = self.error_red if is_error else self.primary_color
        
        self.current_toast = ctk.CTkFrame(self, 
                                          fg_color=bg_color, 
                                          corner_radius=20, 
                                          width=350,
                                          height=40)
        self.current_toast.place(relx=0.5, rely=-0.1, anchor="center") 
        self.current_toast.pack_propagate(False) 

        msg_label = ctk.CTkLabel(self.current_toast, 
                                 text=message, 
                                 text_color="#FFFFFF", 
                                 font=self.body_paragraph_font)
        msg_label.place(relx=0.5, rely=0.5, anchor="center")

        # 5. Animation Logic
        def animate_in(current_rely=-0.1):
            if self.current_toast is None or not self.current_toast.winfo_exists(): return
            
            if current_rely < 0.06:
                self.current_toast.place(relx=0.5, rely=current_rely, anchor="center")
                self.after(10, lambda: animate_in(current_rely + 0.01))
            else:
                self.toast_timer = self.after(2500, animate_out) 

        def animate_out(current_rely=0.06):
            if self.current_toast is None or not self.current_toast.winfo_exists(): return
            
            if current_rely > -0.1:
                self.current_toast.place(relx=0.5, rely=current_rely, anchor="center")
                self.after(10, lambda: animate_out(current_rely - 0.01))
            else:
                self.current_toast.destroy()
                self.current_toast = None

        animate_in()

    def show_login_page(self):
        self.clear_container()
        
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=40, fill="both", expand=True)

        # Logo
        logo_label = ctk.CTkLabel(self.form_container,
                                  text=None,
                                  image=self.logo,
                                  width=140,
                                  height=32
                                  )
        logo_label.pack(pady=(5, 15))

        welcome_label = ctk.CTkLabel(self.form_container,
                                     text="WELCOME TO",
                                     width=121,
                                     height=5,
                                     font=self.body_bold_font,
                                     text_color="#4D4D4D"
                                    )
        welcome_label.pack(pady=(0, 7))

        title_label = ctk.CTkLabel(self.form_container, 
                                   text="BOARDING HOUSE FINDER", 
                                   width=273, 
                                   height=20,
                                   font=self.alt_title_font, 
                                   text_color="#4D4D4D"
                                   )
        title_label.pack(pady=(0, 10))

        notes_label = ctk.CTkLabel(self.form_container, 
                                   text="Please enter your login details", 
                                   width=213, 
                                   height=5,
                                   font=self.body_paragraph_font, 
                                   text_color="#4D4D4D"
                                   )
        notes_label.pack(pady=(0, 7))

        # Email Row
        email_frame = ctk.CTkFrame(self.form_container, 
                                   fg_color="transparent")
        email_frame.pack(pady=(0, 15))

        self.email_label = ctk.CTkLabel(email_frame, 
                                        text="Email", 
                                        font=self.body_light_font, 
                                        text_color=self.text_color
                                        )
        self.email_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        email_bg_frame = ctk.CTkFrame(email_frame, 
                                      width=400, 
                                      height=40, 
                                      fg_color="#F8F8F8",
                                      border_color=self.entry_border, 
                                      border_width=1, 
                                      corner_radius=6
                                      )
        email_bg_frame.pack()
        email_bg_frame.pack_propagate(False) 

        self.email_entry = ctk.CTkEntry(email_bg_frame, 
                                        placeholder_text="example@gmail.com", 
                                        height=30,
                                        font=self.body_light_font, 
                                        fg_color="transparent", 
                                        border_width=0,
                                        text_color=self.text_color
                                        )
        self.email_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        
        # Password Row
        password_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        password_frame.pack(pady=(0, 15))

        self.password_label = ctk.CTkLabel(password_frame, 
                                           text="Password", 
                                           font=self.body_light_font, 
                                           text_color=self.text_color
                                           )
        self.password_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        password_bg_frame = ctk.CTkFrame(password_frame, 
                                         width=400, 
                                         height=40, 
                                         fg_color="#F8F8F8",
                                         border_color=self.entry_border, 
                                         border_width=1, 
                                         corner_radius=6
                                         )
        password_bg_frame.pack()
        password_bg_frame.pack_propagate(False)

        self.password_entry = ctk.CTkEntry(password_bg_frame, 
                                           placeholder_text="Password", 
                                           width=400, height=30,
                                           show="•", 
                                           font=self.body_light_font, 
                                           fg_color="transparent",
                                           border_width=0, 
                                           text_color=self.text_color
                                           )
        self.password_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        actions_frame = ctk.CTkFrame(password_frame, fg_color="transparent", width=400, height=30)
        actions_frame.pack(fill="x", pady=(10, 0))

        # 2. Pack the checkbox to the LEFT
        self.remember_checkbox = ctk.CTkCheckBox(actions_frame,
                                                text="Remember me",
                                                font=self.body_paragraph_font,
                                                text_color=self.text_color,
                                                fg_color=self.primary_color,
                                                hover_color=self.hover_color,
                                                border_color=self.entry_border,
                                                border_width=2,
                                                checkbox_height=20,
                                                checkbox_width=20)
        self.remember_checkbox.pack(side="left")

        self.forgot_pwd_btn = ctk.CTkButton(actions_frame,
                                            text="Forgot Password?",
                                            font=self.body_paragraph_font,
                                            text_color="#AC7F5E", 
                                            fg_color="transparent",        
                                            hover_color="#F8F8F8",        
                                            width=0,                       
                                            height=20,
                                            command=self.forgot_password)
        self.forgot_pwd_btn.pack(side="right")

        # Login Action
        login_btn = ctk.CTkButton(self.form_container, 
                                  text="LOG IN", 
                                  width=400, 
                                  height=45, 
                                  corner_radius=6,
                                  font=self.body_bold_font, 
                                  fg_color="#AC7F5E", 
                                  hover_color=self.hover_color,
                                  text_color="#FFFFFF", 
                                  command=self.attempt_login
                                  )
        login_btn.pack(pady=(10, 10)) 

        self.google_label = ctk.CTkLabel(self.form_container,
                                         text="Or Continue With",
                                         width=153,
                                         height=20,
                                         font=self.body_paragraph_font,
                                         text_color=self.text_color
                                         )
        self.google_label.pack(pady=(15, 0))

        self.google_btn = ctk.CTkLabel(self.form_container,
                                       text="", 
                                       image=self.google_icon,
                                       cursor="hand2"
                                       )
        self.google_btn.pack(pady=(0, 0))
        self.google_btn.bind("<Button-1>", lambda event: self.google_login())

        register_frame = ctk.CTkFrame(self.form_container,
                                      fg_color="transparent"
                                      )
        register_frame.pack(pady=(0, 0))

        self.new_member_label = ctk.CTkLabel(register_frame,
                                             text="New member here?",
                                             font=self.body_paragraph_font,
                                             text_color=self.text_color,
                                             )
        self.new_member_label.pack(side="left", padx=(0, 5))

        self.register_btn = ctk.CTkButton(register_frame,
                                          text="Register Now",
                                          font=ctk.CTkFont(family="Poppins", size=15, weight="bold"),
                                          text_color=self.primary_color,
                                          fg_color="transparent",
                                          hover_color="#F8F8F8",
                                          width=0,
                                          height=20,
                                          command=self.show_register_page
                                          )
        self.register_btn.pack(side="left")




    def attempt_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email and password:
            self.show_toast("BEEEEEEP", is_error=False)
        else:
            self.show_toast("Please fill in both fields.", is_error=True)

    def forgot_password(self):
        self.show_toast("BOOOOOOOOP", is_error=False)

    def google_login(self):
        self.show_toast("BEEEEP BOOOOOP", is_error=False)
    
    def show_register_page(self):
        self.show_toast("asdjladasd", is_error=False)

if __name__ == "__main__":
    app = BoardingHouseApp()
    app.mainloop()