import customtkinter as ctk


class ChangePasswordMixin:
    def show_change_password_page(self):
        self.clear_container()
        self.geometry("630x700")

        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=40, fill="both", expand=True)

        bk_btn_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        bk_btn_frame.pack(fill="x", pady=(15, 0))

        back_btn = ctk.CTkLabel(bk_btn_frame, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left", padx=(15, 0))
        back_btn.bind("<Button-1>", lambda event: self._back_to_dashboard())

        title_label = ctk.CTkLabel(self.form_container, text="CHANGE PASSWORD",
                                    font=self.alt_title_font, text_color=self.text_color)
        title_label.pack(pady=(20, 20))

        fields_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        fields_frame.pack(pady=10)

        # Current Password
        ctk.CTkLabel(fields_frame, text="Current Password", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", padx=(15, 0), pady=(0, 5))
        self.old_pw_entry = ctk.CTkEntry(fields_frame, width=400, height=40,
                                         font=self.body_light_font,
                                         fg_color=self.fg_color, border_color=self.entry_border,
                                         border_width=1, corner_radius=6,
                                         text_color=self.text_color, show="\u2022")
        self.old_pw_entry.pack(pady=(0, 15))

        # New Password
        ctk.CTkLabel(fields_frame, text="New Password", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", padx=(15, 0), pady=(0, 5))
        self.new_pw_entry = ctk.CTkEntry(fields_frame, width=400, height=40,
                                         font=self.body_light_font,
                                         fg_color=self.fg_color, border_color=self.entry_border,
                                         border_width=1, corner_radius=6,
                                         text_color=self.text_color, show="\u2022")
        self.new_pw_entry.pack(pady=(0, 15))

        # Confirm New Password
        ctk.CTkLabel(fields_frame, text="Confirm New Password", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", padx=(15, 0), pady=(0, 5))
        self.confirm_pw_entry = ctk.CTkEntry(fields_frame, width=400, height=40,
                                             font=self.body_light_font,
                                             fg_color=self.fg_color, border_color=self.entry_border,
                                             border_width=1, corner_radius=6,
                                             text_color=self.text_color, show="\u2022")
        self.confirm_pw_entry.pack(pady=(0, 15))

        self.change_pw_btn = ctk.CTkButton(self.form_container, text="CHANGE PASSWORD",
                                 width=400, height=45, corner_radius=6,
                                 font=self.body_bold_font,
                                 fg_color=self.primary_color, hover_color=self.hover_color,
                                 text_color="#FFFFFF", command=self._change_password)
        self.change_pw_btn.pack(pady=(20, 10))

        self.pw_error = ctk.CTkLabel(self.form_container, text="",
                                     text_color=self.error_red,
                                     font=self.inline_error_font)
        self.pw_error.pack()

    def _change_password(self):
        old_pw = self.old_pw_entry.get()
        new_pw = self.new_pw_entry.get()
        confirm_pw = self.confirm_pw_entry.get()

        if not old_pw or not new_pw or not confirm_pw:
            self.pw_error.configure(text="All fields are required")
            return

        if new_pw != confirm_pw:
            self.pw_error.configure(text="New passwords do not match")
            return

        if len(new_pw) < 8:
            self.pw_error.configure(text="New password must be at least 8 characters")
            return

        self.change_pw_btn.configure(state="disabled", text="CHANGING...")
        try:
            resp = self.api.post("/auth/change-password", json={
                "old_password": old_pw,
                "new_password": new_pw
            }, timeout=10)
            if resp.status_code == 200:
                self.show_toast("Password changed successfully!", is_error=False)
                self._back_to_dashboard()
            else:
                self.pw_error.configure(text=resp.json().get("detail", "Failed to change password"))
        except Exception:
            self.pw_error.configure(text="Cannot connect to server")
        finally:
            self.change_pw_btn.configure(state="normal", text="CHANGE PASSWORD")

    def _back_to_dashboard(self):
        role = getattr(self, 'current_user', {}).get('role')
        if role == 'owner':
            self.show_owner_dashboard()
        else:
            self.show_tenant_dashboard()