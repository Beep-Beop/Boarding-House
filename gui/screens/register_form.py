import customtkinter as ctk
from CTkScrollableDropdown import CTkScrollableDropdown
import threading
import datetime
from src.logger import logger


class RegisterFormMixin:
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
        if hasattr(self, "_email_check_timer") and self._email_check_timer:
            self.after_cancel(self._email_check_timer)
        self._email_check_timer = None

        # Main Container
        self.form_container = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        self.form_container.bind_all("<Button-4>", lambda e: self.form_container._parent_canvas.yview("scroll", -1, "units") if hasattr(self.form_container, "_parent_canvas") else None)
        self.form_container.bind_all("<Button-5>", lambda e: self.form_container._parent_canvas.yview("scroll", 1, "units") if hasattr(self.form_container, "_parent_canvas") else None)

        self._build_navbar()
        self._build_personal_section()
        self._build_location_section()
        self._build_security_section()

        self._screen_active = True
        self.load_provinces()

    def _build_navbar(self):
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
                                   text_color=self.text_color
                                   )
        notes_label.pack(anchor="w", padx=90)

    def _build_personal_section(self):
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
        first_name_frame.pack(pady=(0, 5))

        self.first_name_label = ctk.CTkLabel(first_name_frame,
                                         text="First Name",
                                         font=self.body_light_font,
                                         text_color=self.text_color
                                         )
        self.first_name_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        self.first_name_bg_frame = ctk.CTkFrame(first_name_frame,
                                       width=430,
                                       height=40,
                                       fg_color=self.fg_color,
                                       border_color=self.entry_border,
                                       border_width=1,
                                       corner_radius=6
                                       )
        self.first_name_bg_frame.pack()
        self.first_name_bg_frame.pack_propagate(False)
        self.first_name_error_lbl = ctk.CTkLabel(first_name_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
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
                                           fg_color=self.fg_color,
                                           border_color=self.entry_border,
                                           border_width=1,
                                           corner_radius=6
                                           )
        self.last_name_bg_frame.pack()
        self.last_name_bg_frame.pack_propagate(False)
        self.last_name_error_lbl = ctk.CTkLabel(last_name_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
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
        dob_frame.pack(anchor="w", fill="x", pady=(0, 15))

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
        self.dob_error_lbl = ctk.CTkLabel(dob_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
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
        self.month_box._entry.bind("<Key>", lambda e: None if e.keysym == "Tab" else "break")
        self.month_box.pack(side="left", padx=(35, 10), pady=8)

        ctk.CTkLabel(self.dob_bg_frame,
                     text="/",
                     text_color=self.text_color,
                     width=10
                     ).pack(side="left", padx=(25, 20))

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
        self.day_box._entry.bind("<Key>", lambda e: None if e.keysym == "Tab" else "break")
        self.day_box.pack(side="left", pady=8, padx=(0, 5))

        ctk.CTkLabel(self.dob_bg_frame,
                     text="/",
                     text_color=self.text_color,
                     width=10
                     ).pack(side="left", padx=(30, 25))

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
        self.year_box._entry.bind("<Key>", lambda e: None if e.keysym == "Tab" else "break")
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
        self.email_error_lbl = ctk.CTkLabel(self.email_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
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
        self.phone_error_lbl = ctk.CTkLabel(phone_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
        self.phone_error_lbl.pack(anchor="w", padx=15)

        self.phone_entry = ctk.CTkEntry(self.phone_bg_frame,
                                        height=30,
                                        font=self.body_light_font,
                                        fg_color="transparent",
                                        border_width=0,
                                        text_color=self.text_color,
                                        placeholder_text="Enter your mobile number"
                                        )
        self.phone_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        self.phone_entry.bind("<KeyRelease>", self.validate_phone_realtime)

    def _build_location_section(self):
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
        self.province_error_lbl = ctk.CTkLabel(province_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
        self.province_error_lbl.pack(anchor="w", padx=15)

        def _province_blur(e=None):
            def check():
                val = self.province_menu.get().strip()
                opts = getattr(self, "province_options", [])
                if opts and val and val not in opts and not val.startswith("Select"):
                    self.province_menu.set("Select Province...")
            self.after(300, check)
        self.province_menu._entry.bind("<FocusOut>", _province_blur, add="+")

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
        self.city_menu.set("Select City...")

        self.city_dropdown = CTkScrollableDropdown(self.city_menu,
                                                   values=["Select City..."],
                                                   autocomplete=True,
                                                   command=self.on_city_selected
                                                   )
        self.city_error_lbl = ctk.CTkLabel(city_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
        self.city_error_lbl.pack(anchor="w", padx=15)

        def _city_blur(e=None):
            def check():
                val = self.city_menu.get().strip()
                opts = getattr(self, "city_options", [])
                if opts and val and val not in opts and not val.startswith("Select") and not val.startswith("Loading") and not val.startswith("No "):
                    self.city_menu.set("Select City...")
            self.after(300, check)
        self.city_menu._entry.bind("<FocusOut>", _city_blur, add="+")

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
        self.barangay_menu.set("Select Barangay...")

        self.barangay_dropdown = CTkScrollableDropdown(self.barangay_menu,
                                                       values=["Select Barangay..."],
                                                       autocomplete=True,
                                                       command=lambda choice: [self.barangay_menu.set(choice), setattr(self, 'selected_barangay', choice)]
                                                       )
        self.barangay_error_lbl = ctk.CTkLabel(barangay_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
        self.barangay_error_lbl.pack(anchor="w", padx=15)

        def _barangay_blur(e=None):
            def check():
                val = self.barangay_menu.get().strip()
                opts = getattr(self, "barangay_options", [])
                if opts and val and val not in opts and not val.startswith("Select") and not val.startswith("Loading") and not val.startswith("No "):
                    self.barangay_menu.set("Select Barangay...")
            self.after(300, check)
        self.barangay_menu._entry.bind("<FocusOut>", _barangay_blur, add="+")

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
        self.street_error_lbl = ctk.CTkLabel(street_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
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

    def _build_security_section(self):
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
        self.create_pass_error_lbl = ctk.CTkLabel(create_pass_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
        self.create_pass_error_lbl.pack(anchor="w", padx=15)

        req_frame = ctk.CTkFrame(create_pass_frame, fg_color="transparent")
        req_frame.pack(anchor="w", padx=15, pady=(2, 4))

        self.req_length  = ctk.CTkLabel(req_frame, text="\u2717  8+ characters",    font=self.inline_error_font, text_color=self.entry_border)
        self.req_upper   = ctk.CTkLabel(req_frame, text="\u2717  Uppercase letter",  font=self.inline_error_font, text_color=self.entry_border)
        self.req_number  = ctk.CTkLabel(req_frame, text="\u2717  Number",            font=self.inline_error_font, text_color=self.entry_border)
        self.req_special = ctk.CTkLabel(req_frame, text="\u2717  Special character", font=self.inline_error_font, text_color=self.entry_border)

        self.req_length.grid( row=0, column=0, sticky="w", padx=(0, 20), pady=1)
        self.req_upper.grid(  row=0, column=1, sticky="w",               pady=1)
        self.req_number.grid( row=1, column=0, sticky="w", padx=(0, 20), pady=1)
        self.req_special.grid(row=1, column=1, sticky="w",               pady=1)

        self.create_pass_entry = ctk.CTkEntry(self.create_pass_bg_frame,
                                              placeholder_text="Min of 8 Characters",
                                              height=30,
                                              show="\u2022",
                                              font=self.body_light_font,
                                              fg_color="transparent",
                                              border_width=0,
                                              text_color=self.text_color
                                              )
        self.create_pass_entry.place(relx=0.46, rely=0.5, relwidth=0.82, anchor="center")

        self.create_pass_eye = ctk.CTkLabel(self.create_pass_bg_frame,
                                            image=self.closed_eye_icon,
                                            text="",
                                            cursor="hand2",
                                            )
        self.create_pass_eye.place(relx=0.9, rely=0.5, anchor="center")

        def _toggle_create_pass(e):
            self._create_pass_visible = not getattr(self, "_create_pass_visible", False)
            if self._create_pass_visible:
                self.create_pass_entry.configure(show="")
                self._animate_eye(self.create_pass_eye, self._eye_frames_open)
            else:
                self.create_pass_entry.configure(show="\u2022")
                self._animate_eye(self.create_pass_eye, self._eye_frames_closed)
        self.create_pass_eye.bind("<Button-1>", _toggle_create_pass)

        def _on_pass_key(e=None):
            self.validate_password_strength_realtime()
            self.validate_password_match_realtime()
        self.create_pass_entry.bind("<KeyRelease>", _on_pass_key)

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
        self.confirm_pass_error_lbl = ctk.CTkLabel(confirm_pass_frame, text="", height=14, font=self.inline_error_font, text_color=self.error_red)
        self.confirm_pass_error_lbl.pack(anchor="w", padx=15)

        self.confirm_pass_entry = ctk.CTkEntry(self.confirm_pass_bg_frame,
                                               placeholder_text="Re-enter your password",
                                               height=30,
                                               show="\u2022",
                                               font=self.body_light_font,
                                               fg_color="transparent",
                                               border_width=0,
                                               text_color=self.text_color
                                               )
        self.confirm_pass_entry.place(relx=0.46, rely=0.5, relwidth=0.82, anchor="center")

        self.confirm_pass_eye = ctk.CTkLabel(self.confirm_pass_bg_frame,
                                             image=self.closed_eye_icon,
                                             text="",
                                             cursor="hand2",
                                             )
        self.confirm_pass_eye.place(relx=0.9, rely=0.5, anchor="center")

        def _toggle_confirm_pass(e):
            self._confirm_pass_visible = not getattr(self, "_confirm_pass_visible", False)
            if self._confirm_pass_visible:
                self.confirm_pass_entry.configure(show="")
                self._animate_eye(self.confirm_pass_eye, self._eye_frames_open)
            else:
                self.confirm_pass_entry.configure(show="\u2022")
                self._animate_eye(self.confirm_pass_eye, self._eye_frames_closed)
        self.confirm_pass_eye.bind("<Button-1>", _toggle_confirm_pass)

        self.confirm_pass_entry.bind("<KeyRelease>", self.validate_password_match_realtime)

        self.tos_frame = ctk.CTkFrame(self.form_container,
                                      fg_color="transparent"
                                      )
        self.tos_frame.pack(anchor="center", pady=(5, 0), padx=100)

        self.tos_and_pp_checkbox = ctk.CTkCheckBox(self.tos_frame,
                                                   text="I agree to BHFinder\u2019s",
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

        tos_lbl_and_pp_frame = ctk.CTkFrame(self.form_container,
                                            fg_color="transparent"
                                            )
        tos_lbl_and_pp_frame.pack(anchor="center")

        self.tos_and_lbl = ctk.CTkLabel(tos_lbl_and_pp_frame,
                                        text="and",
                                        font=self.body_paragraph_font,
                                        text_color=self.text_color
                                        )
        self.tos_and_lbl.grid(row=1, column=1, padx=(2, 2), sticky="w")

        self.pp_link_btn = ctk.CTkButton(tos_lbl_and_pp_frame,
                                         text="Privacy Policy",
                                         font=self.body_paragraph_font,
                                         text_color=self.primary_color,
                                         fg_color="transparent",
                                         hover=False,
                                         width=0,
                                         height=20,
                                         command=self.open_privacy_policy
                                         )
        self.pp_link_btn.grid(row=1, column=2, padx=2, sticky="w")

        self.tos_error_lbl = ctk.CTkLabel(self.form_container,
                                          text="",
                                          font=self.inline_error_font,
                                          text_color=self.error_red
                                          )
        self.tos_error_lbl.pack(anchor="w", padx=120, pady=(2, 10))

        self.create_acc_btn = ctk.CTkButton(self.form_container,
                                             text="CREATE ACCOUNT",
                                             width=430,
                                             height=45,
                                             corner_radius=6,
                                             font=self.body_bold_font,
                                             fg_color=self.primary_color,
                                             hover_color=self.hover_color,
                                             text_color="#FFFFFF",
                                             command=self.attempt_register
                                             )
        self.create_acc_btn.pack(pady=(10, 40))

    def load_provinces(self):
        cached = getattr(self, "_cached_provinces", None)
        if cached is not None:
            self.province_options = cached
            if cached and hasattr(self, "province_dropdown") and self.province_menu.winfo_exists():
                self.province_dropdown.configure(values=cached)
            self._cached_provinces = None
            return

        def fetch():
            if not self._screen_active:
                return
            try:
                response = self.api.get("/locations/provinces")
                if response.status_code == 200:
                    options = response.json().get("options", [])
                    self.province_options = options
                    if options and hasattr(self, "province_dropdown") and self.province_menu.winfo_exists():
                        def update():
                            if not self._screen_active:
                                return
                            self.province_dropdown.configure(values=options)
                        self.after(0, update)
            except Exception as e:
                logger.error("Network error loading provinces: %s", e)

        threading.Thread(target=fetch, daemon=True).start()

    def on_province_selected(self, choice):
        if not choice or not choice.strip() or choice.startswith("Select"):
            return

        self.selected_province = choice
        self.province_menu.set(choice)

        self.barangay_menu.set("Select Barangay...")
        self.barangay_dropdown.configure(values=["Select Barangay..."])
        self.barangay_options = []

        self.city_menu.set("Loading cities...")
        self.city_dropdown.configure(values=["Loading..."])
        self.city_options = []

        def fetch():
            if not self._screen_active:
                return
            try:
                response = self.api.get(f"/locations/cities?province={choice}")
                if response.status_code == 200:
                    options = response.json().get("options", [])
                    self.city_options = options

                    def update():
                        if not self._screen_active:
                            return
                        if hasattr(self, "city_dropdown") and self.city_menu.winfo_exists():
                            self.city_dropdown.configure(values=options)
                            if options:
                                self.city_menu.set("")
                            else:
                                self.city_menu.set("No Cities Found")
                    self.after(0, update)
            except Exception as e:
                logger.error("Network error loading cities: %s", e)

        threading.Thread(target=fetch, daemon=True).start()

    def on_city_selected(self, choice):
        if not choice or not choice.strip() or choice.startswith("Select") or choice.startswith("Loading"):
            return

        self.selected_city = choice
        self.city_menu.set(choice)

        self.barangay_menu.set("Loading Barangays...")
        self.barangay_dropdown.configure(values=["Loading..."])

        def fetch():
            if not self._screen_active:
                return
            try:
                response = self.api.get(f"/locations/barangays?city={choice}")
                if response.status_code == 200:
                    options = response.json().get("options", [])
                    self.barangay_options = options

                    def update():
                        if not self._screen_active:
                            return
                        if hasattr(self, "barangay_dropdown") and self.barangay_menu.winfo_exists():
                            self.barangay_dropdown.configure(values=options)
                            if options:
                                self.barangay_menu.set("")
                            else:
                                self.barangay_menu.set("No Barangay Found")
                    self.after(0, update)
            except Exception as e:
                logger.error("Network error loading barangay: %s", e)

        threading.Thread(target=fetch, daemon=True).start()

    def open_terms_of_service(self):
        import webbrowser
        webbrowser.open("https://beepboops.app/terms")

    def open_privacy_policy(self):
        import webbrowser
        webbrowser.open("https://beepboops.app/privacy")
