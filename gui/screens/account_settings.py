import customtkinter as ctk
import threading
from PIL import Image
import io
import re
from tkinter import filedialog, messagebox


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
                            border_color=self.entry_border, width=580)
        card.place(relx=0.5, rely=0.5, anchor="center")

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
        tabview = ctk.CTkTabview(card, width=540, height=460,
                                 fg_color="transparent",
                                 segmented_button_fg_color=self.fg_color,
                                 segmented_button_selected_color=self.primary_color,
                                 segmented_button_unselected_color=self.hover_color_text,
                                 text_color=self.text_color)
        tabview.pack(padx=20, pady=(0, 20))

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
            from datetime import datetime
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
        import os
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
                from datetime import datetime
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
