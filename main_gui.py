import customtkinter as ctk
from PIL import Image
import os
import requests

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

        self.bk_btn = ctk.CTkImage(Image.open("assets/bk_btn.png"), size=(80, 60))
        raw_bk_btn = Image.open("assets/bk_btn.png")
        bk_orig_w, bk_orig_h = raw_bk_btn.size
        padded_bk_btn = Image.new("RGBA", (bk_orig_w + 40, bk_orig_h + 40), (255, 255, 255, 0))
        padded_bk_btn.paste(raw_bk_btn, (20, 20))
        bk_btn_pad_w, bk_btn_pad_h = padded_bk_btn.size
        target_width_btn = 70
        target_height_btn = int((bk_btn_pad_h / bk_btn_pad_w) * target_width_btn)
        self.bk_btn_icon = ctk.CTkImage(padded_bk_btn, size=(target_width_btn, target_height_btn))

        self.bk_btn_hvr = ctk.CTkImage(Image.open("assets/bk_btn_hvr.png"), size=(80, 60))
        raw_bk_btn_hvr = Image.open("assets/bk_btn_hvr.png")
        bk_hvr_orig_w, bk_hvr_orig_h = raw_bk_btn_hvr.size
        padded_bk_btn_hvr = Image.new("RGBA", (bk_hvr_orig_w + 40, bk_hvr_orig_h + 40), (255, 255, 255, 0))
        padded_bk_btn_hvr.paste(raw_bk_btn_hvr, (20, 20))
        bk_btn_hvr_pad_w, bk_btn_hvr_pad_h = padded_bk_btn_hvr.size
        target_width_hvr = 70
        target_height_hvr = int((bk_btn_hvr_pad_h / bk_btn_hvr_pad_w) * target_width_hvr)
        self.bk_btn_hvr_icon = ctk.CTkImage(padded_bk_btn_hvr, size=(target_width_hvr, target_height_hvr))

        self.title_font = ctk.CTkFont(family="Novecento sans wide Normal", size=32, weight="bold")
        self.alt_title_font = ctk.CTkFont(family="Novecento sans wide Normal", size=24, weight="bold")
        self.body_bold_font = ctk.CTkFont(family="Novecento sans wide Normal", size=20, weight="bold")
        
        self.body_paragraph_font = ctk.CTkFont(family="Poppins", size=15, weight="normal")
        self.body_light_font = ctk.CTkFont(family="Poppins Light", size=16, weight="normal") 

        self.primary_color = "#AC7F5E"
        self.entry_border = "#E0E0E0" 
        self.hover_color = "#C5A376"
        self.hover_color_text = "#E2E2E2"
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
                                          corner_radius=6, 
                                          width=350,
                                          height=40)
        self.current_toast.place(relx=0.5, rely=-0.1, anchor="center") 
        self.current_toast.pack_propagate(False) 

        msg_label = ctk.CTkLabel(self.current_toast, 
                                 text=message, 
                                 text_color="#FFFFFF", 
                                 font=self.body_paragraph_font)
        msg_label.place(relx=0.5, rely=0.5, anchor="center")

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
                                   fg_color="transparent"
                                   )
        email_frame.pack(pady=(0, 15))

        self.email_label = ctk.CTkLabel(email_frame, 
                                        text="Email", 
                                        font=self.body_light_font, 
                                        text_color=self.text_color
                                        )
        self.email_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        # THE "FAKE" ENTRY (Visual box user sees)
        email_fake_entry = ctk.CTkFrame(email_frame, 
                                      width=400, 
                                      height=40, 
                                      fg_color="#F8F8F8",
                                      border_color=self.entry_border, 
                                      border_width=1, 
                                      corner_radius=6
                                      )
        email_fake_entry.pack()
        email_fake_entry.pack_propagate(False) 

        # THE "REAL" ENTRY (Where user types, tightly wrapped & centered)
        self.email_entry = ctk.CTkEntry(email_fake_entry, 
                                        placeholder_text="example@gmail.com", 
                                        height=24, # Tight wrap around text
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

        # THE "FAKE" ENTRY
        password_fake_entry = ctk.CTkFrame(password_frame, 
                                         width=400, 
                                         height=40, 
                                         fg_color="#F8F8F8",
                                         border_color=self.entry_border, 
                                         border_width=1, 
                                         corner_radius=6
                                         )
        password_fake_entry.pack()
        password_fake_entry.pack_propagate(False)

        # THE "REAL" ENTRY
        self.password_entry = ctk.CTkEntry(password_fake_entry, 
                                           placeholder_text="Password", 
                                           height=24, # Tight wrap around text
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
                                            hover_color=self.hover_color_text,     
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
                                          hover_color=self.hover_color_text,
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
        self.clear_container()

        # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        self.bk_btn_frame = ctk.CTkFrame(self.form_container,
                                  fg_color="transparent"
                                  )
        self.bk_btn_frame.pack(fill="x", pady=(15, 0))


        self.back_btn = ctk.CTkLabel(self.bk_btn_frame,
                                     text="",
                                     image=self.bk_btn_icon,
                                     cursor="hand2"
                                     )
        self.back_btn.pack(side="left", padx=(15, 0))
        self.back_btn.bind("<Button-1>", lambda event: self.show_login_page())
        self.back_btn.bind("<Enter>", lambda event: self.back_btn.configure(image=self.bk_btn_hvr_icon))
        self.back_btn.bind("<Leave>", lambda event: self.back_btn.configure(image=self.bk_btn_icon))

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
                                   fg_color="transparent"
                                   )
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
        
        # =========================================================
        # 1. NAME ROW (First Name & Last Name)
        # =========================================================
        name_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        name_frame.pack(pady=(0, 15))

        # --- FIRST NAME (Column 0) ---
        self.f_name_label = ctk.CTkLabel(name_frame,
                                      text="First name",
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        self.f_name_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=(0, 5))

        # THE "FAKE" ENTRY (Visual box user sees)
        f_name_fake_entry = ctk.CTkFrame(name_frame,
                                          width=195, 
                                          height=40,
                                          fg_color="#F8F8F8",
                                          border_color=self.entry_border,
                                          border_width=1,
                                          corner_radius=6
                                          )
        f_name_fake_entry.grid(row=1, column=0, padx=(0, 5))
        f_name_fake_entry.pack_propagate(False)

        # THE "REAL" ENTRY (Where user types, tightly wrapped & centered)
        self.f_name_entry = ctk.CTkEntry(f_name_fake_entry,
                                       placeholder_text="Juan",
                                       height=24, # Tight wrap around text
                                       font=self.body_light_font,
                                       fg_color="transparent",
                                       border_width=0,
                                       text_color=self.text_color
                                       )
        self.f_name_entry.place(relx=0.5, rely=0.5, relwidth=0.9, anchor="center")

        # --- LAST NAME (Column 1) ---
        self.l_name_label = ctk.CTkLabel(name_frame,
                                      text="Last name",
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        self.l_name_label.grid(row=0, column=1, sticky="w", padx=(5, 0), pady=(0, 5))

        # THE "FAKE" ENTRY
        l_name_fake_entry = ctk.CTkFrame(name_frame,
                                          width=195, 
                                          height=40,
                                          fg_color="#F8F8F8",
                                          border_color=self.entry_border,
                                          border_width=1,
                                          corner_radius=6
                                          )
        l_name_fake_entry.grid(row=1, column=1, padx=(5, 0))
        l_name_fake_entry.pack_propagate(False)

        # THE "REAL" ENTRY
        self.l_name_entry = ctk.CTkEntry(l_name_fake_entry,
                                       placeholder_text="Dela Cruz",
                                       height=24,
                                       font=self.body_light_font,
                                       fg_color="transparent",
                                       border_width=0,
                                       text_color=self.text_color
                                       )
        self.l_name_entry.place(relx=0.5, rely=0.5, relwidth=0.9, anchor="center")

        # =========================================================
        # 2. PASSWORD ROW (Create & Confirm Password)
        # =========================================================
        pass_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        pass_frame.pack(pady=(0, 15))

        # --- CREATE PASSWORD (Column 0) ---
        self.c_pass_label = ctk.CTkLabel(pass_frame,
                                        text="Create Password",
                                        font=self.body_light_font,
                                        text_color=self.text_color
                                      )
        self.c_pass_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=(0, 5))

        # THE "FAKE" ENTRY
        c_pass_fake_entry = ctk.CTkFrame(pass_frame,
                                    width=195,
                                    height=40,
                                    fg_color="#F8F8F8",
                                    border_color=self.entry_border,
                                    border_width=1,
                                    corner_radius=6
                                    )
        c_pass_fake_entry.grid(row=1, column=0, padx=(0, 5))
        c_pass_fake_entry.pack_propagate(False)

        # THE "REAL" ENTRY
        self.create_pass_entry = ctk.CTkEntry(c_pass_fake_entry,
                                         placeholder_text="••••••••",
                                         height=24,
                                         show="•",
                                         font=self.body_light_font,
                                         fg_color="transparent",
                                         border_width=0,
                                         text_color=self.text_color
                                         )
        self.create_pass_entry.place(relx=0.5, rely=0.5, relwidth=0.9, anchor="center")
        
        # --- CONFIRM PASSWORD (Column 1) ---
        self.confirm_pass_label = ctk.CTkLabel(pass_frame,
                                               text="Confirm Password",
                                               font=self.body_light_font,
                                               text_color=self.text_color
                                               )
        self.confirm_pass_label.grid(row=0, column=1, sticky="w", padx=(5, 0), pady=(0, 5))

        # THE "FAKE" ENTRY
        confirm_pass_fake_entry = ctk.CTkFrame(pass_frame,
                                          width=195,
                                          height=40,
                                          fg_color="#F8F8F8",
                                          border_color=self.entry_border,
                                          border_width=1,
                                          corner_radius=6
                                          )
        confirm_pass_fake_entry.grid(row=1, column=1, padx=(5, 0))
        confirm_pass_fake_entry.pack_propagate(False)

        # THE "REAL" ENTRY
        self.confirm_pass_entry = ctk.CTkEntry(confirm_pass_fake_entry,
                                               placeholder_text="••••••••",
                                               height=24,
                                               show="•",
                                               font=self.body_light_font,
                                               fg_color="transparent",
                                               border_width=0,
                                               text_color=self.text_color
                                               )
        self.confirm_pass_entry.place(relx=0.5, rely=0.5, relwidth=0.9, anchor="center")

        self.next_btn = ctk.CTkButton(self.form_container,
                                      text="REGISTER",
                                      width=350,
                                      height=45,
                                      corner_radius=6,
                                      font=self.body_bold_font,
                                      fg_color=self.primary_color,
                                      hover_color=self.hover_color,
                                      text_color="#FFFFFF",
                                      command=self.attempt_register # Update to Email Verification
                                      )
        self.next_btn.pack(pady=(10, 10))

    def attempt_register(self):
        f_name = self.f_name_entry.get().strip()
        l_name = self.l_name_entry.get().strip()
        email = self.email_entry.get()
        password = self.create_pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()

        if f_name and l_name and email and password and confirm_password:

            if password != confirm_password:
                self.show_toast("Password Do Not Match!", is_error=True)
                return

            full_name = f"{f_name} {l_name}"

            try:
                user_data = {
                    "name": full_name,
                    "email": email,
                    "password": password,
                    "role": "student"
                }
                
                response = requests.post("http://127.0.0.1:8000/users/", json=user_data)
                
                if response.status_code == 200:
                    self.show_toast("Success! Account created.", is_error=False)
                    self.after(2000, self.show_login_page) 
                    
                elif response.status_code == 400:
                    error_msg = response.json().get("detail", "Registration failed.")
                    self.show_toast(error_msg, is_error=True)
                    
                else:
                    self.show_toast("Server error. Try again later.", is_error=True)
                    
            except requests.exceptions.ConnectionError:
                self.show_toast("Error: Is your backend server running?", is_error=True)
        else:
            self.show_toast("Please fill in all fields.", is_error=True)


if __name__ == "__main__":
    app = BoardingHouseApp()
    app.mainloop()


