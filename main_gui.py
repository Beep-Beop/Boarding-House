import customtkinter as ctk
from tkinter import messagebox
from CTkScrollableDropdown import CTkScrollableDropdown
from PIL import Image
import re
import os
import requests
import threading
import datetime


ctk.set_appearance_mode("Light")

# Bug: Add validation in dob only numbers
# Bug: Don't let User Enter their typo if they type the location
# Bug: Change combo box of dob to scrollable drop down
# Bug: When province scrollabledrop down is open whe i use scroll wheel the whole page gets scrolled instead of the scrollable dropdown
# Bug: While users typing their email it should detetct if their email is already used and use an inline error

# Add: Add in password the thing they need for example their password must have special charackter number and Capital letter

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

        self.inline_error_font = ctk.CTkFont(family="Poppins", size=12, weight="normal")

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

        # --- Fonts specific to dashboard ---
        self.table_header_font = ctk.CTkFont(family="Poppins", size=12, weight="bold")
        self.table_body_font   = ctk.CTkFont(family="Poppins Light", size=12)
        self.card_value_font   = ctk.CTkFont(family="Poppins", size=32, weight="bold")
        self.user_id_font      = ctk.CTkFont(family="Poppins Light", size=10)

        # --- Colors specific to dashboard ---
        self.sidebar_bg     = "#FFFFFF"
        self.content_bg     = "#F0F0F0"
        self.card_bg        = "#FFFFFF"
        self.divider_color  = "#DEDEDE"
        self.muted_color    = "#6B6B6B"
        self.table_row_bg   = "#F5F5F5"


        #Debugg
        # self.show_admin_dashboard()
        # self.show_manage_users()
        # self.show_manage_boarding_houses()
        # self.show_reviews_and_feedback()
        # self.show_reports()


    def clear_container(self):
        for widget in self.winfo_children():
            if "!ctkscrollabledropdown" in str(widget).lower():
                try:
                    widget.destroy()
                except Exception:
                    pass

        if hasattr(self, 'container'):
            for widget in self.container.winfo_children():
                try:
                    widget.destroy()
                except Exception:
                    pass
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
                                     height=5,
                                     width=121,
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
        self.email_fake_entry = ctk.CTkFrame(email_frame,
                                      width=400,
                                      height=40,
                                      fg_color="#F8F8F8",
                                      border_color=self.entry_border,
                                      border_width=1,
                                      corner_radius=6
                                      )
        self.email_fake_entry.pack()
        self.email_fake_entry.pack_propagate(False)

        self.email_entry = ctk.CTkEntry(self.email_fake_entry,
                                        placeholder_text="example@gmail.com",
                                        height=24, # Tight wrap around text
                                        font=self.body_light_font,
                                        fg_color="transparent",
                                        border_width=0,
                                        text_color=self.text_color
                                        )
        self.email_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        self.login_email_error = ctk.CTkLabel(email_frame,
                                              text="",
                                              text_color=self.error_red,
                                              font=self.inline_error_font
                                              )
        self.login_email_error.pack(anchor="w", padx=(15, 0))

        # Password Row
        password_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        password_frame.pack(pady=(0, 15))

        self.password_label = ctk.CTkLabel(password_frame,
                                           text="Password",
                                           font=self.body_light_font,
                                           text_color=self.text_color
                                           )
        self.password_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        self.password_fake_entry = ctk.CTkFrame(password_frame,
                                         width=400,
                                         height=40,
                                         fg_color="#F8F8F8",
                                         border_color=self.entry_border,
                                         border_width=1,
                                         corner_radius=6
                                         )
        self.password_fake_entry.pack()
        self.password_fake_entry.pack_propagate(False)

        self.password_entry = ctk.CTkEntry(self.password_fake_entry,
                                           placeholder_text="Password",
                                           height=24,
                                           show="•",
                                           font=self.body_light_font,
                                           fg_color="transparent",
                                           border_width=0,
                                           text_color=self.text_color
                                           )
        self.password_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        self.login_password_error = ctk.CTkLabel(password_frame,
                                                 text="",
                                                 text_color=self.error_red,
                                                 font=self.inline_error_font
                                                 )
        self.login_password_error.pack(anchor="w", padx=(15, 0))

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

        self.login_email_error.configure(text="")
        self.login_password_error.configure(text="")
        self.email_fake_entry.configure(border_color=self.entry_border)
        self.password_fake_entry.configure(border_color=self.entry_border)

        has_error = False

        if not email:
            self.login_email_error.configure(text="Please enter your email.")
            self.email_fake_entry.configure(border_color=self.error_red)
            has_error = True

        if not password:
            self.login_password_error.configure(text="Please enter your password.")
            self.password_fake_entry.configure(border_color=self.error_red)
            has_error = True

        if has_error:
            return

        try:
            login_data = {
                "email": email,
                "password": password
            }

            response = requests.post("http://127.0.0.1:8000/auth/login", json=login_data)

            if response.status_code == 200:
                user_info = response.json()
                self.show_toast(f"Welcom Back, {user_info['name']}", is_error=False)

            elif response.status_code in [401, 403]:
                error_msg = response.json().get("detail", "Login Failed.")
                self.login_email_error.configure(text=error_msg)
                self.login_password_error.configure(text=error_msg)
                self.email_fake_entry.configure(border_color=self.error_red)
                self.password_fake_entry.configure(border_color=self.error_red)

            else:
                self.login_email_error.configure(text="Server error, Try again Later.")
        except requests.exceptions.ConnectionError:
            self.login_email_error.configure(text="Error: Cannot connect to backend server")
            self.email_fake_entry.configure(border_color=self.error_red)

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


        # Tracking arrays
        self.province_options = []
        self.city_options = []
        self.barangay_options = []
        self.selected_province = ""
        self.selected_city = ""
        self.selected_barangay = ""

        # Main Container
        self.form_container = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)
        self.form_container.bind_all("<Button-4>", lambda e: self.form_container._parent_canvas.yview("scroll", -1, "units"))
        self.form_container.bind_all("<Button-5>", lambda e: self.form_container._parent_canvas.yview("scroll", 1, "units"))

        # Top Navigation: Back Button
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
        self.create_acc_label.pack(side="left", padx=5, pady=(15, 10))

        notes_label = ctk.CTkLabel(self.form_container,
                                   text="Sign up to get started with BHFinder",
                                   width=213,
                                   height=5,
                                   font=self.body_paragraph_font,
                                   text_color="#4D4D4D"
                                   )
        notes_label.pack(anchor="w", padx=90)


        # Section 1: Personal Details
        section_1_label = ctk.CTkLabel(self.form_container,
                                       text="Personal Details",
                                       font=self.body_bold_paragraph_font,
                                       text_color=self.primary_color
                                       )
        section_1_label.pack(anchor="w", padx=90, pady=(10, 10))

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

        self.first_name_bg_frame = ctk.CTkFrame(first_name_frame,
                                      width=430,
                                      height=40,
                                      fg_color="#F8F8F8",
                                      border_color=self.entry_border,
                                      border_width=1,
                                      corner_radius=6
                                      )
        self.first_name_bg_frame.pack()
        self.first_name_bg_frame.pack_propagate(False)
        self.first_name_error_lbl = ctk.CTkLabel(first_name_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.first_name_error_lbl.pack(anchor="w", padx=15)

        self.first_name_entry = ctk.CTkEntry(self.first_name_bg_frame,
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

        self.last_name_bg_frame = ctk.CTkFrame(last_name_frame,
                                          width=430,
                                          height=40,
                                          fg_color="#F8F8F8",
                                          border_color=self.entry_border,
                                          border_width=1,
                                          corner_radius=6
                                          )
        self.last_name_bg_frame.pack()
        self.last_name_bg_frame.pack_propagate(False)
        self.last_name_error_lbl = ctk.CTkLabel(last_name_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.last_name_error_lbl.pack(anchor="w", padx=15)

        self.last_name_entry = ctk.CTkEntry(self.last_name_bg_frame,
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
        dob_frame.pack(anchor="w", fill="x",  pady=(0, 15))

        self.dob_label = ctk.CTkLabel(dob_frame,
                                      text="Date Of Birth",
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        self.dob_label.pack(anchor="w", padx=(100, 0), pady=(0, 5))

        self.dob_bg_frame = ctk.CTkFrame(dob_frame,
                                           fg_color=self.fg_color,
                                           corner_radius=6,
                                           border_width=1,
                                           border_color=self.entry_border,
                                           width=430
                                           )
        self.dob_bg_frame.pack()
        self.dob_error_lbl = ctk.CTkLabel(dob_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.dob_error_lbl.pack(anchor="w", padx=100)
        months = [f"{i:02d}" for i in range(1, 13)]
        self.month_box = ctk.CTkComboBox(self.dob_bg_frame,
                                         values=months,
                                         width=70,
                                         fg_color=self.fg_color,
                                         border_width=0,
                                         button_color=self.primary_color,
                                         button_hover_color=self.hover_color,
                                         dropdown_fg_color=self.fg_color
                                         )
        self.month_box.set("MM")
        self.month_box.pack(side="left", padx=(35, 10), pady=8)

        ctk.CTkLabel(self.dob_bg_frame,
                     text="/",
                     text_color=self.text_color,
                     width=10
                     ).pack(side="left", padx=(25, 20))

        # Days dropdown
        days = [f"{i:02d}" for i in range(1, 32)]
        self.day_box = ctk.CTkComboBox(self.dob_bg_frame,
                                       values=days,
                                       width=65,
                                       fg_color=self.fg_color,
                                       border_width=0,
                                       border_color=self.entry_border,
                                       button_color=self.primary_color,
                                       button_hover_color=self.hover_color,
                                       dropdown_fg_color=self.fg_color
                                       )
        self.day_box.set("DD")
        self.day_box.pack(side="left", pady=8, padx=(0, 5))

        ctk.CTkLabel(self.dob_bg_frame,
                     text="/",
                     text_color=self.text_color,
                     width=10
                     ).pack(side="left", padx=(30, 25))

        # Year Dropdown
        current_year = datetime.datetime.now().year
        years = [str(y) for y in range(current_year, 1949, -1)]
        self.year_box = ctk.CTkComboBox(self.dob_bg_frame,
                                        values=years,
                                        width=75,
                                        fg_color=self.fg_color,
                                        border_width=0,
                                        border_color=self.entry_border,
                                        button_color=self.primary_color,
                                        button_hover_color=self.hover_color,
                                        dropdown_fg_color=self.fg_color
                                        )
        self.year_box.set("YYYY")
        self.year_box.pack(side="left", pady=8, padx=(0, 45))

        # Email
        self.email_frame = ctk.CTkFrame(self.form_container,

                                   fg_color="transparent"
                                   )
        self.email_frame.pack(pady=(0, 15))

        self.email_label = ctk.CTkLabel(self.email_frame,
                                        text="Email",
                                        font=self.body_light_font,
                                        text_color=self.text_color
                                        )
        self.email_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        self.email_bg_frame = ctk.CTkFrame(self.email_frame,
                                      width=430,
                                      height=40,
                                      fg_color=self.fg_color,
                                      border_color=self.entry_border,
                                      border_width=1,
                                      corner_radius=6
                                      )
        self.email_bg_frame.pack()
        self.email_bg_frame.pack_propagate(False)
        self.email_error_lbl = ctk.CTkLabel(self.email_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.email_error_lbl.pack(anchor="w", padx=15)

        self.email_entry = ctk.CTkEntry(self.email_bg_frame,
                                        placeholder_text="Enter email",
                                        height=30,
                                        font=self.body_light_font,
                                        fg_color="transparent",
                                        border_width=0,
                                        text_color=self.text_color
                                        )
        self.email_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        self.email_entry.bind("<KeyRelease>", self.validate_email_realtime)

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

        self.phone_bg_frame = ctk.CTkFrame(phone_frame,
                                      width=430,
                                      height=40,
                                      fg_color=self.fg_color,
                                      border_color=self.entry_border,
                                      border_width=1,
                                      corner_radius=6
                                      )
        self.phone_bg_frame.pack()
        self.phone_bg_frame.pack_propagate(False)
        self.phone_error_lbl = ctk.CTkLabel(phone_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.phone_error_lbl.pack(anchor="w", padx=15)



        self.phone_entry = ctk.CTkEntry(self.phone_bg_frame,
                                        height=30,
                                        font=self.body_light_font,
                                        fg_color="transparent",
                                        border_width=0,
                                        text_color="#aaaaaa",
                                        validate="key",
                                        validatecommand=(self.register(self.validate_phone), "%P")
                                        )
        self.phone_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        self.phone_entry.configure(validate="none")
        self.phone_entry.insert(0, "Enter your mobile number")
        self.phone_entry.configure(validate="key")
        def phone_focus_in(e):
            if self.phone_entry.get() == "Enter your mobile number":
                self.phone_entry.delete(0, "end")
                self.phone_entry.configure(text_color=self.text_color)

        def phone_focus_out(e):
            if not self.phone_entry.get():
                self.phone_entry.configure(validate="none")
                self.phone_entry.insert(0, "Enter your mobile number")
                self.phone_entry.configure(validate="key")
                self.phone_entry.configure(text_color="#aaaaaa")
        self.phone_entry.bind("<FocusIn>", phone_focus_in)
        self.phone_entry.bind("<FocusOut>", phone_focus_out)
        self.phone_entry.bind("<KeyRelease>", self.validate_phone_realtime)



        # Section 2: Location Details
        self.section_2_label = ctk.CTkLabel(self.form_container,
                                            text="Location Details",
                                            font=self.body_bold_paragraph_font,
                                            text_color=self.primary_color
                                            )
        self.section_2_label.pack(anchor="w", padx=90, pady=(15, 10))

        # Province
        province_frame = ctk.CTkFrame(self.form_container,
                                      fg_color="transparent"
                                      )
        province_frame.pack(pady=(0, 5))

        self.province_label = ctk.CTkLabel(province_frame,

                                           text="Province",
                                           font=self.body_light_font,
                                           text_color=self.text_color
                                           )
        self.province_label.pack(anchor="w", padx=(15, 0), pady=(0, 2))

        self.province_menu = ctk.CTkComboBox(province_frame,
                                             values=[],
                                             width=430,
                                             height=40,
                                             font=self.body_light_font,
                                             dropdown_font=self.body_light_font,
                                             fg_color=self.fg_color,
                                             border_color=self.entry_border,
                                             border_width=1,
                                             button_color=self.primary_color,
                                             button_hover_color=self.hover_color,
                                             dropdown_fg_color=self.fg_color,
                                             dropdown_hover_color=self.hover_color,
                                             text_color=self.text_color,
                                             command=self.on_province_selected
                                             )
        self.province_menu.pack(pady=(0, 10))
        self.province_menu.configure(state="normal")
        self.province_menu.set("Select Province...")

        self.province_menu._entry.bind("<FocusIn>", lambda e: self.province_menu.set("")
                                if self.province_menu.get() == "Select Province..." else None)

        self.province_menu.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.province_menu, "Select Province..."))

        self.province_dropdown = CTkScrollableDropdown(self.province_menu,
                                                       values=["Select Province..."],
                                                       autocomplete=True,
                                                       command=self.on_province_selected
                                                       )
        self.province_error_lbl = ctk.CTkLabel(province_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.province_error_lbl.pack(anchor="w", padx=15)

        # City
        city_frame = ctk.CTkFrame(self.form_container,
                                  fg_color="transparent"
                                  )
        city_frame.pack(pady=(0, 5))

        city_label = ctk.CTkLabel(city_frame,
                                  text="City",
                                  font=self.body_light_font,
                                  text_color=self.text_color
                                  )
        city_label.pack(anchor="w", padx=(15, 0), pady=(5, 2))

        self.city_menu = ctk.CTkComboBox(city_frame,
                                         values=[],
                                         width=430,
                                         height=40,
                                         font=self.body_light_font,
                                         dropdown_font=self.body_light_font,
                                         fg_color=self.fg_color,
                                         border_color=self.entry_border,
                                         border_width=1,
                                         button_color=self.primary_color,
                                         button_hover_color=self.hover_color,
                                         dropdown_fg_color=self.fg_color,
                                         dropdown_hover_color=self.hover_color,
                                         dropdown_text_color=self.text_color,
                                         command=self.on_city_selected
                                         )
        self.city_menu.pack(pady=(0, 10))
        self.city_menu.configure(state="normal")
        self.city_menu.set("Select City...")

        self.city_menu._entry.bind("<FocusIn>", lambda e: self.city_menu.set("")
                            if self.city_menu.get() == "Select City..." else None)
        self.city_menu.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.city_menu, "Select City..."))

        self.city_dropdown = CTkScrollableDropdown(self.city_menu,
                                                   values=["Select City..."],
                                                   autocomplete=True,
                                                   command=self.on_city_selected
                                                   )
        self.city_error_lbl = ctk.CTkLabel(city_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.city_error_lbl.pack(anchor="w", padx=15)

        # Barangay
        barangay_frame = ctk.CTkFrame(self.form_container,
                                      fg_color="transparent"
                                      )
        barangay_frame.pack(pady=(0, 5))

        barangay_label = ctk.CTkLabel(barangay_frame,
                                      text="Barangay",
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        barangay_label.pack(anchor="w", padx=(15, 0), pady=(5, 2))

        self.barangay_menu = ctk.CTkComboBox(barangay_frame,
                                             values=[],
                                             width=430,
                                             height=40,
                                             font=self.body_light_font,
                                             dropdown_font=self.body_light_font,
                                             fg_color=self.fg_color,
                                             border_color=self.entry_border,
                                             border_width=1,
                                             button_color=self.primary_color,
                                             button_hover_color=self.hover_color,
                                             dropdown_fg_color=self.fg_color,
                                             dropdown_hover_color=self.hover_color,
                                             dropdown_text_color=self.text_color,
                                             text_color=self.text_color,
                                             command=lambda choice: setattr(self, 'selected_barangay', choice)
                                             )
        self.barangay_menu.pack(pady=(0, 10))
        self.barangay_menu.configure(state="normal")
        self.barangay_menu.set("Select Barangay...")

        self.barangay_menu._entry.bind("<FocusIn>", lambda e: self.barangay_menu.set("")
                                if self.barangay_menu.get() == "Select Barangay..." else None)
        self.barangay_menu.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.barangay_menu, "Select Barangay..."))

        self.barangay_dropdown = CTkScrollableDropdown(self.barangay_menu,
                                                       values=["Select Barangay..."],
                                                       autocomplete=True,
                                                       command=lambda choice: [self.barangay_menu.set(choice), setattr(self, 'selected_barangay', choice)]
                                                       )
        self.barangay_error_lbl = ctk.CTkLabel(barangay_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.barangay_error_lbl.pack(anchor="w", padx=15)

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

        self.street_bg_frame = ctk.CTkFrame(street_frame,
                                       width=430,
                                       height=40,
                                       fg_color=self.fg_color,
                                       border_color=self.entry_border,
                                       border_width=1,
                                       corner_radius=6
                                       )
        self.street_bg_frame.pack()
        self.street_bg_frame.pack_propagate(False)
        self.street_error_lbl = ctk.CTkLabel(street_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.street_error_lbl.pack(anchor="w", padx=15)

        self.street_entry = ctk.CTkEntry(self.street_bg_frame,
                                         placeholder_text="e.g 123 Sitio Maagay 3",
                                         height=30,
                                         font=self.body_light_font,
                                         fg_color="transparent",
                                         border_width=0,
                                         text_color=self.text_color
                                         )
        self.street_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")

        # Section 3: Accpunt Security
        self.section_3_label = ctk.CTkLabel(self.form_container,
                                            text="Account Security",
                                            font=self.body_bold_paragraph_font,
                                            text_color=self.primary_color
                                            )
        self.section_3_label.pack(anchor="w", padx=90, pady=(15, 10))

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

        self.create_pass_bg_frame = ctk.CTkFrame(create_pass_frame,
                                            width=430,
                                            height=40,
                                            fg_color=self.fg_color,
                                            border_color=self.entry_border,
                                            border_width=1,
                                            corner_radius=6
                                            )
        self.create_pass_bg_frame.pack()
        self.create_pass_bg_frame.pack_propagate(False)
        self.create_pass_error_lbl = ctk.CTkLabel(create_pass_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.create_pass_error_lbl.pack(anchor="w", padx=15)

        self.create_pass_entry = ctk.CTkEntry(self.create_pass_bg_frame,
                                              placeholder_text="Min of 8 Characters",
                                              height=30,
                                              show="•",
                                              font=self.body_light_font,
                                              fg_color="transparent",
                                              border_width=0,
                                              text_color=self.text_color
                                              )
        self.create_pass_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        self.create_pass_entry.bind("<KeyRelease>", self.validate_password_match_realtime)

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

        self.confirm_pass_bg_frame = ctk.CTkFrame(confirm_pass_frame,
                                        width=430,
                                        height=40,
                                        fg_color=self.fg_color,
                                        border_color=self.entry_border,
                                        border_width=1,
                                        corner_radius=6
                                        )
        self.confirm_pass_bg_frame.pack()
        self.confirm_pass_bg_frame.pack_propagate(False)
        self.confirm_pass_error_lbl = ctk.CTkLabel(confirm_pass_frame, text="", font=ctk.CTkFont(size=12), text_color=self.error_red)
        self.confirm_pass_error_lbl.pack(anchor="w", padx=15)

        self.confirm_pass_entry = ctk.CTkEntry(self.confirm_pass_bg_frame,
                                               placeholder_text="Re-rnter your password",
                                               height=30,
                                               show="•",
                                               font=self.body_light_font,
                                               fg_color="transparent",
                                               border_width=0,
                                               text_color=self.text_color
                                               )
        self.confirm_pass_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        self.confirm_pass_entry.bind("<KeyRelease>", self.validate_password_match_realtime)

        self.tos_frame = ctk.CTkFrame(self.form_container,
                                      fg_color="transparent"
                                      )
        self.tos_frame.pack(anchor="w", pady=(5, 0), padx=100)

        self.tos_and_pp_checkbox = ctk.CTkCheckBox(self.tos_frame,
                                                   text="I agree to BHFinder’s",
                                                   font=self.body_paragraph_font,
                                                   fg_color=self.primary_color,
                                                   border_width=2,
                                                   checkbox_height=20,
                                                   checkbox_width=20
                                                   )
        self.tos_and_pp_checkbox.grid(row=0, column=0, sticky="w")

        self.tos_link_btn = ctk.CTkButton(self.tos_frame,
                                          text="Terms of Service",
                                          font=self.body_paragraph_font,
                                          text_color=self.primary_color,
                                          fg_color="transparent",
                                          hover=False,
                                          width=0,
                                          height=20,
                                          command=self.open_terms_of_service
                                          )
        self.tos_link_btn.grid(row=0, column=1, padx=2, sticky="w")

        self.tos_and_lbl = ctk.CTkLabel(self.tos_frame,
                                        text="and",
                                        font=self.body_paragraph_font,
                                        text_color=self.text_color
                                        )
        self.tos_and_lbl.grid(row=0, column=2, padx=2, sticky="w")

        self.pp_link_btn = ctk.CTkButton( self.tos_frame,
                                         text="Privacy Policy",
                                         font=self.body_paragraph_font,
                                         text_color=self.primary_color,
                                         fg_color="transparent",
                                         hover=False,
                                         width=0,
                                         height=20,
                                         command=self.open_privacy_policy
                                         )
        self.pp_link_btn.grid(row=0, column=3, padx=2, sticky="w")

        self.tos_error_lbl = ctk.CTkLabel(self.form_container,
                                          text="",
                                          font=ctk.CTkFont(size=12),
                                          text_color=self.error_red
                                          )
        self.tos_error_lbl.pack(anchor="w", padx=120, pady=(2, 10))

        self.create_acc_btn = ctk.CTkButton(self.form_container,
                                            text="CREATE ACCOUNT",
                                            width=430,
                                            height=45,
                                            corner_radius=6,
                                            font=self.body_bold_font,
                                            fg_color="#AC7F5E",
                                            hover_color=self.hover_color,
                                            text_color="#FFFFFF",
                                            command=self.attempt_register
                                            )
        self.create_acc_btn.pack(pady=(10, 40))

        self.after(100, self.load_provinces)

    def validate_email_realtime(self, event=None):
       email = self.email_entry.get().strip()
       pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

       if not email:
            self.email_bg_frame.configure(border_color=self.entry_border)
            self.email_error_lbl.configure(text="")
       elif re.match(pattern, email):
            self.email_bg_frame.configure(border_color="green")
            self.email_error_lbl.configure(text="")
       else:
            self.email_bg_frame.configure(border_color=self.error_red)
            self.email_error_lbl.configure(text="Invalid email format")

    def validate_phone_realtime(self, event=None):
        phone = self.phone_entry.get().strip()

        if not phone:
            self.phone_bg_frame.configure(border_color=self.entry_border)
            self.phone_error_lbl.configure(text="")

        elif not phone.isdigit() or len(phone) != 11:
            self.phone_bg_frame.configure(border_color=self.error_red)
            self.phone_error_lbl.configure(text="Invalid Phone number.")

        else:
            self.phone_bg_frame.configure(border_color="green")
            self.phone_error_lbl.configure(text="")

    def validate_password_match_realtime(self, event=None):
        password = self.create_pass_entry.get()
        confirm = self.confirm_pass_entry.get()

        if not confirm:
            self.confirm_pass_bg_frame.configure(border_color=self.entry_border)
            self.confirm_pass_error_lbl.configure(text="")

        elif password != confirm:
            self.confirm_pass_bg_frame.configure(border_color=self.error_red)
            self.confirm_pass_error_lbl.configure(text="Passwords do not match")

        else:
            self.confirm_pass_bg_frame.configure(border_color="green")
            self.confirm_pass_error_lbl.configure(text="")

    def validate_phone(self, text):
        if text == "" or (text.isdigit() and len(text) <= 11):
            return True
        return False

    def _filter_phone_input(self, *args):
        val = self.phone_var.get()
        filtered = "".join(c for c in val if c.isdigit())[:11]
        if filtered != val:
            self.phone_var.set(filtered)

    def load_provinces(self):
        def fetch():
            try:
                response = requests.get("http://127.0.0.1:8000/locations/provinces")
                if response.status_code == 200:
                    options = response.json().get("options", [])
                    self.province_options = options
                    if options and hasattr(self, "province_dropdown") and self.province_menu.winfo_exists():
                        self.province_dropdown.configure(values=options)
                        self.update_idletasks()
            except Exception as e:
                print(f"Network error loading provinces: {e}")

        threading.Thread(target=fetch, daemon=True).start()

    def on_province_selected(self, choice):
        if not choice or not choice.strip() or choice.startswith("Select"):
            return

        self.selected_province = choice
        self.province_menu.set(choice)

        self.city_menu.set("Loading cities...")
        self.barangay_menu.set("Selected Barangay...")
        self.city_dropdown.configure(values=["Loading..."])
        self.barangay_dropdown.configure(values=["Loading..."])

        self.city_options = []
        self.barangay_options = []

        try:
            response = requests.get(f"http://127.0.0.1:8000/locations/cities?province={choice}")
            if response.status_code == 200:
                options = response.json().get("options", [])
                self.city_options = options
                if hasattr(self, "city_dropdown") and self.city_menu.winfo_exists():
                    self.city_dropdown.configure(values=options)
                    if options and len(options) > 0:
                        self.city_menu.set("")
                    else:
                        self.city_menu.set("No Cities Found")
        except Exception as e:
            print(f"Network error loading cities: {e}")

    def on_city_selected(self, choice):
        if not choice or not choice.strip() or choice.startswith("Select") or choice.startswith("Loading"):
            return

        self.selected_city = choice
        self.city_menu.set(choice)

        self.barangay_menu.set("Loading Barangays...")
        self.barangay_dropdown.configure(values=["Loading..."])

        try:
            response = requests.get(f"http://127.0.0.1:8000/locations/barangays?city={choice}")
            if response.status_code == 200:
                options = response.json().get("options", [])
                self.barangay_options = options
                if hasattr(self, "barangay_dropdown") and self.barangay_menu.winfo_exists():
                    self.barangay_dropdown.configure(values=options)
                    if options and len(options) > 0:
                        self.barangay_menu.set("")
                    else:
                        self.barangay_menu.set("No Barangay Found")
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
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        if phone == "Enter your mobile number":
            phone = ""

        month = self.month_box.get()
        day = self.day_box.get()
        year = self.year_box.get()

        province = self.province_menu.get().strip()
        city = self.city_menu.get().strip()
        barangay = self.barangay_menu.get().strip()
        street = self.street_entry.get().strip()

        password = self.create_pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()

        error_labels = [
            self.first_name_error_lbl, self.last_name_error_lbl, self.dob_error_lbl,
            self.email_error_lbl, self.phone_error_lbl, self.province_error_lbl,
            self.city_error_lbl, self.barangay_error_lbl, self.street_error_lbl,
            self.create_pass_error_lbl, self.confirm_pass_error_lbl, self.tos_error_lbl
        ]
        for lbl in error_labels:
            lbl.configure(text="")

        self.first_name_bg_frame.configure(border_color=self.entry_border)
        self.last_name_bg_frame.configure(border_color=self.entry_border)
        self.dob_bg_frame.configure(border_color=self.entry_border)
        self.email_bg_frame.configure(border_color=self.entry_border)
        self.phone_bg_frame.configure(border_color=self.entry_border)
        self.province_menu.configure(border_color=self.entry_border)
        self.city_menu.configure(border_color=self.entry_border)
        self.barangay_menu.configure(border_color=self.entry_border)
        self.street_bg_frame.configure(border_color=self.entry_border)
        self.create_pass_bg_frame.configure(border_color=self.entry_border)
        self.confirm_pass_bg_frame.configure(border_color=self.entry_border)

        has_error = False

        # Validate Basic Fields Inline
        if not f_name:
            self.first_name_error_lbl.configure(text="⚠ First name is required.")
            self.first_name_bg_frame.configure(border_color=self.error_red)
            has_error = True
        if not l_name:
            self.last_name_error_lbl.configure(text="⚠ Last name is required.")
            self.last_name_bg_frame.configure(border_color=self.error_red)
            has_error = True

        if month == "MM" or day == "DD" or year == "YYYY":
            self.dob_error_lbl.configure(text="⚠ Please complete your Date of Birth selection.")
            self.dob_bg_frame.configure(border_color=self.error_red)
            has_error = True
        dob_string = f"{year}-{month}-{day}"

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not email:
            self.email_error_lbl.configure(text="⚠ Email address is required.")
            self.email_bg_frame.configure(border_color=self.error_red)
            has_error = True
        elif not re.match(email_pattern, email):
            self.email_error_lbl.configure(text="⚠ Incorrect email format.")
            self.email_bg_frame.configure(border_color=self.error_red)
            has_error = True

        if not phone:
            self.phone_error_lbl.configure(text="⚠ Phone number is required.")
            self.phone_bg_frame.configure(border_color=self.error_red)
            has_error = True
        elif len(phone) < 11:
            self.phone_error_lbl.configure(text="⚠ Mobile number must be exactly 11 digits.")
            self.phone_bg_frame.configure(border_color=self.error_red)
            has_error = True

        # Validate Location Options (Typos)
        matched_prov = [p for p in getattr(self, "province_options", []) if p.lower() == province.lower()]
        if not matched_prov or province.startswith("Select"):
            self.province_error_lbl.configure(text="⚠ Select a valid Province from the list.")
            self.province_menu.configure(border_color=self.error_red)
            has_error = True
        else:
            province = matched_prov[0]
            self.province_menu.set(province)

        matched_cit = [c for c in getattr(self, "city_options", []) if c.lower() == city.lower()]
        if not matched_cit or city.startswith("Select") or city.startswith("Loading"):
            self.city_error_lbl.configure(text="⚠ Select a valid City from the list.")
            self.city_menu.configure(border_color=self.error_red)
            has_error = True
        else:
            city = matched_cit[0]
            self.city_menu.set(city)

        matched_brgy = [b for b in getattr(self, "barangay_options", []) if b.lower() == barangay.lower()]
        if not matched_brgy or barangay.startswith("Select") or barangay.startswith("Loading"):
            self.barangay_error_lbl.configure(text="⚠ Select a valid Barangay from the list.")
            self.barangay_menu.configure(border_color=self.error_red)
            has_error = True
        else:
            barangay = matched_brgy[0]
            self.barangay_menu.set(barangay)

        if not street:
            self.street_error_lbl.configure(text="⚠ Street address is required.")
            self.street_bg_frame.configure(border_color=self.error_red)
            has_error = True

        if len(password) < 8:
            self.create_pass_error_lbl.configure(text="⚠ Password must be at least 8 characters.")
            self.create_pass_bg_frame.configure(border_color=self.error_red)
            has_error = True
        if password != confirm_password:
            self.confirm_pass_error_lbl.configure(text="⚠ Passwords do not match.")
            self.confirm_pass_bg_frame.configure(border_color=self.error_red)
            has_error = True

        if not self.tos_and_pp_checkbox.get():
            self.tos_error_lbl.configure(text="⚠ You must agree to the Terms of Service.")
            has_error = True

        if has_error:
            return

        # 3. Live Database Check for Existing Registration
        try:
            response = requests.get(f"http://127.0.0.1:8000/users/check-email?email={email}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get("exists"):
                    self.email_error_lbl.configure(text="⚠ This email is already registered.")
                    self.email_bg_frame.configure(border_color=self.error_red)
                    return
        except requests.exceptions.ConnectionError:
            pass

        # 4. Create Account Payload Submission
        full_name = f"{f_name} {l_name}"
        try:
            user_data = {
                "name": full_name,
                "email": email,
                "password": password,
                "role": self.selected_account_type,
                "phone": phone,
                "province": province,
                "city": city,
                "barangay": barangay,
                "street": street,
                "date_of_birth": dob_string
            }

            response = requests.post("http://127.0.0.1:8000/users/", json=user_data)
            if response.status_code == 201:
                self.show_toast("Success! Account created.", is_error=False)
                self.after(2000, self.show_login_page)
            elif response.status_code == 400:
                error_msg = response.json().get("detail", "Registration failed.")
                self.show_toast(error_msg, is_error=True)
            else:
                self.show_toast("Server error. Try again later.", is_error=True)
        except requests.exceptions.ConnectionError:
            self.show_toast("Error: Is your backend server running?", is_error=True)

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

        self.geometry("1200x700")

    # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        bk_btn_frame = ctk.CTkFrame(self.form_container,
                                  fg_color="transparent"
                                  )
        bk_btn_frame.pack(fill="x", pady=(15, 0))

        self.back_btn = ctk.CTkLabel(bk_btn_frame,
                                     text="",
                                     image=self.bk_btn_icon,
                                     cursor="hand2"
                                     )
        self.back_btn.pack(side="left", padx=(15, 0))
        self.back_btn.bind("<Button-1>", lambda event: self.show_login_page())
        self.back_btn.bind("<Enter>", lambda event: self.back_btn.configure(image=self.bk_btn_hvr_icon))

    def clear_placeholder(self, event, combobox, placeholder_text):
        if combobox.get() == placeholder_text:
            combobox.set("")

    def restore_placeholder(self, event, combobox, placeholder_text):
        if not combobox.get().strip():
            combobox.set(placeholder_text)



    def show_admin_dashboard(self):
        self.clear_container()
        self.geometry("1100x580")

        self.sidebar = ctk.CTkFrame(
            self.container,
            width=170,
            fg_color=self.sidebar_bg,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content_area = ctk.CTkFrame(
            self.container,
            fg_color=self.content_bg,
            corner_radius=0
        )
        self.content_area.pack(side="left", fill="both", expand=True)

        self._build_admin_sidebar()
        self._build_admin_topbar()
        self._build_admin_main()

    def _build_admin_sidebar(self):

        # Brand row: logo.png
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=18, pady=(18, 25))

        brand_logo_label = ctk.CTkLabel(brand_frame,
                                        text="",
                                        image=self.logo
                                        )
        brand_logo_label.pack(side="left")

        # Nav items: (label, is_active)
        nav_items = [
            ("Dashboard",              True),
            ("Manage Users",           False),
            ("Manage\nBoarding Houses",False),
            ("Reviews & Feedback",     False),
            ("Reports",                False),
            ("Settings",               False),
        ]

        for label_text, is_active in nav_items:
            self._admin_nav_button(label_text, is_active)

        # Spacer pushes Logout to the bottom
        spacer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer_frame.pack(fill="both", expand=True)

        logout_btn = ctk.CTkButton(self.sidebar,
                                   text="Logout",
                                   width=140,
                                   height=34,
                                   corner_radius=6,
                                   fg_color="transparent",
                                   hover_color="#F0E8E0",
                                   text_color=self.muted_color,
                                   font=self.body_paragraph_font,
                                   anchor="center",
                                   command=self.show_login_page
                                   )
        logout_btn.pack(pady=(0, 20))

    def _admin_nav_button(self, text, is_active):
        """Creates a single sidebar navigation button."""
        fg_color    = self.primary_color if is_active else "transparent"
        text_color  = "#FFFFFF"          if is_active else self.text_color
        font        = ctk.CTkFont(family="Poppins", size=13, weight="bold") if is_active \
                      else ctk.CTkFont(family="Poppins", size=13)
        hover_color = self.hover_color   if is_active else "#F0E8E0"

        nav_btn = ctk.CTkButton(self.sidebar,
                                text=text,
                                width=175,
                                height=38,
                                corner_radius=0,
                                fg_color=fg_color,
                                hover_color=hover_color,
                                text_color=text_color,
                                font=font,
                                anchor="center",
                                command=lambda: None
                                )
        nav_btn.pack(fill="x")

    def _build_admin_topbar(self):

        topbar_frame = ctk.CTkFrame(self.content_area,
                                    height=55,
                                    fg_color="#FFFFFF",
                                    corner_radius=0
                                    )
        topbar_frame.pack(fill="x")
        topbar_frame.pack_propagate(False)

        # Thin bottom border line
        topbar_border = ctk.CTkFrame(topbar_frame,
                                     height=1,
                                     fg_color=self.divider_color,
                                     corner_radius=0
                                     )
        topbar_border.pack(side="bottom", fill="x")

        # Right side: avatar circle + name + TID
        user_info_frame = ctk.CTkFrame(topbar_frame, fg_color="transparent")
        user_info_frame.pack(side="right", padx=20, pady=8)

        avatar_frame = ctk.CTkFrame(user_info_frame,
                                    width=36,
                                    height=36,
                                    corner_radius=18,
                                    fg_color=self.primary_color
                                    )
        avatar_frame.pack(side="left", padx=(0, 8))
        avatar_frame.pack_propagate(False)

        avatar_icon_label = ctk.CTkLabel(avatar_frame,
                                         text="👤",
                                         font=ctk.CTkFont(size=16),
                                         text_color="#FFFFFF"
                                         )
        avatar_icon_label.place(relx=0.5, rely=0.5, anchor="center")

        name_id_frame = ctk.CTkFrame(user_info_frame, fg_color="transparent")
        name_id_frame.pack(side="left")

        name_label = ctk.CTkLabel(name_id_frame,
                                  text="kamrul",
                                  font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
                                  text_color=self.text_color
                                  )
        name_label.pack(anchor="w")

        tid_label = ctk.CTkLabel(name_id_frame,
                                 text="TID: 23545",
                                 font=self.user_id_font,
                                 text_color=self.muted_color
                                 )
        tid_label.pack(anchor="w")

    def _build_admin_main(self):

        main_frame = ctk.CTkFrame(self.content_area,
                                  fg_color=self.content_bg,
                                  corner_radius=0
                                  )
        main_frame.pack(fill="both", expand=True, padx=28, pady=20)

        # Welcome line
        welcome_label = ctk.CTkLabel(main_frame,
                                     text="Welcome Back, Admin",
                                     font=self.body_paragraph_font,
                                     text_color=self.text_color
                                     )
        welcome_label.pack(anchor="w", pady=(0, 16))

        # Stat cards then table
        self._build_admin_stat_cards(main_frame)
        self._build_admin_recent_listings(main_frame)

    def _build_admin_stat_cards(self, parent):

        stat_data = [
            ("Total Users:",      "150"),
            ("Pending Approval:", "15"),
            ("Users Registered:", "350"),
            ("Active Listings:",  "105"),
        ]

        cards_grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_grid_frame.pack(fill="x", pady=(0, 20))

        cards_grid_frame.columnconfigure(0, weight=1)
        cards_grid_frame.columnconfigure(1, weight=1)

        for idx, (label_text, value_text) in enumerate(stat_data):
            row = idx // 2
            col = idx % 2

            card_frame = ctk.CTkFrame(cards_grid_frame,
                                      fg_color=self.card_bg,
                                      corner_radius=10,
                                      border_width=0
                                      )
            card_frame.grid(row=row,
                            column=col,
                            padx=(0 if col == 0 else 10, 0),
                            pady=(0 if row == 0 else 10, 0),
                            sticky="nsew"
                            )

            card_label = ctk.CTkLabel(card_frame,
                                      text=label_text,
                                      font=self.body_paragraph_font,
                                      text_color=self.text_color
                                      )
            card_label.pack(anchor="w", padx=20, pady=(18, 2))

            card_value = ctk.CTkLabel(card_frame,
                                      text=value_text,
                                      font=self.card_value_font,
                                      text_color=self.text_color
                                      )
            card_value.pack(anchor="w", padx=20, pady=(0, 18))

    def _build_admin_recent_listings(self, parent):
        import tkinter as tk

        # Section title
        section_label = ctk.CTkLabel(parent,
                                     text="Recent Listings",
                                     font=self.body_paragraph_font,
                                     text_color=self.text_color
                                     )
        section_label.pack(anchor="w", pady=(0, 8))

        headers = ["House Name:", "Location:", "Price:", "Status:"]
        col_widths = [185, 185, 185, 145]   # exact pixel widths per column

        listing_rows = [
            ("Blue Dorm",   "QC",      "3,500 pesos", "Approved"),
            ("Green Stay",  "Manila",  "4,500 pesos", "Pending"),
            ("Cozy House",  "Marikina","2,000 pesos", "Approved"),
        ]

        BORDER = "#DEDEDE"   # divider / outer border color
        BG     = "#FFFFFF"   # cell background
        FG     = self.text_color

        all_rows  = [headers]      + list(listing_rows)
        row_fonts = [self.table_header_font] + [self.table_body_font] * len(listing_rows)

        # ── Outer frame: bg=BORDER so the 1px gaps show as lines ──────────────
        table_outer = tk.Frame(parent, bg=BORDER, bd=1, relief="flat")
        table_outer.pack(anchor="center", padx=(10, 0))

        for row_idx, (row_data, row_font) in enumerate(zip(all_rows, row_fonts)):

            row_frame = tk.Frame(table_outer, bg=BORDER, bd=0)
            # 1px top spacing between rows acts as the horizontal divider line
            top_pad = 1 if row_idx > 0 else 0
            row_frame.pack(side="top", fill="x", pady=(top_pad, 0))

            for col_idx, cell_text in enumerate(row_data):

                # Fixed-size container — pack_propagate(False) locks the width
                cell_frame = tk.Frame(row_frame,
                                      width=col_widths[col_idx],
                                      height=42,
                                      bg=BG,
                                      bd=0
                                      )
                # 1px left spacing between columns acts as the vertical divider
                left_pad = 1 if col_idx > 0 else 0
                cell_frame.pack(side="left", padx=(left_pad, 0))
                cell_frame.pack_propagate(False)

                cell_label = tk.Label(cell_frame,
                                      text=cell_text,
                                      font=row_font,
                                      bg=BG,
                                      fg=FG,
                                      anchor="w",
                                      padx=14,
                                      pady=0
                                      )
                cell_label.place(relx=0, rely=0.5, anchor="w")



    def show_manage_users(self):
        self.clear_container()
        self.geometry("1100x580")

        self.sidebar = ctk.CTkFrame(
            self.container,
            width=170,
            fg_color=self.sidebar_bg,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(
            self.container,
            fg_color=self.content_bg,
            corner_radius=0
        )
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar_manage_users()
        self._build_manage_users_content()

    def _build_sidebar_manage_users(self):
        logo = ctk.CTkLabel(
            self.sidebar,
            image=self.logo,
            text=""
        )
        logo.pack(pady=(30, 25))

        nav_items = [
            ("Dashboard", False),
            ("Manage Users", True),
            ("Manage\nBoarding Houses", False),
            ("Reviews & Feedback", False),
            ("Reports", False),
            ("Settings", False)
        ]

        for text, active in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=165,
                height=38,
                fg_color="#D4B183" if active else "transparent",
                hover_color="#D4B183",
                text_color="#222222",
                corner_radius=2,
                font=ctk.CTkFont(family="Poppins", size=13, weight="bold" if active else "normal")
            )
            btn.pack(pady=3)

        ctk.CTkLabel(
            self.sidebar,
            text=""
        ).pack(expand=True)

        logout = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="transparent",
            hover_color="#EFEFEF",
            text_color="#444444",
            font=ctk.CTkFont(family="Poppins", size=13)
        )
        logout.pack(pady=20)

    def _build_manage_users_content(self):
        # ── Top bar ───────────────────────────────────────────────────────────
        topbar_frame = ctk.CTkFrame(
            self.content,
            height=55,
            fg_color="#FFFFFF",
            corner_radius=0
        )
        topbar_frame.pack(fill="x")
        topbar_frame.pack_propagate(False)

        topbar_border = ctk.CTkFrame(
            topbar_frame,
            height=1,
            fg_color="#DEDEDE",
            corner_radius=0
        )
        topbar_border.pack(side="bottom", fill="x")

        user_info_frame = ctk.CTkFrame(topbar_frame, fg_color="transparent")
        user_info_frame.pack(side="right", padx=20, pady=8)

        avatar_frame = ctk.CTkFrame(
            user_info_frame,
            width=36,
            height=36,
            corner_radius=18,
            fg_color=self.primary_color
        )
        avatar_frame.pack(side="left", padx=(0, 8))
        avatar_frame.pack_propagate(False)

        avatar_icon_label = ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=ctk.CTkFont(size=16),
            text_color="#FFFFFF"
        )
        avatar_icon_label.place(relx=0.5, rely=0.5, anchor="center")

        name_id_frame = ctk.CTkFrame(user_info_frame, fg_color="transparent")
        name_id_frame.pack(side="left")

        name_label = ctk.CTkLabel(
            name_id_frame,
            text="kamrul",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            text_color=self.text_color
        )
        name_label.pack(anchor="w")

        tid_label = ctk.CTkLabel(
            name_id_frame,
            text="TID: 23545",
            font=ctk.CTkFont(family="Poppins Light", size=10),
            text_color="#6B6B6B"
        )
        tid_label.pack(anchor="w")
        # ─────────────────────────────────────────────────────────────────────

        body = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        body.pack(fill="both", expand=True, padx=25, pady=10)

        title = ctk.CTkLabel(
            body,
            text="MANAGE USERS",
            font=ctk.CTkFont(family="Poppins", size=24, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 20))

        self._build_search_toolbar(body)
        self._build_users_table(body)

    def _build_search_toolbar(self, parent):
        toolbar = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        toolbar.pack(fill="x", pady=(0, 25))

        search = ctk.CTkEntry(
            toolbar,
            width=460,
            height=42,
            placeholder_text="Search user name...",
            corner_radius=20,
            border_width=0,
            fg_color="#EAEAEA",
            font=ctk.CTkFont(family="Poppins", size=12)
        )
        search.pack(side="left", padx=(100, 50))

        add_btn = ctk.CTkButton(
            toolbar,
            text="+  Add User",
            width=135,
            height=32,
            fg_color="#B8865B",
            hover_color="#A87850",
            corner_radius=4,
            font=ctk.CTkFont(family="Poppins", size=12)
        )
        add_btn.pack(side="left")

    def _build_users_table(self, parent):

        card = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=8
        )
        card.pack(fill="both", expand=True)

        headers = [
            "User ID",
            "Name",
            "Email",
            "Role",
            "Status",
            "Date Registered",
            "Actions"
        ]

        table_outer = ctk.CTkFrame(card, fg_color="transparent")
        table_outer.pack(fill="both", expand=True, padx=30, pady=25)

        table = ctk.CTkFrame(table_outer, fg_color="transparent")
        table.pack(fill="both", expand=True)

        col_weights = [6, 13, 15, 8, 8, 11, 7]
        for i, w in enumerate(col_weights):
            table.grid_columnconfigure(i, weight=w, uniform="col")

        # ── Fonts copied from first code ──────────────────────────────────
        HEADER_FONT = ctk.CTkFont(family="Poppins", size=12, weight="bold")
        CELL_FONT   = ctk.CTkFont(family="Poppins Light", size=12)
        PADX        = (8, 8)
        HEADER_PADY = (10, 18)
        ROW_PADY    = 16

        for col, header in enumerate(headers):
            sticky = "" if col in (3, 4, 6) else "w"
            ctk.CTkLabel(
                table,
                text=header,
                font=HEADER_FONT,
                text_color="#000000"
            ).grid(
                row=0, column=col,
                padx=PADX, pady=HEADER_PADY,
                sticky=sticky
            )

        sep = ctk.CTkFrame(table, height=1, fg_color="#E0E0E0")
        sep.grid(row=1, column=0, columnspan=len(headers), sticky="ew", padx=0, pady=0)

        users = [
            ["U001", "Jhay Del Socorro",    "jhay@gmail.com", "Tenant", "Active",   "Jan 10, 2026"],
            ["U002", "Kyll Kouichi Harabe", "kyll@gmail.com", "Owner",  "Pending",  "Jan 12, 2026"],
            ["U003", "Mike Ulang",          "mike@gmail.com", "Tenant", "Disabled", "Jan 16, 2026"]
        ]

        for r, row in enumerate(users, start=2):
            data_row = r

            ctk.CTkLabel(
                table, text=row[0], font=CELL_FONT
            ).grid(row=data_row, column=0, padx=PADX, pady=ROW_PADY, sticky="w")

            ctk.CTkLabel(
                table, text=row[1], font=CELL_FONT
            ).grid(row=data_row, column=1, padx=PADX, pady=ROW_PADY, sticky="w")

            ctk.CTkLabel(
                table, text=row[2], font=CELL_FONT
            ).grid(row=data_row, column=2, padx=PADX, pady=ROW_PADY, sticky="w")

            ctk.CTkLabel(
                table,
                text=row[3],
                width=90, height=30,
                corner_radius=15,
                fg_color="#F2F2F2",
                text_color="#000000",
                font=CELL_FONT
            ).grid(row=data_row, column=3, padx=PADX, pady=ROW_PADY)

            ctk.CTkLabel(
                table,
                text=row[4],
                width=90, height=30,
                corner_radius=15,
                fg_color="#F2F2F2",
                text_color="#000000",
                font=CELL_FONT
            ).grid(row=data_row, column=4, padx=PADX, pady=ROW_PADY)

            ctk.CTkLabel(
                table, text=row[5], font=CELL_FONT
            ).grid(row=data_row, column=5, padx=PADX, pady=ROW_PADY, sticky="w")

            actions_frame = ctk.CTkFrame(table, fg_color="transparent")
            actions_frame.grid(row=data_row, column=6, padx=PADX, pady=ROW_PADY)

            edit_btn = ctk.CTkButton(
                actions_frame,
                text="✎",
                width=28, height=28,
                fg_color="transparent",
                hover_color="#F0F0F0",
                text_color="black",
                corner_radius=4,
                font=CELL_FONT
            )
            edit_btn.pack(side="left", padx=3)

            delete_btn = ctk.CTkButton(
                actions_frame,
                text="🗑",
                width=28, height=28,
                fg_color="transparent",
                hover_color="#F0F0F0",
                text_color="black",
                corner_radius=4,
                font=CELL_FONT
            )
            delete_btn.pack(side="left", padx=3)

            if r < len(users) + 1:
                div = ctk.CTkFrame(table, height=1, fg_color="#F0F0F0")
                div.grid(row=data_row + 1, column=0,
                         columnspan=len(headers), sticky="ew", padx=0, pady=0)



    def show_manage_boarding_houses(self):
        self.clear_container()
        self.geometry("1100x580")

        self.sidebar = ctk.CTkFrame(
            self.container,
            width=170,
            fg_color=self.sidebar_bg,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(
            self.container,
            fg_color=self.content_bg,
            corner_radius=0
        )
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar_boarding_houses()
        self._build_boarding_houses_content()

    def _build_sidebar_boarding_houses(self):
        logo = ctk.CTkLabel(
            self.sidebar,
            image=self.logo,
            text=""
        )
        logo.pack(pady=(30, 25))

        nav_items = [
            ("Dashboard", False),
            ("Manage Users", False),
            ("Manage\nBoarding Houses", True),
            ("Reviews & Feedback", False),
            ("Reports", False),
            ("Settings", False)
        ]

        for text, active in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=165,
                height=38,
                fg_color="#D4B183" if active else "transparent",
                hover_color="#D4B183",
                text_color="#222222",
                corner_radius=2,
                font=ctk.CTkFont(family="Poppins", size=13, weight="bold" if active else "normal")
            )
            btn.pack(pady=3)

        ctk.CTkLabel(self.sidebar, text="").pack(expand=True)

        logout = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="transparent",
            hover_color="#EFEFEF",
            text_color="#444444",
            font=ctk.CTkFont(family="Poppins", size=13)
        )
        logout.pack(pady=20)

    def _build_boarding_houses_content(self):
        topbar_frame = ctk.CTkFrame(
            self.content,
            height=55,
            fg_color="#FFFFFF",
            corner_radius=0
        )
        topbar_frame.pack(fill="x")
        topbar_frame.pack_propagate(False)

        # Thin bottom border line
        topbar_border = ctk.CTkFrame(
            topbar_frame,
            height=1,
            fg_color="#DEDEDE",
            corner_radius=0
        )
        topbar_border.pack(side="bottom", fill="x")

        # Right side: avatar circle + name + TID
        user_info_frame = ctk.CTkFrame(topbar_frame, fg_color="transparent")
        user_info_frame.pack(side="right", padx=20, pady=8)

        avatar_frame = ctk.CTkFrame(
            user_info_frame,
            width=36,
            height=36,
            corner_radius=18,
            fg_color=self.primary_color
        )
        avatar_frame.pack(side="left", padx=(0, 8))
        avatar_frame.pack_propagate(False)

        avatar_icon_label = ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=ctk.CTkFont(size=16),
            text_color="#FFFFFF"
        )
        avatar_icon_label.place(relx=0.5, rely=0.5, anchor="center")

        name_id_frame = ctk.CTkFrame(user_info_frame, fg_color="transparent")
        name_id_frame.pack(side="left")

        name_label = ctk.CTkLabel(
            name_id_frame,
            text="kamrul",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            text_color=self.text_color
        )
        name_label.pack(anchor="w")

        tid_label = ctk.CTkLabel(
            name_id_frame,
            text="TID: 23545",
            font=ctk.CTkFont(family="Poppins Light", size=10),
            text_color="#6B6B6B"
        )
        tid_label.pack(anchor="w")
        # ─────────────────────────────────────────────────────────────────────

        # ── Body ─────────────────────────────────────────────────────────────
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=20)

        title = ctk.CTkLabel(
            body,
            text="MANAGE BOARDING HOUSES",
            font=ctk.CTkFont(family="Poppins", size=24, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 15))

        self._build_boarding_houses_table(body)

    def _build_boarding_houses_table(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=8
        )
        card.pack(fill="both", expand=True)

        table_outer = ctk.CTkFrame(card, fg_color="transparent")
        table_outer.pack(fill="both", expand=True, padx=30, pady=25)

        table = ctk.CTkFrame(table_outer, fg_color="transparent")
        table.pack(fill="both", expand=True)

        headers = ["House Name", "Location", "Price", "Status", "View", "Actions"]

        col_weights = [12, 12, 8, 10, 6, 14]
        for i, w in enumerate(col_weights):
            table.grid_columnconfigure(i, weight=w, uniform="col")

        HEADER_FONT = ctk.CTkFont(family="Poppins", size=12, weight="bold")
        CELL_FONT   = ctk.CTkFont(family="Poppins Light", size=12)
        PADX        = (8, 8)
        HEADER_PADY = (10, 18)
        ROW_PADY    = 14

        # ── Header Row ────────────────────────────────────────────────────────
        for col, header in enumerate(headers):
            sticky = "" if col in (3, 4, 5) else "w"
            ctk.CTkLabel(
                table,
                text=header,
                font=HEADER_FONT,
                text_color="#000000"
            ).grid(
                row=0, column=col,
                padx=PADX, pady=HEADER_PADY,
                sticky=sticky
            )

        # ── Separator under header ────────────────────────────────────────────
        sep = ctk.CTkFrame(table, height=1, fg_color="#E0E0E0")
        sep.grid(row=1, column=0, columnspan=len(headers), sticky="ew", padx=0, pady=0)

        # ── Data ─────────────────────────────────────────────────────────────
        boarding_houses = [
            ["Blue Dorm",       "Quezon City",  "₱3500", "Approved"],
            ["Green Stay",      "Manila",       "₱4000", "Pending"],
            ["Mike Ulang\nU003","Marikina City","₱2000", "Approved"],
        ]

        for r, row in enumerate(boarding_houses, start=2):
            data_row = r * 2

            # ── House Name ────────────────────────────────────────────────────
            ctk.CTkLabel(
                table, text=row[0], font=CELL_FONT, justify="left"
            ).grid(row=data_row, column=0, padx=PADX, pady=ROW_PADY, sticky="w")

            # ── Location ──────────────────────────────────────────────────────
            ctk.CTkLabel(
                table, text=row[1], font=CELL_FONT
            ).grid(row=data_row, column=1, padx=PADX, pady=ROW_PADY, sticky="w")

            # ── Price ─────────────────────────────────────────────────────────
            ctk.CTkLabel(
                table, text=row[2], font=CELL_FONT
            ).grid(row=data_row, column=2, padx=PADX, pady=ROW_PADY, sticky="w")

            # ── Status Badge ──────────────────────────────────────────────────
            status = row[3]
            if status == "Approved":
                badge_fg   = "#22C55E"
                badge_text = "#FFFFFF"
            else:
                badge_fg   = "#F2F2F2"
                badge_text = "#000000"

            ctk.CTkLabel(
                table,
                text=status,
                width=90, height=28,
                corner_radius=14,
                fg_color=badge_fg,
                text_color=badge_text,
                font=CELL_FONT
            ).grid(row=data_row, column=3, padx=PADX, pady=ROW_PADY)

            # ── View (eye icon) ───────────────────────────────────────────────
            ctk.CTkButton(
                table,
                text="👁",
                width=32, height=28,
                fg_color="transparent",
                hover_color="#F0F0F0",
                text_color="#333333",
                corner_radius=4,
                font=CELL_FONT
            ).grid(row=data_row, column=4, padx=PADX, pady=ROW_PADY)

            # ── Actions ───────────────────────────────────────────────────────
            actions_frame = ctk.CTkFrame(table, fg_color="transparent")
            actions_frame.grid(row=data_row, column=5, padx=PADX, pady=ROW_PADY)

            if status == "Approved":
                ctk.CTkButton(
                    actions_frame,
                    text="Edit",
                    width=65, height=30,
                    fg_color="white",
                    hover_color="#F0F0F0",
                    text_color="#000000",
                    border_width=1,
                    border_color="#CCCCCC",
                    corner_radius=4,
                    font=CELL_FONT
                ).pack(side="left", padx=4)

                ctk.CTkButton(
                    actions_frame,
                    text="Delete",
                    width=65, height=30,
                    fg_color="white",
                    hover_color="#F0F0F0",
                    text_color="#000000",
                    border_width=1,
                    border_color="#CCCCCC",
                    corner_radius=4,
                    font=CELL_FONT
                ).pack(side="left", padx=4)

            else:
                ctk.CTkButton(
                    actions_frame,
                    text="Approve",
                    width=70, height=30,
                    fg_color="white",
                    hover_color="#F0F0F0",
                    text_color="#000000",
                    border_width=1,
                    border_color="#CCCCCC",
                    corner_radius=4,
                    font=CELL_FONT
                ).pack(side="left", padx=4)

                ctk.CTkButton(
                    actions_frame,
                    text="Reject",
                    width=65, height=30,
                    fg_color="#EF4444",
                    hover_color="#DC2626",
                    text_color="#FFFFFF",
                    corner_radius=4,
                    font=CELL_FONT
                ).pack(side="left", padx=4)

            # ── Row divider ───────────────────────────────────────────────────
            if r < len(boarding_houses) + 1:
                div = ctk.CTkFrame(table, height=1, fg_color="#E0E0E0")
                div.grid(row=data_row + 1, column=0,
                        columnspan=len(headers), sticky="ew", padx=0, pady=0)



    def show_reviews_and_feedback(self):
        self.clear_container()
        self.geometry("1100x580")


        self.sidebar = ctk.CTkFrame(
            self.container,
            width=170,
            fg_color=self.sidebar_bg,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(
            self.container,
            fg_color=self.content_bg,
            corner_radius=0
        )
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar_reviews()
        self._build_reviews_content()

    def _build_sidebar_reviews(self):
        logo = ctk.CTkLabel(
            self.sidebar,
            image=self.logo,
            text=""
        )
        logo.pack(pady=(30, 25))

        nav_items = [
            ("Dashboard", False),
            ("Manage Users", False),
            ("Manage\nBoarding Houses", False),
            ("Reviews & Feedback", True),
            ("Reports", False),
            ("Settings", False)
        ]

        for text, active in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=165,
                height=38,
                fg_color="#D4B183" if active else "transparent",
                hover_color="#D4B183",
                text_color="#222222",
                corner_radius=2,
                font=ctk.CTkFont(family="Poppins", size=13, weight="bold" if active else "normal")
            )
            btn.pack(pady=3)

        ctk.CTkLabel(self.sidebar, text="").pack(expand=True)

        logout = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="transparent",
            hover_color="#EFEFEF",
            text_color="#444444",
            font=ctk.CTkFont(family="Poppins", size=13)
        )
        logout.pack(pady=20)

    def _build_reviews_content(self):
        topbar_frame = ctk.CTkFrame(
            self.content,
            height=55,
            fg_color="#FFFFFF",
            corner_radius=0
        )
        topbar_frame.pack(fill="x")
        topbar_frame.pack_propagate(False)

        topbar_border = ctk.CTkFrame(
            topbar_frame,
            height=1,
            fg_color="#DEDEDE",
            corner_radius=0
        )
        topbar_border.pack(side="bottom", fill="x")

        user_info_frame = ctk.CTkFrame(topbar_frame, fg_color="transparent")
        user_info_frame.pack(side="right", padx=20, pady=8)

        avatar_frame = ctk.CTkFrame(
            user_info_frame,
            width=36,
            height=36,
            corner_radius=18,
            fg_color=self.primary_color
        )
        avatar_frame.pack(side="left", padx=(0, 8))
        avatar_frame.pack_propagate(False)

        avatar_icon_label = ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=ctk.CTkFont(size=16),
            text_color="#FFFFFF"
        )
        avatar_icon_label.place(relx=0.5, rely=0.5, anchor="center")

        name_id_frame = ctk.CTkFrame(user_info_frame, fg_color="transparent")
        name_id_frame.pack(side="left")

        name_label = ctk.CTkLabel(
            name_id_frame,
            text="kamrul",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            text_color=self.text_color
        )
        name_label.pack(anchor="w")

        tid_label = ctk.CTkLabel(
            name_id_frame,
            text="TID: 23545",
            font=ctk.CTkFont(family="Poppins Light", size=10),
            text_color="#6B6B6B"
        )
        tid_label.pack(anchor="w")
        # ─────────────────────────────────────────────────────────────────────

        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=15)

        ctk.CTkLabel(
            body,
            text="REVIEWS AND FEEDBACK",
            font=ctk.CTkFont(family="Poppins", size=20, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        self._build_reviews_table(body)

    def _build_reviews_table(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(fill="both", expand=True)

        table_outer = ctk.CTkFrame(card, fg_color="transparent")
        table_outer.pack(fill="both", expand=True, padx=15, pady=15)

        table = ctk.CTkFrame(table_outer, fg_color="transparent")
        table.pack(fill="both", expand=True)

        headers = ["Reviewer", "Listing", "Rating", "Review", "Status", "Date", "Actions"]

        col_weights = [10, 8, 9, 22, 7, 8, 8]
        for i, w in enumerate(col_weights):
            table.grid_columnconfigure(i, weight=w, uniform="col")

        # ── Reduced font sizes to fit content ─────────────────────────────────
        HEADER_FONT = ctk.CTkFont(family="Poppins", size=11, weight="bold")
        CELL_FONT   = ctk.CTkFont(family="Poppins Light", size=10)
        ICON_FONT   = ctk.CTkFont(family="Poppins", size=10)
        STAR_FONT   = ctk.CTkFont(family="Poppins", size=11)
        PADX        = (4, 4)
        HEADER_PADY = (6, 10)
        ROW_PADY    = 4

        # ── Header Row ────────────────────────────────────────────────────────
        for col, header in enumerate(headers):
            sticky = "" if col in (2, 4, 5, 6) else "w"
            ctk.CTkLabel(
                table,
                text=header,
                font=HEADER_FONT,
                text_color="#000000"
            ).grid(row=0, column=col, padx=PADX, pady=HEADER_PADY, sticky=sticky)

        sep = ctk.CTkFrame(table, height=1, fg_color="#E0E0E0")
        sep.grid(row=1, column=0, columnspan=len(headers), sticky="ew", padx=0, pady=0)

        reviews = [
            [
                "Jhay Del Socorro\nU001",
                "Oceanview\nRetreat",
                5,
                "Super clean and the owner is very\napproachable. WiFi is fast enough for\nonline classes. Highly recommend for\nPUP students!",
                "Active",
                "Jan 10,2026"
            ],
            [
                "Kyll Kouichi Harabe\nU002",
                "Oceanview\nRetreat",
                4,
                "Super clean and the owner is very\napproachable. WiFi is fast enough for\nonline classes. Highly recommend for\nPUP students!",
                "Pending",
                "Jan 12,2026"
            ],
            [
                "Mike Ulang\nU003",
                "Oceanview\nRetreat",
                3,
                "Super clean and the owner is very\napproachable. WiFi is fast enough for\nonline classes. Highly recommend for\nPUP students!",
                "Disabled",
                "Jan 16,2026"
            ],
        ]

        for r, row in enumerate(reviews, start=2):
            data_row = r * 2

            # ── Reviewer ──────────────────────────────────────────────────────
            ctk.CTkLabel(
                table, text=row[0], font=CELL_FONT, justify="left"
            ).grid(row=data_row, column=0, padx=PADX, pady=ROW_PADY, sticky="w")

            # ── Listing ───────────────────────────────────────────────────────
            ctk.CTkLabel(
                table, text=row[1], font=CELL_FONT, justify="left"
            ).grid(row=data_row, column=1, padx=PADX, pady=ROW_PADY, sticky="w")

            # ── Star Rating ───────────────────────────────────────────────────
            stars_frame = ctk.CTkFrame(table, fg_color="transparent")
            stars_frame.grid(row=data_row, column=2, padx=PADX, pady=ROW_PADY)

            for s in range(5):
                color = "#F5A623" if s < row[2] else "#CCCCCC"
                ctk.CTkLabel(
                    stars_frame,
                    text="★",
                    font=STAR_FONT,
                    text_color=color
                ).pack(side="left")

            # ── Review Text ───────────────────────────────────────────────────
            ctk.CTkLabel(
                table,
                text=row[3],
                font=CELL_FONT,
                justify="left",
                wraplength=160
            ).grid(row=data_row, column=3, padx=PADX, pady=ROW_PADY, sticky="w")

            # ── Status Badge ──────────────────────────────────────────────────
            ctk.CTkLabel(
                table,
                text=row[4],
                width=65, height=22,
                corner_radius=11,
                fg_color="#F2F2F2",
                text_color="#000000",
                font=CELL_FONT
            ).grid(row=data_row, column=4, padx=PADX, pady=ROW_PADY)

            # ── Date ──────────────────────────────────────────────────────────
            ctk.CTkLabel(
                table, text=row[5], font=CELL_FONT
            ).grid(row=data_row, column=5, padx=PADX, pady=ROW_PADY)

            # ── Actions ───────────────────────────────────────────────────────
            actions_frame = ctk.CTkFrame(table, fg_color="transparent")
            actions_frame.grid(row=data_row, column=6, padx=PADX, pady=ROW_PADY)

            status = row[4]

            ctk.CTkButton(
                actions_frame,
                text="👁",
                width=22, height=22,
                fg_color="transparent",
                hover_color="#F0F0F0",
                text_color="#333333",
                corner_radius=4,
                font=ICON_FONT
            ).pack(side="left", padx=1)

            if status == "Active":
                ctk.CTkButton(
                    actions_frame,
                    text="✎",
                    width=22, height=22,
                    fg_color="transparent",
                    hover_color="#F0F0F0",
                    text_color="#333333",
                    corner_radius=4,
                    font=ICON_FONT
                ).pack(side="left", padx=1)

                ctk.CTkButton(
                    actions_frame,
                    text="🗑",
                    width=22, height=22,
                    fg_color="transparent",
                    hover_color="#F0F0F0",
                    text_color="#333333",
                    corner_radius=4,
                    font=ICON_FONT
                ).pack(side="left", padx=1)

            elif status == "Pending":
                ctk.CTkButton(
                    actions_frame,
                    text="✓",
                    width=22, height=22,
                    fg_color="transparent",
                    hover_color="#F0F0F0",
                    text_color="#333333",
                    corner_radius=4,
                    font=ICON_FONT
                ).pack(side="left", padx=1)

                ctk.CTkButton(
                    actions_frame,
                    text="✗",
                    width=22, height=22,
                    fg_color="transparent",
                    hover_color="#F0F0F0",
                    text_color="#333333",
                    corner_radius=4,
                    font=ICON_FONT
                ).pack(side="left", padx=1)

            elif status == "Disabled":
                ctk.CTkButton(
                    actions_frame,
                    text="⊘",
                    width=22, height=22,
                    fg_color="transparent",
                    hover_color="#F0F0F0",
                    text_color="#333333",
                    corner_radius=4,
                    font=ICON_FONT
                ).pack(side="left", padx=1)

                ctk.CTkButton(
                    actions_frame,
                    text="🗑",
                    width=22, height=22,
                    fg_color="transparent",
                    hover_color="#F0F0F0",
                    text_color="#333333",
                    corner_radius=4,
                    font=ICON_FONT
                ).pack(side="left", padx=1)

            # ── Row divider ───────────────────────────────────────────────────
            if r < len(reviews) + 1:
                div = ctk.CTkFrame(table, height=1, fg_color="#E0E0E0")
                div.grid(row=data_row + 1, column=0,
                        columnspan=len(headers), sticky="ew", padx=0, pady=0)



    def show_reports(self):
        self.clear_container()
        self.geometry("1100x580")

        self.sidebar = ctk.CTkFrame(
            self.container,
            width=170,
            fg_color=self.sidebar_bg,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(
            self.container,
            fg_color=self.content_bg,
            corner_radius=0
        )
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar_reports()
        self._build_reports_content()

    def _build_sidebar_reports(self):
        logo = ctk.CTkLabel(
            self.sidebar,
            image=self.logo,
            text=""
        )
        logo.pack(pady=(30, 25))

        nav_items = [
            ("Dashboard", False),
            ("Manage Users", False),
            ("Manage\nBoarding Houses", False),
            ("Reviews & Feedback", False),
            ("Reports", True),
            ("Settings", False)
        ]

        for text, active in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=165,
                height=38,
                fg_color="#D4B183" if active else "transparent",
                hover_color="#D4B183",
                text_color="#222222",
                corner_radius=2,
                font=ctk.CTkFont(family="Poppins", size=13, weight="bold" if active else "normal")
            )
            btn.pack(pady=3)

        ctk.CTkLabel(self.sidebar, text="").pack(expand=True)

        ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="transparent",
            hover_color="#EFEFEF",
            text_color="#444444",
            font=ctk.CTkFont(family="Poppins", size=13)
        ).pack(pady=20)

    def _build_reports_content(self):
        topbar_frame = ctk.CTkFrame(
            self.content,
            height=55,
            fg_color="#FFFFFF",
            corner_radius=0
        )
        topbar_frame.pack(fill="x")
        topbar_frame.pack_propagate(False)

        # Thin bottom border line
        topbar_border = ctk.CTkFrame(
            topbar_frame,
            height=1,
            fg_color="#DEDEDE",
            corner_radius=0
        )
        topbar_border.pack(side="bottom", fill="x")

        # Right side: avatar circle + name + TID
        user_info_frame = ctk.CTkFrame(topbar_frame, fg_color="transparent")
        user_info_frame.pack(side="right", padx=20, pady=8)

        avatar_frame = ctk.CTkFrame(
            user_info_frame,
            width=36,
            height=36,
            corner_radius=18,
            fg_color=self.primary_color
        )
        avatar_frame.pack(side="left", padx=(0, 8))
        avatar_frame.pack_propagate(False)

        avatar_icon_label = ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=ctk.CTkFont(size=16),
            text_color="#FFFFFF"
        )
        avatar_icon_label.place(relx=0.5, rely=0.5, anchor="center")

        name_id_frame = ctk.CTkFrame(user_info_frame, fg_color="transparent")
        name_id_frame.pack(side="left")

        name_label = ctk.CTkLabel(
            name_id_frame,
            text="kamrul",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            text_color=self.text_color
        )
        name_label.pack(anchor="w")

        tid_label = ctk.CTkLabel(
            name_id_frame,
            text="TID: 23545",
            font=ctk.CTkFont(family="Poppins Light", size=10),
            text_color="#6B6B6B"
        )
        tid_label.pack(anchor="w")
        # ─────────────────────────────────────────────────────────────────────

        # ── Body ──────────────────────────────────────────────────────────────
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(
            body,
            text="REPORTS",
            font=ctk.CTkFont(family="Poppins", size=20, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        # ── Two-column layout ─────────────────────────────────────────────────
        columns = ctk.CTkFrame(body, fg_color="transparent")
        columns.pack(fill="both", expand=True)

        columns.grid_columnconfigure(0, weight=4)
        columns.grid_columnconfigure(1, weight=5)
        columns.grid_rowconfigure(0, weight=1)

        left_col = ctk.CTkFrame(columns, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right_col = ctk.CTkFrame(columns, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")

        self._build_summary_statistic(left_col)
        self._build_recent_reports(left_col)
        self._build_generate_reports(right_col)

    def _build_summary_statistic(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            card,
            text="Summary Statistic",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold")
        ).pack(anchor="w", padx=18, pady=(14, 8))

        stats = [
            ("Total Boarding Houses:",       "120"),
            ("Available Boarding Houses:",   "95"),
            ("Occupied Boarding Houses:",    "25"),
            ("Total Registered Users:",      "350"),
        ]

        for label, value in stats:
            row_frame = ctk.CTkFrame(card, fg_color="transparent")
            row_frame.pack(fill="x", padx=18, pady=(6, 0))

            ctk.CTkLabel(
                row_frame,
                text=label,
                font=ctk.CTkFont(family="Poppins Light", size=10),
                text_color="#333333"
            ).pack(side="left")

            ctk.CTkLabel(
                row_frame,
                text=value,
                font=ctk.CTkFont(family="Poppins Light", size=10),
                text_color="#333333"
            ).pack(side="right")

            div = ctk.CTkFrame(card, height=1, fg_color="#E0E0E0")
            div.pack(fill="x", padx=18, pady=(8, 0))

        ctk.CTkLabel(card, text="", height=10).pack()

    def _build_recent_reports(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(fill="x")

        ctk.CTkLabel(
            card,
            text="Recent Reports",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold")
        ).pack(anchor="w", padx=18, pady=(14, 8))

        recent = [
            ("Boarding House Report", "Aug 10, 2026"),
            ("User Report",           "Aug 08, 2026"),
            ("Occupany Report",       "Aug 01, 2026"),
        ]

        for name, date in recent:
            row_frame = ctk.CTkFrame(card, fg_color="transparent")
            row_frame.pack(fill="x", padx=18, pady=(6, 0))

            ctk.CTkLabel(
                row_frame,
                text=name,
                font=ctk.CTkFont(family="Poppins Light", size=10),
                text_color="#333333"
            ).pack(side="left")

            ctk.CTkLabel(
                row_frame,
                text=date,
                font=ctk.CTkFont(family="Poppins Light", size=10),
                text_color="#333333"
            ).pack(side="right")

            div = ctk.CTkFrame(card, height=1, fg_color="#E0E0E0")
            div.pack(fill="x", padx=18, pady=(8, 0))

        ctk.CTkLabel(card, text="", height=10).pack()

    def _build_generate_reports(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            card,
            text="Generate Reports",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold")
        ).pack(anchor="w", padx=18, pady=(14, 10))

        report_types = [
            "Boarding House Report",
            "User Report",
            "Occupany Report",
        ]

        for report_name in report_types:
            ctk.CTkLabel(
                card,
                text=report_name,
                font=ctk.CTkFont(family="Poppins Light", size=10),
                text_color="#333333"
            ).pack(anchor="w", padx=18, pady=(6, 4))

            box = ctk.CTkFrame(
                card,
                fg_color="#E8E8E8",
                corner_radius=6,
                height=65
            )
            box.pack(fill="x", padx=18, pady=(0, 10))
            box.pack_propagate(False)

        ctk.CTkLabel(card, text="", height=5).pack()


if __name__ == "__main__":
    app = BoardingHouseApp()
    app.mainloop()