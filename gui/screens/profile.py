import customtkinter as ctk
from datetime import datetime


class ProfileMixin:
    def show_profile_page(self):
        self.clear_container()
        self.geometry("630x700")

        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=40, fill="both", expand=True)

        # Back button
        bk_btn_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        bk_btn_frame.pack(fill="x", pady=(15, 0))

        back_btn = ctk.CTkLabel(bk_btn_frame, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left", padx=(15, 0))
        back_btn.bind("<Button-1>", lambda event: self._back_to_dashboard())

        # Title
        title_label = ctk.CTkLabel(self.form_container, text="EDIT PROFILE",
                                    font=self.alt_title_font, text_color=self.text_color)
        title_label.pack(pady=(20, 20))

        # Fetch current user data
        user_id = getattr(self, 'current_user', {}).get('user_id')
        user_data = {}
        if user_id:
            try:
                resp = self.api.get(f"/users/{user_id}", timeout=5)
                if resp.status_code == 200:
                    user_data = resp.json()
            except Exception:
                pass

        fields_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        fields_frame.pack(pady=10)

        def make_field(label, key, default=""):
            row = ctk.CTkFrame(fields_frame, fg_color="transparent")
            row.pack(pady=(0, 15))

            ctk.CTkLabel(row, text=label, font=self.body_light_font,
                         text_color=self.text_color).pack(anchor="w", padx=(15, 0), pady=(0, 5))

            entry = ctk.CTkEntry(row, width=400, height=40,
                                 font=self.body_light_font,
                                 fg_color=self.fg_color, border_color=self.entry_border,
                                 border_width=1, corner_radius=6,
                                 text_color=self.text_color)
            entry.pack()
            entry.insert(0, str(user_data.get(key, default)))
            return entry

        self.name_entry = make_field("Name", "name")
        self.phone_entry = make_field("Phone", "phone")
        self.street_entry = make_field("Street Address", "street")

        # Date of Birth
        dob_row = ctk.CTkFrame(fields_frame, fg_color="transparent")
        dob_row.pack(pady=(0, 15))

        ctk.CTkLabel(dob_row, text="Date of Birth", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", padx=(15, 0), pady=(0, 5))

        self.dob_entry = ctk.CTkEntry(dob_row, width=400, height=40,
                                      font=self.body_light_font,
                                      fg_color=self.fg_color, border_color=self.entry_border,
                                      border_width=1, corner_radius=6,
                                      text_color=self.text_color,
                                      placeholder_text="YYYY-MM-DD")
        self.dob_entry.pack()
        dob_val = user_data.get("date_of_birth")
        if dob_val:
            self.dob_entry.insert(0, str(dob_val))

        # Save button
        self.save_btn = ctk.CTkButton(self.form_container, text="SAVE CHANGES",
                                 width=400, height=45, corner_radius=6,
                                 font=self.body_bold_font,
                                 fg_color=self.primary_color, hover_color=self.hover_color,
                                 text_color="#FFFFFF", command=self._save_profile)
        self.save_btn.pack(pady=(20, 10))
        save_btn.pack(pady=(20, 10))

        self.profile_error = ctk.CTkLabel(self.form_container, text="",
                                          text_color=self.error_red,
                                          font=self.inline_error_font)
        self.profile_error.pack()

    def _save_profile(self):
        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            self.profile_error.configure(text="Not logged in")
            return

        payload = {}
        name = self.name_entry.get().strip()
        if name:
            payload["name"] = name
        phone = self.phone_entry.get().strip()
        if phone:
            payload["phone"] = phone
        street = self.street_entry.get().strip()
        if street:
            payload["street"] = street
        dob = self.dob_entry.get().strip()
        if dob:
            try:
                datetime.strptime(dob, "%Y-%m-%d")
                payload["date_of_birth"] = dob
            except ValueError:
                self.profile_error.configure(text="Invalid date format. Use YYYY-MM-DD")
                return

        self.save_btn.configure(state="disabled", text="SAVING...")
        try:
            resp = self.api.patch(f"/users/{user_id}", json=payload, timeout=10)
            if resp.status_code == 200:
                updated = resp.json()
                if self.current_user:
                    self.current_user["name"] = updated.get("name", self.current_user.get("name"))
                self.show_toast("Profile updated!", is_error=False)
                self._back_to_dashboard()
            else:
                self.profile_error.configure(text=resp.json().get("detail", "Update failed"))
        except Exception:
            self.profile_error.configure(text="Cannot connect to server")
        finally:
            self.save_btn.configure(state="normal", text="SAVE CHANGES")

    def _back_to_dashboard(self):
        role = getattr(self, 'current_user', {}).get('role')
        if role == 'owner':
            self.show_owner_dashboard()
        else:
            self.show_tenant_dashboard()