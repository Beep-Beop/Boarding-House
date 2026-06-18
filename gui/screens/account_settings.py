import customtkinter as ctk
import threading
from PIL import Image
import io
import re
from tkinter import filedialog, messagebox
import os
from datetime import datetime
from customtkinter import CTkInputDialog


class AccountSettingsMixin:

    def show_account_settings(self):
        """Build the unified Account Settings overlay with CTkTabview."""
        # Determine which container to use (same pattern as existing overlays)
        container = getattr(self, 'form_container', None) or \
                    getattr(self, '_admin_form_container', None) or \
                    self.container

        # Destroy any existing overlay
        self._close_account_overlay()

        # Outer overlay
        overlay = ctk.CTkFrame(container, fg_color=self.fg_color)
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.lift()
        self._account_overlay = overlay

        # Card
        card = ctk.CTkFrame(overlay, fg_color=self.secondary_color,
                            corner_radius=12, border_width=1,
                            border_color=self.entry_border)
        card.pack(fill="both", expand=True, padx=40, pady=40)

        # Close button
        close_btn = ctk.CTkButton(card, text="✕", width=32, height=32,
                                  fg_color="transparent",
                                  text_color=self.text_color,
                                  hover_color=self.hover_color,
                                  command=self._close_account_overlay)
        close_btn.place(x=12, y=12)

        # Title
        title = ctk.CTkLabel(card, text="ACCOUNT SETTINGS",
                             font=self.alt_title_font,
                             text_color=self.text_color)
        title.pack(pady=(20, 10))

        # Determine tabs based on role
        role = getattr(self.current_user, 'role', None) or \
               (self.current_user or {}).get('role', 'student')

        if role == "admin":
            tab_names = ["Profile", "Security"]
        elif role == "owner":
            tab_names = ["Profile", "Security", "Documents"]
        else:
            tab_names = ["Profile", "Security", "Verification"]

        # Tabview
        tabview = ctk.CTkTabview(card, fg_color="transparent",
                                 segmented_button_fg_color=self.fg_color,
                                 segmented_button_selected_color=self.primary_color,
                                 segmented_button_unselected_color=self.hover_color_text,
                                 text_color=self.text_color)
        tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Create tabs
        self._account_tabs = {}
        for name in tab_names:
            tab = tabview.add(name)
            tab_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
            tab_scroll.pack(fill="both", expand=True)
            self._account_tabs[name] = tab_scroll

        # Build tab contents
        self._build_profile_tab(self._account_tabs["Profile"])
        self._build_security_tab(self._account_tabs["Security"])
        if "Verification" in self._account_tabs:
            self._build_verification_tab(self._account_tabs["Verification"])
        if "Documents" in self._account_tabs:
            self._build_documents_tab(self._account_tabs["Documents"])

    def _close_account_overlay(self):
        """Destroy the account settings overlay."""
        if hasattr(self, '_account_overlay') and self._account_overlay:
            try:
                self._account_overlay.destroy()
            except Exception:
                pass
            self._account_overlay = None

    def _build_profile_tab(self, parent):
        """Build the Profile tab — shared across all roles."""
        user = getattr(self, 'current_user', {}) or {}

        # ── Avatar Section ──────────────────────────────────────────
        avatar_row = ctk.CTkFrame(parent, fg_color="transparent")
        avatar_row.pack(fill="x", pady=(10, 15))

        # Left: avatar
        avatar_frame = ctk.CTkFrame(avatar_row, fg_color="transparent", width=120)
        avatar_frame.pack(side="left", fill="y")
        avatar_frame.pack_propagate(False)

        self._profile_avatar = ctk.CTkLabel(avatar_frame, text="",
                                            image=self.pfp_placeholder,
                                            width=80, height=80,
                                            corner_radius=40,
                                            fg_color=self.fg_color)
        self._profile_avatar.pack(pady=(0, 5))

        edit_photo_btn = ctk.CTkButton(avatar_frame, text="Edit",
                                       font=self.body_description_font,
                                       fg_color="transparent",
                                       text_color=self.primary_color,
                                       hover_color=self.hover_color,
                                       command=self._pick_profile_photo)
        edit_photo_btn.pack()

        # Right: name + email + badges
        info_frame = ctk.CTkFrame(avatar_row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=(15, 0))

        name = user.get('name', 'User')
        email = user.get('email', '')
        role = user.get('role', 'student').capitalize()
        email_verified = user.get('email_verified', False)
        auth_provider = user.get('auth_provider', 'email')

        ctk.CTkLabel(info_frame, text=name,
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=email,
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w")

        # Badges row
        badges_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        badges_frame.pack(anchor="w", pady=(4, 0))

        # Role badge
        ctk.CTkLabel(badges_frame, text=role,
                     font=self.body_description_font,
                     fg_color=self.primary_color,
                     text_color=("white", "white"),
                     corner_radius=4, padx=6).pack(side="left", padx=(0, 4))

        # Email verified badge
        if email_verified:
            ctk.CTkLabel(badges_frame, text="✓ Email Verified",
                         font=self.body_description_font,
                         fg_color=("#2E7D32", "#4CAF50"), text_color=("white", "white"),
                         corner_radius=4, padx=6).pack(side="left", padx=(0, 4))
        else:
            ctk.CTkLabel(badges_frame, text="○ Unverified",
                         font=self.body_description_font,
                         fg_color=self.hover_color, text_color=("white", "white"),
                         corner_radius=4, padx=6).pack(side="left", padx=(0, 4))

        # Auth provider badge
        provider_text = auth_provider.replace('_', ' ').title()
        ctk.CTkLabel(badges_frame, text=provider_text,
                     font=self.body_description_font,
                     fg_color=self.hover_color, text_color=("white", "white"),
                     corner_radius=4, padx=6).pack(side="left")

        # ── Separator ───────────────────────────────────────────────
        ctk.CTkFrame(parent, height=1, fg_color=self.entry_border).pack(
            fill="x", padx=10, pady=5)

        # ── Personal Information Section ────────────────────────────
        ctk.CTkLabel(parent, text="Personal Information",
                     font=self.body_paragraph_font,
                     text_color=self.primary_color).pack(anchor="w", padx=10, pady=(10, 5))

        # Full Name
        name_frame = ctk.CTkFrame(parent, fg_color="transparent")
        name_frame.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(name_frame, text="Full Name",
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        self._profile_name_entry = ctk.CTkEntry(name_frame, width=480, height=38,
                                                font=self.body_light_font,
                                                fg_color=self.fg_color,
                                                border_color=self.entry_border,
                                                border_width=1, corner_radius=6,
                                                text_color=self.text_color,
                                                placeholder_text="John Doe")
        self._profile_name_entry.pack()
        self._profile_name_entry.insert(0, user.get('name', ''))

        # Phone
        phone_frame = ctk.CTkFrame(parent, fg_color="transparent")
        phone_frame.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(phone_frame, text="Phone Number",
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        self._profile_phone_entry = ctk.CTkEntry(phone_frame, width=480, height=38,
                                                 font=self.body_light_font,
                                                 fg_color=self.fg_color,
                                                 border_color=self.entry_border,
                                                 border_width=1, corner_radius=6,
                                                 text_color=self.text_color,
                                                 placeholder_text="+63 912 345 6789")
        self._profile_phone_entry.pack()
        self._profile_phone_entry.insert(0, user.get('phone', ''))

        # Street
        street_frame = ctk.CTkFrame(parent, fg_color="transparent")
        street_frame.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(street_frame, text="Street Address",
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        self._profile_street_entry = ctk.CTkEntry(street_frame, width=480, height=38,
                                                  font=self.body_light_font,
                                                  fg_color=self.fg_color,
                                                  border_color=self.entry_border,
                                                  border_width=1, corner_radius=6,
                                                  text_color=self.text_color,
                                                  placeholder_text="123 Mabini St, Barangay ...")
        self._profile_street_entry.pack()
        self._profile_street_entry.insert(0, user.get('street', ''))

        # Date of Birth
        dob_frame = ctk.CTkFrame(parent, fg_color="transparent")
        dob_frame.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(dob_frame, text="Date of Birth",
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))

        dob_picker = ctk.CTkFrame(dob_frame, fg_color="transparent")
        dob_picker.pack(anchor="w")

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        days = [str(i) for i in range(1, 32)]
        years = [str(i) for i in range(2025, 1949, -1)]

        self._profile_dob_month = ctk.CTkOptionMenu(dob_picker, values=months,
                                                     width=100, height=35,
                                                     fg_color=self.fg_color,
                                                     button_color=self.primary_color,
                                                     button_hover_color=self.hover_color,
                                                     dropdown_fg_color=self.fg_color,
                                                     text_color=self.text_color,
                                                     dropdown_text_color=self.text_color,
                                                     dropdown_hover_color=self.hover_color,
                                                     font=self.body_light_font)
        self._profile_dob_month.pack(side="left", padx=(0, 6))

        self._profile_dob_day = ctk.CTkOptionMenu(dob_picker, values=days,
                                                   width=70, height=35,
                                                   fg_color=self.fg_color,
                                                   button_color=self.primary_color,
                                                   button_hover_color=self.hover_color,
                                                   dropdown_fg_color=self.fg_color,
                                                   text_color=self.text_color,
                                                   dropdown_text_color=self.text_color,
                                                   dropdown_hover_color=self.hover_color,
                                                   font=self.body_light_font)
        self._profile_dob_day.pack(side="left", padx=(0, 6))

        self._profile_dob_year = ctk.CTkOptionMenu(dob_picker, values=years,
                                                    width=90, height=35,
                                                    fg_color=self.fg_color,
                                                    button_color=self.primary_color,
                                                    button_hover_color=self.hover_color,
                                                    dropdown_fg_color=self.fg_color,
                                                    text_color=self.text_color,
                                                    dropdown_text_color=self.text_color,
                                                    dropdown_hover_color=self.hover_color,
                                                    font=self.body_light_font)
        self._profile_dob_year.pack(side="left")

        # Pre-populate DOB
        dob_val = user.get('date_of_birth', '')
        if dob_val and isinstance(dob_val, str) and len(dob_val) >= 10:
            parts = dob_val.split('-')
            if len(parts) == 3:
                month_num = int(parts[1])
                if 1 <= month_num <= 12:
                    self._profile_dob_month.set(months[month_num - 1])
                self._profile_dob_day.set(str(int(parts[2])))
                self._profile_dob_year.set(parts[0])

        # ── Separator ───────────────────────────────────────────────
        ctk.CTkFrame(parent, height=1, fg_color=self.entry_border).pack(
            fill="x", padx=10, pady=5)

        # ── Account Info Section (read-only) ────────────────────────
        ctk.CTkLabel(parent, text="Account Info",
                     font=self.body_paragraph_font,
                     text_color=self.primary_color).pack(anchor="w", padx=10, pady=(10, 5))

        info_rows = [
            ("Role", role),
            ("Member Since", self._format_date(user.get('created_at', ''))),
            ("Auth Provider", provider_text),
            ("Account Status", user.get('status', 'active').capitalize()),
        ]
        for label, value in info_rows:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=label,
                         font=self.body_light_font,
                         text_color=self.text_color,
                         width=120).pack(side="left")
            ctk.CTkLabel(row, text=value,
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left")

        # ── Error label + Save Button ───────────────────────────────
        self._profile_error = ctk.CTkLabel(parent, text="",
                                           text_color=self.error_red,
                                           font=self.inline_error_font)
        self._profile_error.pack(pady=(10, 0))

        self._profile_save_btn = ctk.CTkButton(parent, text="SAVE CHANGES",
                                               width=480, height=42,
                                               corner_radius=6,
                                               font=self.body_bold_font,
                                               fg_color=self.primary_color,
                                               hover_color=self.hover_color,
                                               text_color=("white", "white"),
                                               command=self._save_profile_tab)
        self._profile_save_btn.pack(pady=(8, 15))

    def _format_date(self, date_str):
        """Format ISO date string to 'Month Day, Year'."""
        if not date_str or not isinstance(date_str, str):
            return "—"
        try:
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
            return dt.strftime("%B %d, %Y")
        except (ValueError, IndexError):
            return date_str[:10] if date_str else "—"

    def _pick_profile_photo(self):
        """Open file dialog to select a profile photo."""
        file_path = filedialog.askopenfilename(
            title="Select Profile Photo",
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return

        # Validate file size (max 2MB)
        if os.path.getsize(file_path) > 2 * 1024 * 1024:
            self._profile_error.configure(text="Image must be under 2MB")
            return

        try:
            pil_img = Image.open(file_path)
            pil_img.thumbnail((80, 80))
            ctk_img = ctk.CTkImage(pil_img, size=(80, 80))
            self._profile_avatar.configure(image=ctk_img)
            self._profile_photo_path = file_path  # store for save
        except Exception:
            self._profile_error.configure(text="Could not load image")

    def _save_profile_tab(self):
        """Save profile changes via API."""
        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            self._profile_error.configure(text="Not logged in")
            return

        payload = {}
        name = self._profile_name_entry.get().strip()
        if name:
            payload["name"] = name
        phone = self._profile_phone_entry.get().strip()
        if phone:
            payload["phone"] = phone
        street = self._profile_street_entry.get().strip()
        if street:
            payload["street"] = street

        # Date of birth
        month = self._profile_dob_month.get()
        day = self._profile_dob_day.get()
        year = self._profile_dob_year.get()
        dob_changed = False
        if day and year:
            month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                         "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                         "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
            month_num = month_map.get(month, "01")
            try:
                day_int = int(day)
                new_dob_str = f"{year}-{month_num}-{day_int:02d}"
                datetime.strptime(new_dob_str, "%Y-%m-%d")  # validate
                # Check if actually changed
                current_dob = getattr(self, 'current_user', {}).get('date_of_birth', '')
                if current_dob != new_dob_str:
                    payload["date_of_birth"] = new_dob_str
                    dob_changed = True
            except (ValueError, TypeError):
                self._profile_error.configure(text="Invalid date of birth")
                return

        if not payload:
            self._profile_error.configure(text="No changes to save")
            return

        self._profile_save_btn.configure(state="disabled", text="SAVING...")
        self._profile_error.configure(text="")

        def _do():
            try:
                resp = self.api.patch(f"/users/{user_id}", json=payload, timeout=10)
                if resp.status_code == 200:
                    updated = resp.json()
                    if self.current_user and isinstance(updated, dict):
                        for key in ("name", "phone", "street", "date_of_birth", "email"):
                            if key in updated:
                                self.current_user[key] = updated[key]
                    self.after(0, lambda: self._on_profile_saved())
                else:
                    err = resp.json().get("detail", "Update failed")
                    self.after(0, lambda: self._profile_error.configure(text=err))
            except Exception:
                self.after(0, lambda: self._profile_error.configure(
                    text="Cannot connect to server"))
            finally:
                self.after(0, lambda: self._profile_save_btn.configure(
                    state="normal", text="SAVE CHANGES"))

        threading.Thread(target=_do, daemon=True).start()

    def _on_profile_saved(self):
        """Handle successful profile save."""
        self.show_toast("Profile updated!", is_error=False)
        # Update navbar name if it exists
        if hasattr(self, 'name_label') and self.name_label:
            self.name_label.configure(text=self._profile_name_entry.get().strip())
        if hasattr(self, 'owner_name_label') and self.owner_name_label:
            self.owner_name_label.configure(text=self._profile_name_entry.get().strip())

    def _build_security_tab(self, parent):
        """Build the Security tab — shared across all roles."""
        # ── Change Password Section ────────────────────────────────
        ctk.CTkLabel(parent, text="Change Password",
                     font=self.body_paragraph_font,
                     text_color=self.primary_color).pack(anchor="w", padx=10, pady=(10, 8))

        # Current Password
        curr_frame = ctk.CTkFrame(parent, fg_color="transparent")
        curr_frame.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(curr_frame, text="Current Password",
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))

        curr_input_frame = ctk.CTkFrame(curr_frame, fg_color=self.fg_color,
                                        border_color=self.entry_border,
                                        border_width=1, corner_radius=6,
                                        height=38)
        curr_input_frame.pack(fill="x")
        curr_input_frame.pack_propagate(False)

        self._sec_old_pw = ctk.CTkEntry(curr_input_frame,
                                        placeholder_text="Enter current password",
                                        height=30, show="•",
                                        font=self.body_light_font,
                                        fg_color="transparent",
                                        border_width=0,
                                        text_color=self.text_color)
        self._sec_old_pw.place(relx=0.46, rely=0.5, relwidth=0.82, anchor="center")

        self._sec_old_eye = ctk.CTkLabel(curr_input_frame,
                                         image=self.closed_eye_icon,
                                         text="", cursor="hand2")
        self._sec_old_eye.place(relx=0.9, rely=0.5, anchor="center")
        self._sec_old_eye.bind("<Button-1>",
                               lambda e: self._toggle_pw_visibility("old"))

        # New Password
        new_frame = ctk.CTkFrame(parent, fg_color="transparent")
        new_frame.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(new_frame, text="New Password",
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))

        new_input_frame = ctk.CTkFrame(new_frame, fg_color=self.fg_color,
                                       border_color=self.entry_border,
                                       border_width=1, corner_radius=6,
                                       height=38)
        new_input_frame.pack(fill="x")
        new_input_frame.pack_propagate(False)

        self._sec_new_pw = ctk.CTkEntry(new_input_frame,
                                        placeholder_text="Enter new password",
                                        height=30, show="•",
                                        font=self.body_light_font,
                                        fg_color="transparent",
                                        border_width=0,
                                        text_color=self.text_color)
        self._sec_new_pw.place(relx=0.46, rely=0.5, relwidth=0.82, anchor="center")

        self._sec_new_eye = ctk.CTkLabel(new_input_frame,
                                         image=self.closed_eye_icon,
                                         text="", cursor="hand2")
        self._sec_new_eye.place(relx=0.9, rely=0.5, anchor="center")
        self._sec_new_eye.bind("<Button-1>",
                               lambda e: self._toggle_pw_visibility("new"))

        # Password requirement checklist (reusing register page pattern)
        req_frame = ctk.CTkFrame(new_frame, fg_color="transparent")
        req_frame.pack(anchor="w", padx=5, pady=(4, 0))

        self._sec_req_length = ctk.CTkLabel(
            req_frame, text="✗  8+ characters", font=self.inline_error_font,
            text_color=self.entry_border)
        self._sec_req_upper = ctk.CTkLabel(
            req_frame, text="✗  Uppercase letter", font=self.inline_error_font,
            text_color=self.entry_border)
        self._sec_req_number = ctk.CTkLabel(
            req_frame, text="✗  Number", font=self.inline_error_font,
            text_color=self.entry_border)
        self._sec_req_special = ctk.CTkLabel(
            req_frame, text="✗  Special character", font=self.inline_error_font,
            text_color=self.entry_border)

        self._sec_req_length.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=1)
        self._sec_req_upper.grid(row=0, column=1, sticky="w", pady=1)
        self._sec_req_number.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=1)
        self._sec_req_special.grid(row=1, column=1, sticky="w", pady=1)

        self._sec_new_pw.bind("<KeyRelease>", self._validate_sec_strength)

        # Confirm New Password
        confirm_frame = ctk.CTkFrame(parent, fg_color="transparent")
        confirm_frame.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(confirm_frame, text="Confirm New Password",
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))

        confirm_input_frame = ctk.CTkFrame(confirm_frame, fg_color=self.fg_color,
                                           border_color=self.entry_border,
                                           border_width=1, corner_radius=6,
                                           height=38)
        confirm_input_frame.pack(fill="x")
        confirm_input_frame.pack_propagate(False)

        self._sec_confirm_pw = ctk.CTkEntry(confirm_input_frame,
                                            placeholder_text="Re-enter new password",
                                            height=30, show="•",
                                            font=self.body_light_font,
                                            fg_color="transparent",
                                            border_width=0,
                                            text_color=self.text_color)
        self._sec_confirm_pw.place(relx=0.46, rely=0.5, relwidth=0.82, anchor="center")

        self._sec_confirm_eye = ctk.CTkLabel(confirm_input_frame,
                                             image=self.closed_eye_icon,
                                             text="", cursor="hand2")
        self._sec_confirm_eye.place(relx=0.9, rely=0.5, anchor="center")
        self._sec_confirm_eye.bind("<Button-1>",
                                   lambda e: self._toggle_pw_visibility("confirm"))

        self._sec_confirm_pw.bind("<KeyRelease>", self._validate_sec_match)

        # Password match error label
        self._sec_match_error = ctk.CTkLabel(parent, text="",
                                             text_color=self.error_red,
                                             font=self.inline_error_font)
        self._sec_match_error.pack(anchor="w", padx=15)

        # Error label
        self._sec_error = ctk.CTkLabel(parent, text="",
                                       text_color=self.error_red,
                                       font=self.inline_error_font)
        self._sec_error.pack(pady=(5, 0))

        # Update Password button
        self._sec_update_btn = ctk.CTkButton(parent, text="UPDATE PASSWORD",
                                             width=480, height=42,
                                             corner_radius=6,
                                             font=self.body_bold_font,
                                             fg_color=self.primary_color,
                                             hover_color=self.hover_color,
                                             text_color=("white", "white"),
                                             command=self._update_password)
        self._sec_update_btn.pack(pady=(8, 15))

        # ── Danger Zone ────────────────────────────────────────────
        ctk.CTkFrame(parent, height=1, fg_color=self.entry_border).pack(
            fill="x", padx=10, pady=10)

        ctk.CTkLabel(parent, text="Danger Zone",
                     font=self.body_paragraph_font,
                     text_color=self.error_red).pack(anchor="w", padx=10, pady=(0, 8))

        danger_card = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                   border_width=1, border_color=self.error_red,
                                   corner_radius=6)
        danger_card.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(danger_card,
                     text="Delete your account and all associated data.\nThis action CANNOT be undone.",
                     font=self.body_light_font,
                     text_color=self.text_color,
                     justify="left").pack(anchor="w", padx=15, pady=(15, 10))

        delete_btn = ctk.CTkButton(danger_card, text="Delete Account",
                                   fg_color=self.error_red,
                                   hover_color=self.error_red,
                                   text_color=("white", "white"),
                                   font=self.body_paragraph_font,
                                   width=140, height=36,
                                   command=self._confirm_delete_account)
        delete_btn.pack(anchor="e", padx=15, pady=(0, 12))

    def _toggle_pw_visibility(self, field):
        """Toggle password visibility for security tab fields."""
        attr_visible = f"_sec_{field}_visible"
        attr_entry = f"_sec_{field}_pw"
        attr_eye = f"_sec_{field}_eye"

        is_visible = getattr(self, attr_visible, False)
        setattr(self, attr_visible, not is_visible)

        entry = getattr(self, attr_entry)
        eye = getattr(self, attr_eye)

        if is_visible:
            entry.configure(show="•")
            self._animate_eye(eye, self._eye_frames_closed)
        else:
            entry.configure(show="")
            self._animate_eye(eye, self._eye_frames_open)

    def _validate_sec_strength(self, event=None):
        """Real-time password strength validation (register page pattern)."""
        if not hasattr(self, "_sec_req_length") or not self._sec_req_length.winfo_exists():
            return
        password = self._sec_new_pw.get()
        checks = [
            (self._sec_req_length, len(password) >= 8, "8+ characters"),
            (self._sec_req_upper, bool(re.search(r"[A-Z]", password)), "Uppercase letter"),
            (self._sec_req_number, bool(re.search(r"[0-9]", password)), "Number"),
            (self._sec_req_special, bool(re.search(r"[^a-zA-Z0-9\s]", password)), "Special character"),
        ]
        for label, met, text in checks:
            if met:
                label.configure(text=f"✓  {text}", text_color=("#2E7D32", "#4CAF50"))
            else:
                label.configure(
                    text=f"✗  {text}",
                    text_color=self.error_red if password else self.entry_border
                )

    def _validate_sec_match(self, event=None):
        """Real-time password match validation."""
        new_pw = self._sec_new_pw.get()
        confirm = self._sec_confirm_pw.get()
        if not confirm:
            self._sec_match_error.configure(text="")
        elif new_pw != confirm:
            self._sec_match_error.configure(text="Passwords do not match")
        else:
            self._sec_match_error.configure(text="")

    def _update_password(self):
        """Call API to change password."""
        old_pw = self._sec_old_pw.get()
        new_pw = self._sec_new_pw.get()
        confirm = self._sec_confirm_pw.get()

        # Validation
        if not old_pw or not new_pw or not confirm:
            self._sec_error.configure(text="All fields are required")
            return
        if new_pw != confirm:
            self._sec_error.configure(text="New passwords do not match")
            return
        if len(new_pw) < 8:
            self._sec_error.configure(text="Password must be at least 8 characters")
            return

        self._sec_error.configure(text="")
        self._sec_update_btn.configure(state="disabled", text="UPDATING...")

        def _do():
            try:
                resp = self.api.post("/auth/change-password", json={
                    "old_password": old_pw,
                    "new_password": new_pw
                }, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self._on_password_updated())
                else:
                    err = resp.json().get("detail", "Failed to change password")
                    self.after(0, lambda: self._sec_error.configure(text=err))
            except Exception:
                self.after(0, lambda: self._sec_error.configure(
                    text="Cannot connect to server"))
            finally:
                self.after(0, lambda: self._sec_update_btn.configure(
                    state="normal", text="UPDATE PASSWORD"))

        threading.Thread(target=_do, daemon=True).start()

    def _on_password_updated(self):
        """Handle successful password change."""
        self.show_toast("Password changed successfully!", is_error=False)
        self._sec_old_pw.delete(0, "end")
        self._sec_new_pw.delete(0, "end")
        self._sec_confirm_pw.delete(0, "end")
        self._sec_match_error.configure(text="")
        self._sec_error.configure(text="")
        # Reset requirement labels
        for label in (self._sec_req_length, self._sec_req_upper,
                      self._sec_req_number, self._sec_req_special):
            label.configure(text_color=self.entry_border)

    def _confirm_delete_account(self):
        """Show confirmation dialog, then delete account."""
        dialog = CTkInputDialog(
            text="Type DELETE to permanently delete your account:",
            title="Delete Account"
        )
        result = dialog.get_input()
        if result != "DELETE":
            return

        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            return

        def _do():
            try:
                resp = self.api.delete(f"/users/{user_id}", timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self._on_account_deleted())
                else:
                    err = resp.json().get("detail", "Failed to delete account")
                    self.after(0, lambda: self.show_toast(err, is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast(
                    "Cannot connect to server", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def _on_account_deleted(self):
        """Handle account deletion — logout."""
        self.show_toast("Account deleted.", is_error=False)
        self._close_account_overlay()
        self._handle_logout()

    def _build_verification_tab(self, parent):
        """Build the Verification tab (Tenant only)."""
        user = getattr(self, 'current_user', {}) or {}
        is_verified = user.get('is_verified', False)
        id_doc_url = user.get('id_document_url', '')

        # ── Status Card ─────────────────────────────────────────────
        if is_verified:
            status_color = ("#2E7D32", "#4CAF50")
            status_text = "✓ Verified"
            status_detail = "Your account is verified. You can book listings."
        elif id_doc_url:
            status_color = self.hover_color
            status_text = "● Pending Review"
            status_detail = "Your ID is under review (1-2 business days)."
        else:
            status_color = self.hover_color
            status_text = "○ Not Verified"
            status_detail = "Upload a valid government ID to get verified."

        status_card = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                   border_width=1, border_color=status_color,
                                   corner_radius=6)
        status_card.pack(fill="x", padx=10, pady=(15, 10))

        ctk.CTkLabel(status_card, text=status_text,
                     font=self.body_paragraph_font,
                     text_color=status_color).pack(anchor="w", padx=15, pady=(10, 2))
        ctk.CTkLabel(status_card, text=status_detail,
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", padx=15, pady=(0, 10))

        # ── ID Upload Section ───────────────────────────────────────
        ctk.CTkLabel(parent, text="Valid ID Document",
                     font=self.body_paragraph_font,
                     text_color=self.primary_color).pack(anchor="w", padx=10, pady=(10, 5))

        upload_frame = ctk.CTkFrame(parent, fg_color="transparent")
        upload_frame.pack(fill="x", padx=10, pady=(0, 10))

        self._verify_upload_btn = ctk.CTkButton(upload_frame,
                                                text="📤  Upload Valid ID",
                                                font=self.body_light_font,
                                                fg_color=self.primary_color,
                                                hover_color=self.hover_color,
                                                text_color=("white", "white"),
                                                command=self._pick_id_document)
        self._verify_upload_btn.pack(side="left")

        ctk.CTkLabel(upload_frame,
                     text="Accepted: JPG, PNG, PDF (max 5MB)",
                     font=self.body_description_font,
                     text_color=self.text_color).pack(side="left", padx=(10, 0))

        # Existing file info
        self._verify_file_label = ctk.CTkLabel(parent, text="",
                                                font=self.body_light_font,
                                                text_color=self.text_color)
        self._verify_file_label.pack(anchor="w", padx=10)
        if id_doc_url:
            filename = id_doc_url.split("/")[-1] if "/" in id_doc_url else id_doc_url
            self._verify_file_label.configure(text=f"Current file: {filename}")

        self._verify_progress = ctk.CTkProgressBar(parent, mode="indeterminate",
                                                    fg_color=self.entry_border,
                                                    progress_color=self.primary_color)
        self._verify_error = ctk.CTkLabel(parent, text="",
                                          text_color=self.error_red,
                                          font=self.inline_error_font)
        self._verify_error.pack(anchor="w", padx=10, pady=(5, 0))

        # ── Linked Accounts ─────────────────────────────────────────
        ctk.CTkFrame(parent, height=1, fg_color=self.entry_border).pack(
            fill="x", padx=10, pady=10)

        ctk.CTkLabel(parent, text="Linked Accounts",
                     font=self.body_paragraph_font,
                     text_color=self.primary_color).pack(anchor="w", padx=10, pady=(0, 8))

        auth_provider = user.get('auth_provider', 'email')
        self._build_linked_account_card(parent, auth_provider)

    def _pick_id_document(self):
        """Open file dialog to select an ID document."""
        file_path = filedialog.askopenfilename(
            title="Select Valid ID",
            filetypes=[("Images/PDF", "*.jpg *.jpeg *.png *.pdf")]
        )
        if not file_path:
            return

        if os.path.getsize(file_path) > 5 * 1024 * 1024:
            self._verify_error.configure(text="File must be under 5MB")
            return

        self._verify_error.configure(text="")
        self._verify_progress.pack(fill="x", padx=10, pady=(5, 0))
        self._verify_progress.start()

        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            self._verify_error.configure(text="Not logged in")
            return

        def _do():
            try:
                # Upload file logic — assumes API endpoint accepts multipart
                with open(file_path, "rb") as f:
                    files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
                    resp = self.api.post(f"/users/{user_id}/upload-id", files=files, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    url = data.get("url", "")
                    if self.current_user:
                        self.after(0, lambda: self.current_user.update({"id_document_url": url}))
                    self.after(0, lambda: self._on_id_uploaded(os.path.basename(file_path)))
                else:
                    err = resp.json().get("detail", "Upload failed")
                    self.after(0, lambda: self._verify_error.configure(text=err))
            except Exception:
                self.after(0, lambda: self._verify_error.configure(
                    text="Cannot connect to server"))
            finally:
                self.after(0, lambda: self._verify_progress.stop())
                self.after(0, lambda: self._verify_progress.pack_forget())

        threading.Thread(target=_do, daemon=True).start()

    def _on_id_uploaded(self, filename):
        """Handle successful ID upload."""
        self.show_toast("ID document uploaded!", is_error=False)
        self._verify_file_label.configure(text=f"Current file: {filename}")

    def _build_documents_tab(self, parent):
        """Build the Documents tab (Owner only — business permit)."""
        user = getattr(self, 'current_user', {}) or {}
        permit_url = user.get('permit_url', '')
        is_verified = user.get('is_verified', False)

        if is_verified:
            status_color = ("#2E7D32", "#4CAF50")
            status_text = "✓ Verified"
            status_detail = "Your business permit is verified. Your listings show the Verified badge."
        elif permit_url:
            status_color = self.hover_color
            status_text = "● Pending Review"
            status_detail = "Your permit is being reviewed by an admin."
        else:
            status_color = self.hover_color
            status_text = "○ Not Uploaded"
            status_detail = "Upload your business permit to get your listings verified."

        status_card = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                   border_width=1, border_color=status_color,
                                   corner_radius=6)
        status_card.pack(fill="x", padx=10, pady=(15, 10))

        ctk.CTkLabel(status_card, text=status_text,
                     font=self.body_paragraph_font,
                     text_color=status_color).pack(anchor="w", padx=15, pady=(10, 2))
        ctk.CTkLabel(status_card, text=status_detail,
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkLabel(parent, text="Business Permit",
                     font=self.body_paragraph_font,
                     text_color=self.primary_color).pack(anchor="w", padx=10, pady=(10, 5))

        upload_frame = ctk.CTkFrame(parent, fg_color="transparent")
        upload_frame.pack(fill="x", padx=10, pady=(0, 10))

        self._doc_upload_btn = ctk.CTkButton(upload_frame,
                                             text="📤  Upload Business Permit",
                                             font=self.body_light_font,
                                             fg_color=self.primary_color,
                                             hover_color=self.hover_color,
                                             text_color=("white", "white"),
                                             command=self._pick_permit)
        self._doc_upload_btn.pack(side="left")

        ctk.CTkLabel(upload_frame,
                     text="Accepted: JPG, PNG, PDF (max 10MB)",
                     font=self.body_description_font,
                     text_color=self.text_color).pack(side="left", padx=(10, 0))

        self._doc_file_label = ctk.CTkLabel(parent, text="",
                                            font=self.body_light_font,
                                            text_color=self.text_color)
        self._doc_file_label.pack(anchor="w", padx=10)
        if permit_url:
            filename = permit_url.split("/")[-1] if "/" in permit_url else permit_url
            self._doc_file_label.configure(text=f"Current file: {filename}")

        self._doc_progress = ctk.CTkProgressBar(parent, mode="indeterminate",
                                                 fg_color=self.entry_border,
                                                 progress_color=self.primary_color)
        self._doc_error = ctk.CTkLabel(parent, text="",
                                       text_color=self.error_red,
                                       font=self.inline_error_font)
        self._doc_error.pack(anchor="w", padx=10, pady=(5, 0))

        ctk.CTkFrame(parent, height=1, fg_color=self.entry_border).pack(
            fill="x", padx=10, pady=10)

        ctk.CTkLabel(parent, text="Linked Accounts",
                     font=self.body_paragraph_font,
                     text_color=self.primary_color).pack(anchor="w", padx=10, pady=(0, 8))

        auth_provider = user.get('auth_provider', 'email')
        self._build_linked_account_card(parent, auth_provider)

    def _build_linked_account_card(self, parent, auth_provider):
        """Build the linked accounts card (Google only)."""
        has_google = auth_provider in ("google", "both")
        user = getattr(self, 'current_user', {}) or {}
        email = user.get('email', '')

        card = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                            corner_radius=6, border_width=1,
                            border_color=self.entry_border)
        card.pack(fill="x", padx=10, pady=(0, 10))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(row, text="Google",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(side="left")

        if has_google:
            ctk.CTkLabel(row, text="● Connected",
                         font=self.body_description_font,
                         fg_color=("#2E7D32", "#4CAF50"), text_color=("white", "white"),
                         corner_radius=4, padx=6).pack(side="right")

            ctk.CTkButton(row, text="Unlink",
                          font=self.body_description_font,
                          fg_color="transparent",
                          text_color=self.error_red,
                          hover_color=self.hover_color,
                          width=60, height=28,
                          command=self._unlink_google).pack(side="right", padx=(0, 8))
        else:
            ctk.CTkLabel(row, text="○ Not linked",
                         font=self.body_description_font,
                         text_color=self.text_color).pack(side="right")

            ctk.CTkButton(row, text="Link",
                          font=self.body_description_font,
                          fg_color=self.secondary_color,
                          text_color=self.text_color,
                          border_width=1, border_color=self.entry_border,
                          state="disabled",
                          width=60, height=28).pack(side="right", padx=(0, 8))

        ctk.CTkLabel(card, text=email,
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", padx=15, pady=(0, 10))

    def _unlink_google(self):
        """Unlink Google account from user."""
        dialog = CTkInputDialog(
            text="Unlink your Google account? You can still log in with your email.",
            title="Unlink Google"
        )
        result = dialog.get_input()
        if result is None:
            return

        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            return

        def _do():
            try:
                resp = self.api.patch(f"/users/{user_id}",
                                      json={"auth_provider": "email"}, timeout=10)
                if resp.status_code == 200:
                    if self.current_user:
                        self.after(0, lambda: self.current_user.update({"auth_provider": "email"}))
                    self.after(0, lambda: self.show_toast("Google account unlinked", is_error=False))
                    self.after(0, lambda: self._close_account_overlay())
                    self.after(100, self.show_account_settings)
                else:
                    err = resp.json().get("detail", "Failed to unlink")
                    self.after(0, lambda: self.show_toast(err, is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def _pick_permit(self):
        """Open file dialog to select a business permit."""
        file_path = filedialog.askopenfilename(
            title="Select Business Permit",
            filetypes=[("Images/PDF", "*.jpg *.jpeg *.png *.pdf")]
        )
        if not file_path:
            return

        if os.path.getsize(file_path) > 10 * 1024 * 1024:
            self._doc_error.configure(text="File must be under 10MB")
            return

        self._doc_error.configure(text="")
        self._doc_progress.pack(fill="x", padx=10, pady=(5, 0))
        self._doc_progress.start()

        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            self._doc_error.configure(text="Not logged in")
            return

        def _do():
            try:
                with open(file_path, "rb") as f:
                    files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
                    resp = self.api.post(f"/users/{user_id}/upload-permit", files=files, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    url = data.get("url", "")
                    if self.current_user:
                        self.after(0, lambda: self.current_user.update({"permit_url": url}))
                    self.after(0, lambda: self._on_permit_uploaded(os.path.basename(file_path)))
                else:
                    err = resp.json().get("detail", "Upload failed")
                    self.after(0, lambda: self._doc_error.configure(text=err))
            except Exception:
                self.after(0, lambda: self._doc_error.configure(
                    text="Cannot connect to server"))
            finally:
                self.after(0, lambda: self._doc_progress.stop())
                self.after(0, lambda: self._doc_progress.pack_forget())

        threading.Thread(target=_do, daemon=True).start()

    def _on_permit_uploaded(self, filename):
        """Handle successful permit upload."""
        self.show_toast("Business permit uploaded!", is_error=False)
        self._doc_file_label.configure(text=f"Current file: {filename}")
