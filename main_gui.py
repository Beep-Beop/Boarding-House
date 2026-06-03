import customtkinter as ctk
from PIL import Image
import os
import requests

ctk.set_appearance_mode("Light")

class BoardingHouseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Boarding House Finder")
        self.geometry("630x700")
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

        self.design = ctk.CTkImage(Image.open("assets/design.png"), size=(180, 160))
        self.tenant_icon = ctk.CTkImage(Image.open("assets/icons.png"), size=(25, 25))
        self.landlord_icon = ctk.CTkImage(Image.open("assets/Frame.png"), size=(25, 25))

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


        self.body_paragraph_big_font = ctk.CTkFont(family="Poppins", size=24, weight="normal")
        self.body_bold_paragraph_font = ctk.CTkFont(family="Poppins", size=24, weight="bold")
        self.body_paragraph_font = ctk.CTkFont(family="Poppins", size=16, weight="normal")
        self.body_light_font = ctk.CTkFont(family="Poppins Light", size=16, weight="normal") 
        

        self.metro_manila_png = ctk.CTkImage(Image.open("assets/metro_manila.png"), size=(150, 150))
        self.calabarzon_png = ctk.CTkImage(Image.open("assets/calabarzon.png"), size=(250, 80))
        self.cebu_png = ctk.CTkImage(Image.open("assets/cebu.png"), size=(150, 90))
        self.davao_png = ctk.CTkImage(Image.open("assets/davao.png"), size=(200, 80))
        self.other_areas_png = ctk.CTkImage(Image.open("assets/other_areas.png"), size=(100, 70))


        self.primary_color = "#AC7F5E"
        self.entry_border = "#E0E0E0" 
        self.hover_color = "#C5A376"
        self.hover_color_text = "#E2E2E2"
        self.text_color = "#3E362A"
        self.error_red = "#D9534F"
        self.fg_color = "#F8F8F8"
        
        self.configure(fg_color="#FFFFFF")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)
        
        # --- Notification State Variables  ---
        self.current_toast = None
        self.toast_timer = None


        #Debugg
        #self.show_login_page()
        self.show_how_many_properties()

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

        self.geometry("630x700")
        
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=40, fill="both", expand=True)

        # Logo
        logo_label = ctk.CTkLabel(self.form_container,
                                  text=None,
                                  image=self.logo,
                                  width=140,
                                  height=32
                                  )
        logo_label.pack(pady=(20, 15))

        welcome_label = ctk.CTkLabel(self.form_container,
                                     text="WELCOME TO",
                                     weight=5,idth=121,
                                     font=self.body_light_font,
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
                                                checkbox_width=20
                                                )
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
                                          command=self.show_account_type
                                          )
        self.register_btn.pack(side="left")

    def attempt_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if email and password:
            try:
                login_data = {
                    "email": email,
                    "password": password
                }

                response = requests.post("http://127.0.0.1:8000/auth/login", json=login_data)

                if response.status_code == 200:
                    user_info = response.json()
                    self.show_toast(f"Welcome Back, {user_info['name']}", is_error=False)
                
                elif response.status_code in [401, 403]:
                    error_msg = response.json().get("detail", "Login failed.")
                    self.show_toast(error_msg, is_error=True)
                
                else:
                    print("BACKEND ERROR:", response.json()) 
                    self.show_toast("Server error. Try again Later.", is_error=True)

            except requests.exceptions.ConnectionError:
                self.show_toast("Error: Backend Error", is_error=True)
        
        else:
            self.show_toast("Please fill in both fields.", is_error=True)

    def forgot_password(self):
        self.show_toast("BOOOOOOOOP", is_error=False)
    
    def google_login(self):
        self.show_toast("BEEEEP BOOOOOP", is_error=False)
    
    def show_account_type(self):
        self.clear_container()

        self.geometry("1200x700")

        if not hasattr(self, "selected_account_type"):
            self.selected_account_type = None

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
        
        design_label = ctk.CTkLabel(self.form_container,
                                    text=None,
                                    image=self.design,
                                    width=180,
                                    height=160
                                    )
        design_label.pack(pady=(50, 15))

        self.acc_type_label = ctk.CTkLabel(self.form_container,
                                           text="Account Type",
                                           width=180,
                                           height=40,
                                           font=self.body_bold_paragraph_font,
                                           text_color=self.text_color
                                           )
        self.acc_type_label.pack()

        self.yapfest_1 = ctk.CTkLabel(self.form_container,
                                      text="Choose the account type that suits your needs.",
                                      width=500,
                                      height=10,
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        self.yapfest_1.pack()

        self.yapfest_2 = ctk.CTkLabel(self.form_container,
                                     text="Each has a different set of tools and features.",
                                     font=self.body_light_font,
                                     text_color=self.text_color
                                     )
        self.yapfest_2.pack()

        card_frame = ctk.CTkFrame(self.form_container, 
                                fg_color="transparent"
                                )
        card_frame.pack(pady=(10, 10))

        # Tenant
        self.tenant_card = ctk.CTkFrame(card_frame, 
                                        border_width=1, 
                                        border_color=self.entry_border,
                                        fg_color="white", 
                                        width=360, 
                                        height=140, 
                                        corner_radius=10
                                        )
        self.tenant_card.pack(side="left", padx=15)
        self.tenant_card.pack_propagate(False)

        self.tenant_card.grid_columnconfigure(1, weight=1)
        self.tenant_card.grid_rowconfigure(0, weight=1)
        self.tenant_card.grid_rowconfigure(1, weight=1)

        tenant_icon_lbl = ctk.CTkLabel(self.tenant_card,
                                       text=None,
                                       image=self.tenant_icon
                                       )
        tenant_icon_lbl.grid(row=0, column=0, rowspan=2, padx=(15, 10), pady=(20, 15), sticky="nw")

        tenant_title = ctk.CTkLabel(self.tenant_card, 
                                    text="Tenant", 
                                    font=self.body_bold_paragraph_font, 
                                    text_color=self.text_color
                                    )
        tenant_title.grid(row=0, column=1, padx=5, pady=(17, 0), sticky="w")

        tenant_desc = ctk.CTkLabel(self.tenant_card, 
                                   text="Find a place & pay rent online.", 
                                   font=self.body_light_font, 
                                   text_color=self.text_color,
                                   wraplength=210
                                   )
        tenant_desc.grid(row=1, column=1, padx=5, pady=(0, 20), sticky="w")

        self.tenant_dot = ctk.CTkFrame(self.tenant_card, 
                                       width=16, 
                                       height=16, 
                                       corner_radius=8, 
                                       border_width=1, 
                                       border_color="#D0D0D0", 
                                       fg_color="transparent"
                                       )
        self.tenant_dot.grid(row=0, column=2, padx=(0, 15), pady=(15, 0), sticky="ne")

        for widget in (self.tenant_card, tenant_icon_lbl, tenant_title, tenant_desc, self.tenant_dot):
            widget.bind("<Button-1>", lambda event: self.select_account_type("tenant"))
            widget.configure(cursor="hand2")

        # Landlord
        self.landlord_card = ctk.CTkFrame(card_frame, 
                                          border_width=1, 
                                          border_color=self.entry_border, 
                                          fg_color="white", 
                                          width=360, 
                                          height=140, 
                                          corner_radius=10
                                          )
        self.landlord_card.pack(side="left", padx=15)
        self.landlord_card.pack_propagate(False)

        self.landlord_card.grid_columnconfigure(1, weight=1)
        self.landlord_card.grid_rowconfigure(0, weight=1)
        self.landlord_card.grid_rowconfigure(1, weight=1)

        landlord_icon_lbl = ctk.CTkLabel(self.landlord_card, 
                                         text=None, 
                                         image=self.landlord_icon
                                         )
        landlord_icon_lbl.grid(row=0, column=0, rowspan=2, padx=(15, 10), pady=(20, 15), sticky="nw")

        landlord_title = ctk.CTkLabel(self.landlord_card, 
                                      text="Landlord", 
                                      font=self.body_bold_paragraph_font, 
                                      text_color=self.text_color
                                      )
        landlord_title.grid(row=0, column=1, padx=5, pady=(17, 0), sticky="w")

        landlord_desc = ctk.CTkLabel(self.landlord_card, 
                                     text="Accept rent online & manage rental.", 
                                     font=self.body_light_font, 
                                     text_color=self.text_color,
                                     wraplength=210
                                     )
        landlord_desc.grid(row=1, column=1, padx=(5, 27), pady=(0, 20), sticky="w")

        self.landlord_dot = ctk.CTkFrame(self.landlord_card, 
                                         width=16, 
                                         height=16, 
                                         corner_radius=8, 
                                         border_width=1, 
                                         border_color="#D0D0D0", 
                                         fg_color="transparent"
                                         )
        self.landlord_dot.grid(row=0, column=2, padx=(0, 15), pady=(15, 0), sticky="ne")

        for widget in (self.landlord_card, landlord_icon_lbl, landlord_title, landlord_desc, self.landlord_dot):
            widget.bind("<Button-1>", lambda event: self.select_account_type("landlord"))
            widget.configure(cursor="hand2")

        self.next_step_btn = ctk.CTkButton(self.form_container,
                                           text="NEXT",
                                           width=180,
                                           height=45,
                                           corner_radius=6,
                                           font=self.body_bold_font,
                                           fg_color=self.primary_color,
                                           hover_color=self.hover_color,
                                           text_color="#FFFFFF",
                                           command=self.handle_account_type_submit
                                           )
        self.next_step_btn.pack(pady=(20, 10))

    def show_register_page(self):
        self.clear_container()

        self.geometry("630x700")
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

        create_acc_frame = ctk.CTkFrame(self.form_container,
                                        fg_color="transparent"
                                        )
        create_acc_frame.pack(fill="x")

        self.create_acc_label = ctk.CTkLabel(create_acc_frame,
                                             text="Create Account",
                                             font=self.body_bold_paragraph_font
                                             )
        self.create_acc_label.pack(side="left", padx=100, pady=(0, 10))

        notes_frame = ctk.CTkFrame(self.form_container,
                                   fg_color="transparent"
                                   )
        notes_frame.pack(fill="x")

        notes_label = ctk.CTkLabel(notes_frame, 
                                   text="Sign up to get started with BHFinder", 
                                   width=213, 
                                   height=5,
                                   font=self.body_paragraph_font, 
                                   text_color="#4D4D4D"
                                   )
        notes_label.pack(side="left", padx=100, pady=(0, 10))

        # First Name
        first_name_frame = ctk.CTkFrame(self.form_container, 
                                   fg_color="transparent"
                                   )
        first_name_frame.pack(pady=(0, 15))

        self.first_name_label = ctk.CTkLabel(first_name_frame, 
                                        text="First Name", 
                                        font=self.body_light_font, 
                                        text_color=self.text_color
                                        )
        self.first_name_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        first_name_bg_frame = ctk.CTkFrame(first_name_frame, 
                                      width=430, 
                                      height=40, 
                                      fg_color="#F8F8F8",
                                      border_color=self.entry_border, 
                                      border_width=1, 
                                      corner_radius=6
                                      )
        first_name_bg_frame.pack()
        first_name_bg_frame.pack_propagate(False) 

        self.first_name_entry = ctk.CTkEntry(first_name_bg_frame, 
                                        placeholder_text="Enter your first name", 
                                        height=30,
                                        font=self.body_light_font, 
                                        fg_color="transparent", 
                                        border_width=0,
                                        text_color=self.text_color
                                        )
        self.first_name_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        
        # Last Name
        last_name_frame = ctk.CTkFrame(self.form_container,
                                       fg_color="transparent"
                                       )
        last_name_frame.pack(pady=(0, 15))

        self.last_name_label = ctk.CTkLabel(last_name_frame,
                                            text="Last Name",
                                            font=self.body_light_font,
                                            text_color=self.text_color
                                            )
        self.last_name_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        last_name_bg_frame = ctk.CTkFrame(last_name_frame,
                                          width=430,
                                          height=40,
                                          fg_color="#F8F8F8",
                                          border_color=self.entry_border,
                                          border_width=1,
                                          corner_radius=6
                                          )
        last_name_bg_frame.pack()
        last_name_bg_frame.pack_propagate(False)

        self.last_name_entry = ctk.CTkEntry(last_name_bg_frame,
                                            placeholder_text="Enter your last name",
                                            height=30,
                                            font=self.body_light_font,
                                            fg_color="transparent",
                                            border_width=0,
                                            text_color=self.text_color
                                            )
        self.last_name_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        # Date of Birth
        dob_frame = ctk.CTkFrame(self.form_container,
                                 fg_color="transparent"
                                 )
        dob_frame.pack(pady=(0, 15))

        self.dob_label = ctk.CTkLabel(dob_frame,
                                      text="Date Of Birth",
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        self.dob_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        dob_bg_frame = ctk.CTkFrame(dob_frame,
                                    width=430,
                                    height=40,
                                    fg_color="#F8F8F8",
                                    border_color=self.entry_border,
                                    border_width=1,
                                    corner_radius=6
                                    )
        dob_bg_frame.pack()
        dob_bg_frame.pack_propagate(False)

        self.dob_entry = ctk.CTkEntry(dob_bg_frame,
                                      placeholder_text="Select your date of birth",
                                      height=30,
                                      font=self.body_light_font,
                                      fg_color="transparent",
                                      border_width=0,
                                      text_color=self.text_color
                                      )
        self.dob_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        # Email
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
                                      width=430,
                                      height=40,
                                      fg_color=self.fg_color,
                                      border_color=self.entry_border,
                                      border_width=1,
                                      corner_radius=6
                                      )
        email_bg_frame.pack()
        email_bg_frame.pack_propagate(False)

        self.email_entry = ctk.CTkEntry(email_bg_frame,
                                        placeholder_text="Enter email",
                                        height=30,
                                        font=self.body_light_font,
                                        fg_color="transparent",
                                        border_width=0,
                                        text_color=self.text_color
                                        )
        self.email_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        # Phone number
        phone_frame = ctk.CTkFrame(self.form_container,
                                   fg_color="transparent"
                                   )
        phone_frame.pack(pady=(0, 15))

        self.phone_label = ctk.CTkLabel(phone_frame,
                                        text="Phone Number",
                                        font=self.body_light_font,
                                        text_color=self.text_color
                                        )
        self.phone_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        phone_bg_frame = ctk.CTkFrame(phone_frame,
                                      width=430,
                                      height=40,
                                      fg_color=self.fg_color,
                                      border_color=self.entry_border,
                                      border_width=1,
                                      corner_radius=6
                                      )
        phone_bg_frame.pack()
        phone_bg_frame.pack_propagate(False)

        self.phone_entry = ctk.CTkEntry(phone_bg_frame,
                                        placeholder_text="Enter your mobile number",
                                        height=30,
                                        font=self.body_light_font,
                                        fg_color="transparent",
                                        border_width=0,
                                        text_color=self.text_color
                                        )
        self.phone_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        self.next_step_btn = ctk.CTkButton(self.form_container,
                                           text="NEXT",
                                           width=180,
                                           height=45,
                                           corner_radius=6,
                                           font=self.body_bold_font,
                                           fg_color=self.primary_color,
                                           hover_color=self.hover_color,
                                           text_color="#FFFFFF",
                                           command=self.next_regiter_page
                                           )
        self.next_step_btn.pack(pady=(20, 10))

    def next_regiter_page(self):
        self.clear_container()

        self.geometry("630x700")

        self.province_choices = ["select Province..."]
        self.city_choices = ["Select City..."]
        self.barangay_choices = ["Select Barangay..."]

        self.selected_province = ""
        self.selected_city = ""
        self.selected_barangay = ""


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

        self.create_acc_label = ctk.CTkLabel(self.bk_btn_frame,
                                             text="Create Account",
                                             font=self.body_bold_paragraph_font
                                             )
        self.create_acc_label.pack(side="left", padx=(15, 0), pady=(10, 0))

        notes_frame = ctk.CTkFrame(self.form_container,
                                   fg_color="transparent"
                                   )
        notes_frame.pack(fill="x")

        notes_label = ctk.CTkLabel(notes_frame, 
                                   text="Sign up to get started with BHFinder", 
                                   width=213, 
                                   height=5,
                                   font=self.body_paragraph_font, 
                                   text_color="#4D4D4D"
                                   )
        notes_label.pack(side="left", padx=100, pady=(0, 10))

        # Province
        province_frame = ctk.CTkFrame(self.form_container,
                                      fg_color="transparent"
                                      )
        province_frame.pack(pady=(0, 10))

        self.province_label = ctk.CTkLabel(province_frame,
                                        text="Province",
                                        font=self.body_light_font,
                                        text_color=self.text_color
                                      )
        self.province_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        province_bg_frame = ctk.CTkFrame(province_frame,
                                             width=430,
                                             height=40,
                                             fg_color=self.fg_color,
                                             border_color=self.entry_border,
                                             border_width=1,
                                             corner_radius=6
                                             )
        province_bg_frame.pack(pady=(0, 10))
        province_bg_frame.pack_propagate
        

        self.province_menu = ctk.CTkOptionMenu(province_bg_frame,
                                               values=self.province_choices,
                                               font=self.body_light_font,
                                               dropdown_font=self.body_light_font,
                                               fg_color=self.fg_color,
                                               button_color=self.primary_color,
                                               button_hover_color=self.hover_color,
                                               dropdown_fg_color=self.fg_color,
                                               dropdown_hover_color=self.hover_color,
                                               dropdown_text_color=self.text_color,
                                               text_color=self.text_color,
                                               command=self.on_province_selected
                                               )
        self.province_menu.pack()

        # City
        city_frame = ctk.CTkFrame(self.form_container,
                                  fg_color="transparent"
                                  )
        city_frame.pack(pady=(0, 10))

        self.city_label = ctk.CTkLabel(city_frame,
                                       text="City",
                                       font=self.body_light_font,
                                       text_color=self.text_color
                                       )
        self.city_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        self.city_menu = ctk.CTkOptionMenu(city_frame,
                                           values=self.city_choices,
                                           width=430,
                                           height=40,
                                           fg_color=self.fg_color,
                                           button_color=self.primary_color,
                                           text_color=self.text_color,
                                           command=self.on_city_selected
                                           )
        self.city_menu.pack()

        # Barangay
        barangay_frame = ctk.CTkFrame(self.form_container,
                                      fg_color="transparent"
                                      )
        barangay_frame.pack(pady=(0, 10))

        self.barangay_label = ctk.CTkLabel(barangay_frame,
                                           text="Barangay",
                                           font=self.body_light_font,
                                           text_color=self.text_color
                                           )
        self.barangay_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        self.barangay_menu = ctk.CTkOptionMenu(barangay_frame,
                                               values=self.barangay_choices,
                                               width=430,
                                               height=40,
                                               fg_color=self.fg_color,
                                               button_color=self.primary_color,
                                               text_color=self.text_color,
                                               command=lambda choice: setattr(self, 'selected baranagay', choice)
                                               )
        self.barangay_menu.pack()

        # Street
        street_frame = ctk.CTkFrame(self.form_container,
                                    fg_color="transparent"
                                    )
        street_frame.pack(pady=(0, 15))

        self.street_label = ctk.CTkLabel(street_frame,
                                        text="Street",
                                        font=self.body_light_font,
                                        text_color=self.text_color
                                        )
        self.street_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        street_bg_frame = ctk.CTkFrame(street_frame,
                                       width=430,
                                       height=40,
                                       fg_color=self.fg_color,
                                       border_color=self.entry_border,
                                       border_width=1,
                                       corner_radius=6
                                       )
        street_bg_frame.pack()
        street_bg_frame.pack_propagate(False)

        self.street_entry = ctk.CTkEntry(street_bg_frame,
                                         placeholder_text="e.g 123 Sitio Maagay 3",
                                         height=30,
                                         font=self.body_light_font,
                                         fg_color="transparent",
                                         border_width=0,
                                         text_color=self.text_color
                                         )
        self.street_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        # Create Password
        create_pass_frame = ctk.CTkFrame(self.form_container,
                                         fg_color="transparent"
                                         )
        create_pass_frame.pack(pady=(0, 15))

        self.create_pass_label = ctk.CTkLabel(create_pass_frame,
                                              text="Password",
                                              font=self.body_light_font,
                                              text_color=self.text_color
                                              )
        self.create_pass_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))
        
        create_pass_bg_frame = ctk.CTkFrame(create_pass_frame,
                                            width=430,
                                            height=40,
                                            fg_color=self.fg_color,
                                            border_color=self.entry_border,
                                            border_width=1,
                                            corner_radius=6
                                            )
        create_pass_bg_frame.pack()
        create_pass_bg_frame.pack_propagate(False)

        self.create_pass_entry = ctk.CTkEntry(create_pass_bg_frame,
                                              placeholder_text="Min of 8 Characters",
                                              height=30,
                                              show="•",
                                              font=self.body_light_font,
                                              fg_color="transparent",
                                              border_width=0,
                                              text_color=self.text_color
                                              )
        self.create_pass_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        confirm_pass_frame = ctk.CTkFrame(self.form_container,
                                          fg_color="transparent"
                                          )
        confirm_pass_frame.pack(pady=(0, 15))

        self.confirm_pass_label = ctk.CTkLabel(confirm_pass_frame,
                                               text="Confirm Password",
                                               font=self.body_light_font,
                                               text_color=self.text_color
                                               )
        self.confirm_pass_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        confirm_bg_frame = ctk.CTkFrame(confirm_pass_frame,
                                        width=430,
                                        height=40,
                                        fg_color=self.fg_color,
                                        border_color=self.entry_border,
                                        border_width=1,
                                        corner_radius=6
                                        )
        confirm_bg_frame.pack()
        confirm_bg_frame.pack_propagate(False)

        self.confirm_pass_entry = ctk.CTkEntry(confirm_bg_frame,
                                               placeholder_text="Re-rnter your password",
                                               height=30,
                                               show="•",
                                               font=self.body_light_font,
                                               fg_color="transparent",
                                               border_width=0,
                                               text_color=self.text_color
                                               )
        self.confirm_pass_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        # Terms of Service and Privacy Policy
        tos_and_pp_frame = ctk.CTkFrame(self.form_container,
                                        fg_color="transparent"
                                        )
        tos_and_pp_frame.pack(anchor="w", pady=(5, 0))

        self.tos_and_pp_checkbox = ctk.CTkCheckBox(tos_and_pp_frame,
                                                   text="I agree to BHFinder’s",
                                                   font=self.body_paragraph_font,
                                                   fg_color=self.primary_color,
                                                   hover_color=self.hover_color,
                                                   border_color=self.entry_border,
                                                   border_width=2,
                                                   checkbox_height=20,
                                                   checkbox_width=20
                                                   )
        self.tos_and_pp_checkbox.grid(row=0, column=0, padx=(70, 0), sticky="w")

        self.tos_link_btn = ctk.CTkButton(tos_and_pp_frame,
                                          text="Terms of Service",
                                          font=self.body_paragraph_font,
                                          text_color=self.primary_color,
                                          fg_color="transparent",
                                          hover=False, # Gonna change this ro underline 
                                          width=0,
                                          height=20,
                                          command=self.open_terms_of_service
                                          )
        self.tos_link_btn.grid(row=0, column=2, padx=(0, 0), sticky="w")

        self.tos_and_lbl = ctk.CTkLabel(tos_and_pp_frame,
                                        text="and",
                                        font=self.body_paragraph_font,
                                        text_color=self.text_color
                                        )
        self.tos_and_lbl.grid(row=0, column=3, padx=(0, 0), sticky="w")

        self.pp_link_btn = ctk.CTkButton(tos_and_pp_frame,
                                         text="Privacy Policy",
                                         font=self.body_paragraph_font,
                                         text_color=self.primary_color,
                                         fg_color="transparent",
                                         hover=False, # Gonna change this ro underline 
                                         width=0,
                                         height=20,
                                         command=self.open_privacy_policy
                                         )
        self.pp_link_btn.grid(row=0, column=4, padx=0, sticky="w")

        # Create Account Button
        create_acc_btn = ctk.CTkButton(self.form_container, 
                                  text="CREATE ACCOUNT", 
                                  width=430, 
                                  height=45, 
                                  corner_radius=6,
                                  font=self.body_bold_font, 
                                  fg_color="#AC7F5E", 
                                  hover_color=self.hover_color,
                                  text_color="#FFFFFF", 
                                  command=self.show_email_verification_page
                                  )
        create_acc_btn.pack(pady=(20, 10))

    def load_provinces(self):
        try:
            response = requests.get("http://127.0.0.1:8000/locations/provinces")
            if response.status_code == 200:
                options = response.json().get("options", [])
                if options:
                    self.province_menu.configure(values=options)
                    self.province_menu.set(options[0])
                    self.on_province_selected(options[0])
        except Exception as e:
            print(f"Network error loading provinces: {e}")

    def on_province_selected(self, choice):
        self.selected_province = choice

        self.city_menu.configure(values=["Loading..."])
        self.city_menu.set("Loading...")
        self.barangay_menu.configure["Select Baranagay..."]
        self.barangay_menu.set("Select Barangay...")

        try:
            response = requests.get(f"http://127.0.0.1:8000/locations/cities?province={choice}")
            if response.status_code == 200:
                options = response.json().get("options", [])
                self.city_menu.configure(values=options)
                if options:
                    self.city_menu.set(options[0])
                    self.on_city_selected(options[0])
        except Exception as e:
            print(f"Network error loading cities: {e}")

    def on_city_selected(self, choice):
        self.selected_city = choice

        self.barangay_menu.configure(valus=["Loading..."])
        self.barangay_menu.set("Loading...")

        try:
            response = requests.get(f"http://127.0.0.1:8000/locations/barangays?city={choice}")
            if response.status_code == 200:
                options = response.json().get("options", [])
                self.barangay_menu.configure(values=options)
                if options:
                    self.barangay_menu.set(options[0])
                    self.selected_barangay = options[0]
        except Exception as e:
            print(f"Network error loading barangay: {e}")

    def open_terms_of_service(self):
        self.show_toast("Opening Terms of Service layout or web link...", is_error=False)

    def open_privacy_policy(self):
        self.show_toast("Opening Privacy Policy layout or web link...", is_error=False)

    def select_account_type(self, account_type):
        self.selected_account_type = account_type

        active_border = self.primary_color
        inactive_border = self.entry_border

        if account_type == "tenant":
            self.tenant_card.configure(border_color=active_border)
            self.tenant_dot.configure(fg_color=active_border)
            
            self.landlord_card.configure(border_color=inactive_border)
            self.landlord_dot.configure(fg_color="transparent")
        elif account_type == "landlord":
            self.landlord_card.configure(border_color=active_border)
            self.landlord_dot.configure(fg_color=active_border)
            
            self.tenant_card.configure(border_color=inactive_border)
            self.tenant_dot.configure(fg_color="transparent")
    
    def handle_account_type_submit(self):
        if not getattr(self, "selected_account_type", None):
            self.show_toast("Please select an account type to continue.", is_error=True)
            return
        
        self.show_register_page()

    def attempt_register(self):
        f_name = self.first_name_entry.get().strip()
        l_name = self.last_name_entry.get().strip()
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

    def show_email_verification_page(self):
        self.clear_container()

        self.geometry("630x700")

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
        self.back_btn.bind("<Button-1>", lambda event: self.show_register_page())
        self.back_btn.bind("<Enter>", lambda event: self.back_btn.configure(image=self.bk_btn_hvr_icon))
        
        logo_label = ctk.CTkLabel(self.form_container,
                                  text=None,
                                  image=self.logo,
                                  width=140,
                                  height=32
                                  )
        logo_label.pack(pady=(5, 15))

        title_label = ctk.CTkLabel(self.form_container, 
                                   text="BOARDING HOUSE FINDER", 
                                   width=273, 
                                   height=20,
                                   font=self.alt_title_font, 
                                   text_color="#4D4D4D"
                                   )
        title_label.pack(pady=(0, 10))

        email_frame = ctk.CTkFrame(self.form_container,
                                   fg_color="transparent"
                                   )
        email_frame.pack(pady=(0, 15))

        self.email_label = ctk.CTkLabel(email_frame,
                                        text="Enter your email for Verification",
                                        font=self.body_light_font,
                                        text_color=self.text_color
                                        )
        self.email_label.pack(anchor="c", pady=(50, 15))

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

        self.email_entry = ctk.CTkEntry(email_fake_entry,
                                        placeholder_text="example@gmail.com",
                                        height=24,
                                        font=self.body_light_font,
                                        fg_color="transparent",
                                        border_width=0,
                                        text_color=self.text_color
                                        )
        self.email_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        self.verify_btn = ctk.CTkButton(self.form_container,
                                        text="VERIFY EMAIL",
                                        width=400,
                                        height=45,
                                        corner_radius=6,
                                        font=self.body_bold_font,
                                        fg_color=self.primary_color,
                                        hover_color=self.hover_color,
                                        text_color="#FFFFFF",
                                        command=self.attempt_verify_email
                                        )
        self.verify_btn.pack(pady=(10, 10))

    def attempt_verify_email(self):
        self.show_toast("Verify Email", is_error=False)

    def show_main_dashboard(self):
        self.clear_container()

        self.geometry("1900x1000")
        # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

    def show_location(self):
        self.clear_container()

        self.geometry("1262x666")

        # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        bk_btn_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        bk_btn_frame.pack(fill="x", pady=(15, 0))

        self.back_btn = ctk.CTkLabel(bk_btn_frame,
                                     text="",
                                     image=self.bk_btn_icon,
                                     cursor="hand2"
                                     )
        self.back_btn.pack(side="left", padx=(15, 0))
        self.back_btn.bind("<Button-1>", lambda event: self.show_login_page())
        self.back_btn.bind("<Enter>", lambda event: self.back_btn.configure(image=self.bk_btn_hvr_icon))

        # Top section: design image + title/subtitle
        top_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        top_frame.pack(fill="x", padx=(60, 0), pady=(5, 5))

        design_label = ctk.CTkLabel(top_frame,
                                    text=None,
                                    image=self.design,
                                    width=200,
                                    height=180
                                    )
        design_label.pack(side="left")

        title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=(20, 0), anchor="center")

        self.where_are_you_looking_label = ctk.CTkLabel(title_frame,
                                           text="Where Are You Looking?",
                                           font=self.body_bold_paragraph_font,
                                           text_color=self.text_color
                                           )
        self.where_are_you_looking_label.pack(anchor="w")

        self.yapfest_1 = ctk.CTkLabel(title_frame,
                                      text="Select regions you're interested in",
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        self.yapfest_1.pack(anchor="w")

        # ── helper: vertical card (title top, icon bottom, dot top-right) ────
        def make_card(parent, icon_image, label_text, location_key, row, col):
            card = ctk.CTkFrame(parent,
                                border_width=1,
                                border_color=self.entry_border,
                                fg_color="white",
                                width=370,
                                height=140,
                                corner_radius=10)
            card.grid(row=row, column=col, padx=10, pady=8)
            card.grid_propagate(False)

            # 3 rows inside card: row0=title+dot, row1=icon
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=0)
            card.grid_rowconfigure(0, weight=0)
            card.grid_rowconfigure(1, weight=1)

            title_lbl = ctk.CTkLabel(card,
                                     text=label_text,
                                     font=self.body_bold_paragraph_font,
                                     text_color=self.text_color)
            title_lbl.grid(row=0, column=0, padx=(15, 0), pady=(12, 0), sticky="w")

            dot = ctk.CTkFrame(card,
                               width=16, height=16,
                               corner_radius=8,
                               border_width=1,
                               border_color="#D0D0D0",
                               fg_color="transparent")
            dot.grid(row=0, column=1, padx=(0, 12), pady=(12, 0), sticky="ne")

            icon_lbl = ctk.CTkLabel(card, text=None, image=icon_image)
            icon_lbl.grid(row=1, column=0, columnspan=2, padx=0, pady=(0, 10), sticky="s")

            for widget in (card, icon_lbl, title_lbl, dot):
                widget.bind("<Button-1>", lambda event, k=location_key: self.select_show_location(k))
                widget.configure(cursor="hand2")

            return card, dot

        # ── Row 1: Metro Manila · Calabarzon · Cebu ──────────────────────────
        row1_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        row1_frame.pack(anchor="center", pady=(5, 0))

        row1_frame.grid_columnconfigure(0, weight=1, uniform="card")
        row1_frame.grid_columnconfigure(1, weight=1, uniform="card")
        row1_frame.grid_columnconfigure(2, weight=1, uniform="card")

        self.metro_manila_card, self.metro_manila_dot = make_card(
            row1_frame, self.metro_manila_png, "Metro Manila", "metro manila", row=0, col=0)

        self.calabarzon_card, self.calabarzon_dot = make_card(
            row1_frame, self.calabarzon_png, "Calabarzon", "calabarzon", row=0, col=1)

        self.cebu_card, self.cebu_dot = make_card(
            row1_frame, self.cebu_png, "Cebu", "cebu", row=0, col=2)

        # ── Row 2: Davao · Other Areas (centered) ────────────────────────────
        row2_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        row2_frame.pack(anchor="center", pady=(0, 5))

        row2_frame.grid_columnconfigure(0, weight=1, uniform="card")
        row2_frame.grid_columnconfigure(1, weight=1, uniform="card")

        self.davao_card, self.davao_dot = make_card(
            row2_frame, self.davao_png, "Davao", "davao", row=0, col=0)

        self.other_areas_card, self.other_areas_dot = make_card(
            row2_frame, self.other_areas_png, "Other Areas", "other_areas", row=0, col=1)

        # ── Next Button ───────────────────────────────────────────────────────
        self.next_step_btn = ctk.CTkButton(self.form_container,
                                           text="Next",
                                           width=180,
                                           height=45,
                                           corner_radius=6,
                                           font=self.body_bold_font,
                                           fg_color=self.primary_color,
                                           hover_color=self.hover_color,
                                           text_color="#FFFFFF",
                                           command=self.handle_account_type_submit
                                           )
        self.next_step_btn.pack(pady=(10, 10))

    def show_relationship_to_property(self):
        self.clear_container()

        self.geometry("1262x666")

        # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        bk_btn_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        bk_btn_frame.pack(fill="x", pady=(15, 0))

        self.back_btn = ctk.CTkLabel(bk_btn_frame,
                                     text="",
                                     image=self.bk_btn_icon,
                                     cursor="hand2"
                                     )
        self.back_btn.pack(side="left", padx=(15, 0))
        self.back_btn.bind("<Button-1>", lambda event: self.show_login_page())
        self.back_btn.bind("<Enter>", lambda event: self.back_btn.configure(image=self.bk_btn_hvr_icon))

        self.tell_us_label = ctk.CTkLabel(bk_btn_frame,
                                          text="Tell Us More About You?",
                                          font=self.body_bold_paragraph_font,
                                          text_color=self.text_color
                                          )
        self.tell_us_label.pack(anchor="w", pady=(12, 0), padx=(20, 0))

        # Top section: title/subtitle (top-left)
        top_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        top_frame.pack(fill="x", padx=(90, 0), pady=(0, 0))

        self.yapfest_1 = ctk.CTkLabel(top_frame,
                                      text="Help Us To Personalize Your Experience",
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        self.yapfest_1.pack(anchor="w", padx=(20, 0))

        # Centered question label
        self.relationship_label = ctk.CTkLabel(self.form_container,
                                               text="What Is Your Relationship To The Property?",
                                               font=self.body_bold_paragraph_font,
                                               text_color=self.text_color,
                                               justify="center"
                                               )
        self.relationship_label.pack(anchor="center", pady=(70, 0))

        # ── helper: text-only card ────────────────────────────────────────────
        def make_text_card(parent, label_text, location_key, row, col):
            card = ctk.CTkFrame(parent,
                                border_width=1,
                                border_color=self.entry_border,
                                fg_color="white",
                                width=310,
                                height=70,
                                corner_radius=10)
            card.grid(row=row, column=col, padx=12, pady=8)
            card.grid_propagate(False)

            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=0)
            card.grid_rowconfigure(0, weight=1)

            title_lbl = ctk.CTkLabel(card,
                                     text=label_text,
                                     font=self.body_bold_paragraph_font,
                                     text_color=self.text_color)
            title_lbl.grid(row=0, column=0, padx=(20, 0), pady=0, sticky="w")

            dot = ctk.CTkFrame(card,
                               width=16, height=16,
                               corner_radius=8,
                               border_width=1,
                               border_color="#D0D0D0",
                               fg_color="transparent")
            dot.grid(row=0, column=1, padx=(0, 15), pady=0, sticky="e")

            for widget in (card, title_lbl, dot):
                widget.bind("<Button-1>", lambda event, k=location_key: self.select_relationship(k))
                widget.configure(cursor="hand2")

            return card, dot

        # ── Row 1: Property Owner · Property Manager ──────────────────────────
        row1_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        row1_frame.pack(anchor="center", pady=(35, 0))

        row1_frame.grid_columnconfigure(0, weight=1, uniform="card")
        row1_frame.grid_columnconfigure(1, weight=1, uniform="card")

        self.property_owner_card, self.property_owner_dot = make_text_card(
            row1_frame, "Property Owner", "property_owner", row=0, col=0)

        self.property_manager_card, self.property_manager_dot = make_text_card(
            row1_frame, "Property Manager", "property_manager", row=0, col=1)

        # ── Row 2: Authorized Agent (centered) ───────────────────────────────
        row2_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        row2_frame.pack(anchor="center", pady=(20, 0))

        row2_frame.grid_columnconfigure(0, weight=1)

        self.authorized_agent_card, self.authorized_agent_dot = make_text_card(
            row2_frame, "Authorized Agent", "authorized_agent", row=0, col=0)

        # ── Next Button ───────────────────────────────────────────────────────
        self.next_step_btn = ctk.CTkButton(self.form_container,
                                           text="Next",
                                           width=180,
                                           height=45,
                                           corner_radius=6,
                                           font=self.body_bold_font,
                                           fg_color=self.primary_color,
                                           hover_color=self.hover_color,
                                           text_color="#FFFFFF",
                                           command=self.handle_account_type_submit
                                           )
        self.next_step_btn.pack(pady=(120, 10))

    def show_tell_us_more_about_you(self):
        self.clear_container()

        self.geometry("1262x666")

        # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        bk_btn_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        bk_btn_frame.pack(fill="x", pady=(15, 0))

        self.back_btn = ctk.CTkLabel(bk_btn_frame,
                                     text="",
                                     image=self.bk_btn_icon,
                                     cursor="hand2"
                                     )
        self.back_btn.pack(side="left", padx=(15, 0))
        self.back_btn.bind("<Button-1>", lambda event: self.show_login_page())
        self.back_btn.bind("<Enter>", lambda event: self.back_btn.configure(image=self.bk_btn_hvr_icon))

        self.tell_us_label = ctk.CTkLabel(bk_btn_frame,
                                          text="Tell Us More About You",
                                          font=self.body_bold_paragraph_font,
                                          text_color=self.text_color
                                          )
        self.tell_us_label.pack(anchor="w", pady=(12, 0), padx=(20, 0))

        # Top section: title/subtitle (top-left)
        top_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        top_frame.pack(fill="x", padx=(90, 0), pady=(0, 0))

        self.yapfest_1 = ctk.CTkLabel(top_frame,
                                      text="Help us find the perfect rental for you?",
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        self.yapfest_1.pack(anchor="w", padx=(20, 0))

        # ── helper: text-only card ────────────────────────────────────────────
        def make_text_card(parent, label_text, location_key, row, col):
            card = ctk.CTkFrame(parent,
                                border_width=1,
                                border_color=self.entry_border,
                                fg_color="white",
                                width=310,
                                height=70,
                                corner_radius=10)
            card.grid(row=row, column=col, padx=12, pady=8)
            card.grid_propagate(False)

            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=0)
            card.grid_rowconfigure(0, weight=1)

            title_lbl = ctk.CTkLabel(card,
                                     text=label_text,
                                     font=self.body_bold_paragraph_font,
                                     text_color=self.text_color)
            title_lbl.grid(row=0, column=0, padx=(20, 0), pady=0, sticky="w")

            dot = ctk.CTkFrame(card,
                               width=16, height=16,
                               corner_radius=8,
                               border_width=1,
                               border_color="#D0D0D0",
                               fg_color="transparent")
            dot.grid(row=0, column=1, padx=(0, 15), pady=0, sticky="e")

            for widget in (card, title_lbl, dot):
                widget.bind("<Button-1>", lambda event, k=location_key: self.select_relationship(k))
                widget.configure(cursor="hand2")

            return card, dot

        # ── Row 1: Property Owner · Property Manager ──────────────────────────
        row1_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        row1_frame.pack(anchor="center", pady=(80, 0))

        row1_frame.grid_columnconfigure(0, weight=1, uniform="card")
        row1_frame.grid_columnconfigure(1, weight=1, uniform="card")

        self.employed_card, self.employed_dot = make_text_card(
            row1_frame, "Employed", "employed", row=0, col=0)

        self.self_employed, self.self_employed_dot = make_text_card(
            row1_frame, "Self-Employed", "self-_employed", row=0, col=1)
        
        # ── Row 2:
        row2_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        row2_frame.pack(anchor="center", pady=(5, 0))

        row2_frame.grid_columnconfigure(0, weight=1, uniform="card")
        row2_frame.grid_columnconfigure(1, weight=1, uniform="card")

        self.student_card, self.student_dot = make_text_card(
            row2_frame, "Student", "student", row=0, col=0)

        self.unemployed_card, self.unemployed_dot = make_text_card(
            row2_frame, "Unemployed", "unemployed", row=0, col=1)

        # ── Row 3:
        row3_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        row3_frame.pack(anchor="center", pady=(5, 0))

        row3_frame.grid_columnconfigure(0, weight=1)

        self.prefer_not_to_say_card, self.prefer_not_to_say_dot = make_text_card(
            row3_frame, "Prefer Not To Say", "prefer_not_to_say", row=0, col=0)

        # ── Next Button ───────────────────────────────────────────────────────
        self.next_step_btn = ctk.CTkButton(self.form_container,
                                           text="Next",
                                           width=180,
                                           height=45,
                                           corner_radius=6,
                                           font=self.body_bold_font,
                                           fg_color=self.primary_color,
                                           hover_color=self.hover_color,
                                           text_color="#FFFFFF",
                                           command=self.handle_account_type_submit
                                           )
        self.next_step_btn.pack(pady=(120, 10))

    def show_how_many_properties(self):
        self.clear_container()

        self.geometry("1262x666")

        # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        bk_btn_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        bk_btn_frame.pack(fill="x", pady=(15, 0))

        self.back_btn = ctk.CTkLabel(bk_btn_frame,
                                     text="",
                                     image=self.bk_btn_icon,
                                     cursor="hand2"
                                     )
        self.back_btn.pack(side="left", padx=(15, 0))
        self.back_btn.bind("<Button-1>", lambda event: self.show_login_page())
        self.back_btn.bind("<Enter>", lambda event: self.back_btn.configure(image=self.bk_btn_hvr_icon))

        self.tell_us_label = ctk.CTkLabel(bk_btn_frame,
                                          text="Tell Us More About You",
                                          font=self.body_bold_paragraph_font,
                                          text_color=self.text_color
                                          )
        self.tell_us_label.pack(anchor="w", pady=(12, 0), padx=(20, 0))

        # Top section: title/subtitle (top-left)
        top_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        top_frame.pack(fill="x", padx=(90, 0), pady=(0, 0))

        self.yapfest_1 = ctk.CTkLabel(top_frame,
                                      text="Help us to personalize your experience",
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        self.yapfest_1.pack(anchor="w", padx=(20, 0))

        # ── helper: text-only card ────────────────────────────────────────────
        def make_text_card(parent, label_text, location_key, row, col):
            card = ctk.CTkFrame(parent,
                                border_width=1,
                                border_color=self.entry_border,
                                fg_color="white",
                                width=310,
                                height=70,
                                corner_radius=10)
            card.grid(row=row, column=col, padx=12, pady=8)
            card.grid_propagate(False)

            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=0)
            card.grid_rowconfigure(0, weight=1)

            title_lbl = ctk.CTkLabel(card,
                                     text=label_text,
                                     font=self.body_bold_paragraph_font,
                                     text_color=self.text_color)
            title_lbl.grid(row=0, column=0, padx=(20, 0), pady=0, sticky="w")

            dot = ctk.CTkFrame(card,
                               width=16, height=16,
                               corner_radius=8,
                               border_width=1,
                               border_color="#D0D0D0",
                               fg_color="transparent")
            dot.grid(row=0, column=1, padx=(0, 15), pady=0, sticky="e")

            for widget in (card, title_lbl, dot):
                widget.bind("<Button-1>", lambda event, k=location_key: self.select_relationship(k))
                widget.configure(cursor="hand2")

            return card, dot

        # ── Row 1: Centered question label
        self.how_many_properties_label = ctk.CTkLabel(self.form_container,
                                               text="How Many Properties Do You Manage?",
                                               font=self.body_bold_paragraph_font,
                                               text_color=self.text_color,
                                               justify="center"
                                               )
        self.how_many_properties_label.pack(anchor="center", pady=(85, 40))
        
        # ── Row 2:
        row2_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        row2_frame.pack(anchor="center", pady=(5, 0))

        row2_frame.grid_columnconfigure(0, weight=1, uniform="card")
        row2_frame.grid_columnconfigure(1, weight=1, uniform="card")

        self.one_property_card, self.one_property_dot = make_text_card(
            row2_frame, "1 Property", "1_property", row=0, col=0)

        self.two_to_five_properties_card, self.two_to_five_properties_dot = make_text_card(
            row2_frame, "2-5 Properties", "2-5_properties", row=0, col=1)

        # ── Row 3:
        row3_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        row3_frame.pack(anchor="center", pady=(5, 0))

        row3_frame.grid_columnconfigure(0, weight=1)
        row3_frame.grid_columnconfigure(1, weight=1)

        self.six_to_ten_properties_card, self.six_to_ten_properties_dot = make_text_card(
            row3_frame, "6-10 Properties", "6-10_properties", row=0, col=0)
        
        self.plus10_properties_card, self.plus10_properties_dot = make_text_card(
            row3_frame, "+10 Properties", "+10_properties", row=0, col=1)

        # ── Next Button ───────────────────────────────────────────────────────
        self.next_step_btn = ctk.CTkButton(self.form_container,
                                           text="Next",
                                           width=180,
                                           height=45,
                                           corner_radius=6,
                                           font=self.body_bold_font,
                                           fg_color=self.primary_color,
                                           hover_color=self.hover_color,
                                           text_color="#FFFFFF",
                                           command=self.handle_account_type_submit
                                           )
        self.next_step_btn.pack(pady=(120, 10))




if __name__ == "__main__":
    app = BoardingHouseApp()
    app.mainloop()
