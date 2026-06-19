import threading
import customtkinter as ctk


class AccountTypeMixin:
    def show_account_type(self):
        print("[DEBUG] Showing: Account Type Selection")
        self.clear_container()

        self.geometry("1200x700")
        self.resizable(False, False)

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

        # Student
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
                                    text="Student",
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
                                       border_color=self.entry_border,
                                       fg_color="transparent"
                                       )
        self.tenant_dot.grid(row=0, column=2, padx=(0, 15), pady=(15, 0), sticky="ne")

        for widget in (self.tenant_card, tenant_icon_lbl, tenant_title, tenant_desc, self.tenant_dot):
            widget.bind("<Button-1>", lambda event: self.select_account_type("student"))
            widget.configure(cursor="hand2")

        # Owner
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
                                      text="Owner",
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
                                         border_color=self.entry_border,
                                         fg_color="transparent"
                                         )
        self.landlord_dot.grid(row=0, column=2, padx=(0, 15), pady=(15, 0), sticky="ne")

        for widget in (self.landlord_card, landlord_icon_lbl, landlord_title, landlord_desc, self.landlord_dot):
            widget.bind("<Button-1>", lambda event: self.select_account_type("owner"))
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

    def select_account_type(self, account_type):
        self.selected_account_type = account_type

        active_border = self.primary_color
        inactive_border = self.entry_border

        if account_type == "student":
            self.tenant_card.configure(border_color=active_border)
            self.tenant_dot.configure(fg_color=active_border)

            self.landlord_card.configure(border_color=inactive_border)
            self.landlord_dot.configure(fg_color="transparent")
        elif account_type == "owner":
            self.landlord_card.configure(border_color=active_border)
            self.landlord_dot.configure(fg_color=active_border)

            self.tenant_card.configure(border_color=inactive_border)
            self.tenant_dot.configure(fg_color="transparent")

    def handle_account_type_submit(self):
        if not getattr(self, "selected_account_type", None):
            self.show_toast("Please select an account type to continue.", is_error=True)
            return

        self.show_register_skeleton()

    def show_google_account_type(self, user_info):
        print("[DEBUG] Showing: Google Account Type Selection")
        self.show_account_type()
        self._google_user_info = user_info
        self.next_step_btn.configure(text="FINISH", command=self._finish_google_signup)

    def _finish_google_signup(self):
        role = getattr(self, "selected_account_type", None)
        if not role:
            self.show_toast("Please select an account type to continue.", is_error=True)
            return

        user_info = getattr(self, "_google_user_info", {})
        user_id = user_info.get("user_id")
        if not user_id:
            self.show_toast("Session error. Please log in again.", is_error=True)
            return

        def _do():
            try:
                resp = self.api.patch(f"/users/{user_id}", json={"role": role, "account_setup_complete": True})
                if resp.status_code == 200:
                    self.current_user["role"] = role
                    self.current_user["account_setup_complete"] = True
                    self._save_session(self.current_user)
                    self.after(0, lambda: self._finish_google_signup_ui(role))
                else:
                    self.after(0, lambda: self.show_toast("Failed to save account type. Try again.", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server.", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def _finish_google_signup_ui(self, role):
        self.show_toast(f"Account set up as {role}!", is_error=False)
        if role == "owner":
            self.show_owner_dashboard()
        else:
            self.show_tenant_dashboard()
