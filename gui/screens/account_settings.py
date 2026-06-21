import threading
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import io
import os
import re
from datetime import datetime

from gui.widgets.settings_accordion import SettingsAccordion


class AccountSettingsMixin:

    def show_account_settings(self):
        wrapper = getattr(self, "_admin_content_wrapper", None) or getattr(
            self, "content_wrapper", None
        )
        if not wrapper:
            return

        for w in wrapper.winfo_children():
            w.destroy()

        container = ctk.CTkFrame(wrapper, fg_color="transparent")
        container.pack(fill="both", expand=True)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        back_btn = ctk.CTkLabel(header, text="", image=self.bk_btn_icon,
                                cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: self._go_back_from_settings())
        back_btn.bind("<Enter>",
                      lambda e: back_btn.configure(image=self.bk_btn_hvr_icon))
        back_btn.bind("<Leave>",
                      lambda e: back_btn.configure(image=self.bk_btn_icon))

        ctk.CTkLabel(header, text="ACCOUNT SETTINGS",
                     font=self.alt_title_font,
                     text_color=self.text_color).pack(side="left", padx=10)

        self._settings_accordion = SettingsAccordion(
            container,
            entry_border=self.entry_border,
            text_color=self.text_color,
            primary_color=self.primary_color,
            title_font=self.body_paragraph_font,
        )
        self._settings_accordion.pack(fill="both", expand=True)

        role = self.current_user.get("role", "tenant")

        profile_handle = self._settings_accordion.add_section("Profile")
        self._build_profile_content(profile_handle.content_frame)
        profile_handle.cache_content_height()

        sec_handle = self._settings_accordion.add_section("Security")
        self._build_security_content(sec_handle.content_frame)
        sec_handle.cache_content_height()

        if role == "tenant":
            verif_handle = self._settings_accordion.add_section("Verification")
            self._build_verification_content(verif_handle.content_frame)
            verif_handle.cache_content_height()

        if role == "owner":
            docs_handle = self._settings_accordion.add_section("Documents")
            self._build_documents_content(docs_handle.content_frame)
            docs_handle.cache_content_height()

        self._settings_accordion.expand_first()

    # ── Profile Section ─────────────────────────────────────────────

    def _build_profile_content(self, frame):
        user = self.current_user

        avatar_row = ctk.CTkFrame(frame, fg_color="transparent")
        avatar_row.pack(fill="x", pady=(0, 15))

        avatar_left = ctk.CTkFrame(avatar_row, fg_color="transparent")
        avatar_left.pack(side="left", padx=(0, 20))

        self._settings_avatar = ctk.CTkLabel(
            avatar_left, text="", image=self.pfp_placeholder_lg,
            width=100, height=100)
        self._settings_avatar.pack()

        self._settings_edit_photo_btn = ctk.CTkButton(
            avatar_left, text="Edit Photo",
            font=self.body_description_font,
            fg_color="transparent",
            text_color=self.primary_color,
            hover_color=self.hover_color,
            command=self._pick_profile_photo)
        self._settings_edit_photo_btn.pack(pady=(4, 0))

        avatar_right = ctk.CTkFrame(avatar_row, fg_color="transparent")
        avatar_right.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(avatar_right, text=user.get("name", ""),
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(anchor="w")

        ctk.CTkLabel(avatar_right, text=user.get("email", ""),
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w")

        badge_row = ctk.CTkFrame(avatar_right, fg_color="transparent")
        badge_row.pack(anchor="w", pady=(4, 0))

        role_badge = ctk.CTkLabel(
            badge_row,
            text=f"  {user.get('role', '').capitalize()}  ",
            fg_color=self.primary_color, text_color="white",
            corner_radius=4, font=ctk.CTkFont(size=11, weight="bold"))
        role_badge.pack(side="left", padx=(0, 6))

        email_verified = user.get("email_verified", False) or bool(
            user.get("email_verified_at"))
        ev_color = self.primary_color if email_verified else self.entry_border
        ev_text = "Email Verified" if email_verified else "Not Verified"
        ctk.CTkLabel(badge_row, text=ev_text, fg_color=ev_color,
                     text_color="white", corner_radius=4,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(
                         side="left", padx=(0, 6))

        auth_provider = user.get("auth_provider", "email").capitalize()
        ctk.CTkLabel(badge_row, text=auth_provider, fg_color=self.entry_border,
                     text_color=self.text_color, corner_radius=4,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")

        card = ctk.CTkFrame(frame, fg_color=self.secondary_color,
                            corner_radius=8, border_width=1,
                            border_color=self.entry_border)
        card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(card, text="Personal Information",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(12, 8))

        pi_inner = ctk.CTkFrame(card, fg_color="transparent")
        pi_inner.pack(fill="x", padx=15, pady=(0, 12))

        ctk.CTkLabel(pi_inner, text="Full Name",
                     font=self.body_description_font,
                     text_color=self.text_color).pack(anchor="w")
        self._settings_name_entry = ctk.CTkEntry(
            pi_inner, font=self.body_light_font,
            fg_color="transparent", text_color=self.text_color,
            border_color=self.entry_border)
        self._settings_name_entry.insert(0, user.get("name", ""))
        self._settings_name_entry.pack(fill="x", pady=(0, 2))
        self._settings_name_error = ctk.CTkLabel(
            pi_inner, text="", font=self.inline_error_font,
            text_color=self.error_red)
        self._settings_name_error.pack(anchor="w", pady=(0, 10))
        self._settings_name_entry.bind("<KeyRelease>", self._validate_settings_name)

        ctk.CTkLabel(pi_inner, text="Phone",
                     font=self.body_description_font,
                     text_color=self.text_color).pack(anchor="w")
        self._settings_phone_var = ctk.StringVar()
        self._settings_phone_var.trace_add("write", self._filter_settings_phone)
        self._settings_phone_entry = ctk.CTkEntry(
            pi_inner, font=self.body_light_font,
            fg_color="transparent", text_color=self.text_color,
            border_color=self.entry_border, textvariable=self._settings_phone_var)
        self._settings_phone_entry.insert(0, user.get("phone", ""))
        self._settings_phone_entry.pack(fill="x", pady=(0, 2))
        self._settings_phone_error = ctk.CTkLabel(
            pi_inner, text="", font=self.inline_error_font,
            text_color=self.error_red)
        self._settings_phone_error.pack(anchor="w", pady=(0, 10))
        self._settings_phone_entry.bind("<KeyRelease>", self._validate_settings_phone)

        ctk.CTkLabel(pi_inner, text="Street Address",
                     font=self.body_description_font,
                     text_color=self.text_color).pack(anchor="w")
        self._settings_street_entry = ctk.CTkEntry(
            pi_inner, font=self.body_light_font,
            fg_color="transparent", text_color=self.text_color,
            border_color=self.entry_border)
        self._settings_street_entry.insert(0, user.get("street", ""))
        self._settings_street_entry.pack(fill="x", pady=(0, 10))

        dob_frame = ctk.CTkFrame(pi_inner, fg_color="transparent")
        dob_frame.pack(anchor="w", fill="x", pady=(0, 10))

        ctk.CTkLabel(dob_frame, text="Date Of Birth",
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 5))

        dob_bg = ctk.CTkFrame(dob_frame, fg_color=self.fg_color,
                               corner_radius=6, border_width=1,
                               border_color=self.entry_border)
        dob_bg.pack(anchor="w")

        dob_raw = user.get("date_of_birth", "")
        dob_parts = dob_raw.split("-") if dob_raw else ["", "", ""]
        dob_year, dob_month, dob_day = (dob_parts[0], dob_parts[1],
                                         dob_parts[2]) if len(
                                             dob_parts) == 3 else ("", "", "")

        months = [f"{i:02d}" for i in range(1, 13)]
        days = [f"{i:02d}" for i in range(1, 32)]
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year, 1949, -1)]

        self._settings_dob_month = ctk.CTkComboBox(
            dob_bg, values=months, font=self.body_light_font,
            fg_color=self.fg_color,
            dropdown_fg_color=self.fg_color,
            dropdown_text_color=self.text_color,
            dropdown_hover_color=self.hover_color,
            dropdown_font=self.body_light_font,
            text_color=self.text_color,
            button_color=self.primary_color,
            button_hover_color=self.hover_color,
            width=70, border_width=0)
        self._settings_dob_month._entry.bind(
            "<Key>", lambda e: None if e.keysym == "Tab" else "break")
        self._settings_dob_month.pack(side="left", padx=(35, 10), pady=8)
        self._make_dropdown(
            self._settings_dob_month, values=months,
            autocomplete=True, command=self._settings_dob_month.set)
        if dob_month in months:
            self._settings_dob_month.set(dob_month)

        ctk.CTkLabel(dob_bg, text="/", text_color=self.text_color,
                     width=10).pack(side="left", padx=(25, 20))

        self._settings_dob_day = ctk.CTkComboBox(
            dob_bg, values=days, font=self.body_light_font,
            fg_color=self.fg_color,
            dropdown_fg_color=self.fg_color,
            dropdown_text_color=self.text_color,
            dropdown_hover_color=self.hover_color,
            dropdown_font=self.body_light_font,
            text_color=self.text_color,
            button_color=self.primary_color,
            button_hover_color=self.hover_color,
            width=65, border_width=0,
            border_color=self.entry_border)
        self._settings_dob_day._entry.bind(
            "<Key>", lambda e: None if e.keysym == "Tab" else "break")
        self._settings_dob_day.pack(side="left", pady=8, padx=(0, 5))
        self._make_dropdown(
            self._settings_dob_day, values=days,
            autocomplete=True, command=self._settings_dob_day.set)
        if dob_day in days:
            self._settings_dob_day.set(dob_day)

        ctk.CTkLabel(dob_bg, text="/", text_color=self.text_color,
                     width=10).pack(side="left", padx=(30, 25))

        self._settings_dob_year = ctk.CTkComboBox(
            dob_bg, values=years, font=self.body_light_font,
            fg_color=self.fg_color,
            dropdown_fg_color=self.fg_color,
            dropdown_text_color=self.text_color,
            dropdown_hover_color=self.hover_color,
            dropdown_font=self.body_light_font,
            text_color=self.text_color,
            button_color=self.primary_color,
            button_hover_color=self.hover_color,
            width=95, border_width=0,
            border_color=self.entry_border)
        self._settings_dob_year._entry.bind(
            "<Key>", lambda e: None if e.keysym == "Tab" else "break")
        self._settings_dob_year.pack(side="left", pady=8, padx=(0, 35))
        self._make_dropdown(
            self._settings_dob_year, values=years,
            autocomplete=True, command=self._settings_dob_year.set)
        if dob_year in years:
            self._settings_dob_year.set(dob_year)
        self._settings_dob_year.pack(side="left")
        if dob_year in years:
            self._settings_dob_year.set(dob_year)

        self._settings_profile_error = ctk.CTkLabel(
            pi_inner, text="", font=self.inline_error_font,
            text_color=self.error_red)
        self._settings_profile_error.pack(anchor="w", pady=(4, 0))

        self._settings_save_btn = ctk.CTkButton(
            pi_inner, text="SAVE CHANGES",
            font=self.body_paragraph_font,
            fg_color=self.primary_color,
            hover_color=self.hover_color,
            text_color="white",
            command=self._save_profile)
        self._settings_save_btn.pack(pady=(6, 0))

        info_card = ctk.CTkFrame(frame, fg_color="transparent",
                                 corner_radius=8, border_width=1,
                                 border_color=self.entry_border)
        info_card.pack(fill="x")

        ctk.CTkLabel(info_card, text="Account Information",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(12, 8))

        info_rows = [
            ("Role", user.get("role", "").capitalize()),
            ("Member Since",
             self._format_date(user.get("created_at", ""))),
            ("Auth Provider",
             user.get("auth_provider", "Email").capitalize()),
            ("Account Status",
             "Verified" if user.get("is_verified") else "Active"),
        ]
        for i, (label, value) in enumerate(info_rows):
            bg = self.secondary_color if i % 2 == 0 else "transparent"
            row = ctk.CTkFrame(info_card, fg_color=bg)
            row.pack(fill="x", padx=15, pady=1)

            ctk.CTkLabel(row, text=label, font=self.body_light_font,
                         text_color=self.text_color).pack(
                             side="left", padx=10, pady=6)
            ctk.CTkLabel(row, text=value, font=self.body_paragraph_font,
                         text_color=self.text_color).pack(
                             side="right", padx=10, pady=6)

    def _save_profile(self):
        name = self._settings_name_entry.get().strip()
        phone = self._settings_phone_entry.get().strip()
        street = self._settings_street_entry.get().strip()
        month = self._settings_dob_month.get()
        day = self._settings_dob_day.get()
        year = self._settings_dob_year.get()

        has_error = False
        if not name or len(name) < 2:
            self._settings_name_error.configure(text="Name must be at least 2 characters.")
            self._settings_name_entry.configure(border_color=self.error_red)
            has_error = True
        else:
            self._settings_name_error.configure(text="")

        if phone:
            if not re.match(r"^09\d{9}$", phone):
                self._settings_phone_error.configure(text="Must start with '09' and be exactly 11 digits.")
                self._settings_phone_entry.configure(border_color=self.error_red)
                has_error = True
            else:
                self._settings_phone_error.configure(text="")
        else:
            self._settings_phone_error.configure(text="")

        if has_error:
            return

        dob_str = f"{year}-{month}-{day}"
        try:
            datetime.strptime(dob_str, "%Y-%m-%d")
        except ValueError:
            self._settings_profile_error.configure(text="Invalid date of birth.")
            return

        self._settings_profile_error.configure(text="")

        payload = {}
        if name != self.current_user.get("name"):
            payload["name"] = name
        if phone != self.current_user.get("phone", ""):
            payload["phone"] = phone
        if street != self.current_user.get("street", ""):
            payload["street"] = street
        if dob_str != self.current_user.get("date_of_birth", ""):
            payload["date_of_birth"] = dob_str

        if not payload:
            self._settings_profile_error.configure(
                text="No changes to save.")
            return

        user_id = self.current_user.get("user_id")
        if not user_id:
            self.show_toast("Session error. Please log in again.", is_error=True)
            return

        accordion = self._settings_accordion
        btn = self._settings_save_btn
        btn.configure(state="disabled", text="SAVING...")

        def _do():
            try:
                resp = self.api.patch(f"/users/{user_id}", json=payload,
                                      timeout=10)
                self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                if resp.status_code == 200:
                    try:
                        updated = resp.json()
                    except Exception:
                        self.after(0, lambda: self.winfo_exists() and self.show_toast("Failed to parse response.", is_error=True))
                        return
                    if not isinstance(updated, dict):
                        self.after(0, lambda: self.winfo_exists() and self.show_toast("Invalid response format.", is_error=True))
                        return
                    self.current_user.update(updated)
                    self.after(
                        0, lambda: self.winfo_exists() and self.show_toast("Profile updated!",
                                                                           is_error=False))
                else:
                    try:
                        err = resp.json().get("detail",
                                              "Failed to update profile.")
                    except Exception:
                        err = "Failed to update profile."
                    self.after(
                        0, lambda: self._settings_profile_error.winfo_exists() and self._settings_profile_error.configure(
                            text=err))
                self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal", text="SAVE CHANGES"))
            except Exception as e:
                self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                self.after(
                    0, lambda: self._settings_profile_error.winfo_exists() and self._settings_profile_error.configure(
                        text=f"Error: {e}"))
                self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal", text="SAVE CHANGES"))

        accordion.show_progress()
        threading.Thread(target=_do, daemon=True).start()

    # ── Real-time Validation ──────────────────────────────────────

    def _validate_settings_name(self, event=None):
        name = self._settings_name_entry.get().strip()
        if not name or len(name) < 2:
            self._settings_name_entry.configure(border_color=self.error_red)
            self._settings_name_error.configure(text="Name must be at least 2 characters.")
        else:
            self._settings_name_entry.configure(border_color="green")
            self._settings_name_error.configure(text="")

    def _validate_settings_phone(self, event=None):
        phone = self._settings_phone_entry.get().strip()
        if not phone:
            self._settings_phone_entry.configure(border_color=self.entry_border)
            self._settings_phone_error.configure(text="")
        elif not phone.startswith("09"):
            self._settings_phone_entry.configure(border_color=self.error_red)
            self._settings_phone_error.configure(text="Phone must start with 09.")
        elif len(phone) != 11:
            self._settings_phone_entry.configure(border_color=self.error_red)
            self._settings_phone_error.configure(text=f"Must be 11 digits ({len(phone)}/11).")
        else:
            self._settings_phone_entry.configure(border_color="green")
            self._settings_phone_error.configure(text="")

    def _filter_settings_phone(self, *args):
        val = self._settings_phone_var.get()
        filtered = "".join(c for c in val if c.isdigit())[:11]
        if filtered != val:
            self._settings_phone_var.set(filtered)

    def _pick_profile_photo(self):
        path = filedialog.askopenfilename(
            title="Select Profile Photo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not path:
            return

        try:
            size = os.path.getsize(path)
            if size > 2 * 1024 * 1024:
                self.show_toast("Photo must be under 2MB.", is_error=True)
                return

            img = Image.open(path)
            img.thumbnail((100, 100))
            photo = ctk.CTkImage(img, size=(100, 100))
            self._settings_avatar.configure(image=photo)

            user_id = self.current_user.get("user_id")
            if not user_id:
                self.show_toast("Session error. Please log in again.", is_error=True)
                return

            accordion = self._settings_accordion
            btn = self._settings_edit_photo_btn
            btn.configure(state="disabled")

            def _do():
                try:
                    with open(path, "rb") as f:
                        resp = self.api.post(
                            f"/users/{user_id}/upload-photo",
                            files={"file": (os.path.basename(path), f,
                                            "image/jpeg")},
                            timeout=30)
                    self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                    if resp.status_code == 200:
                        try:
                            updated = resp.json()
                        except Exception:
                            self.after(0, lambda: self.winfo_exists() and self.show_toast("Failed to parse response.", is_error=True))
                            return
                        if not isinstance(updated, dict):
                            self.after(0, lambda: self.winfo_exists() and self.show_toast("Invalid response format.", is_error=True))
                            return
                        self.current_user.update(updated)
                        self.after(
                            0, lambda: self.winfo_exists() and self.show_toast(
                                "Profile photo updated!", is_error=False))
                    else:
                        self.after(
                            0, lambda: self.winfo_exists() and self.show_toast(
                                "Failed to upload photo.", is_error=True))
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))
                except Exception as e:
                    self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                    self.after(
                        0, lambda: self.winfo_exists() and self.show_toast(
                            f"Upload error: {e}", is_error=True))
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))

            accordion.show_progress()
            threading.Thread(target=_do, daemon=True).start()
        except Exception as e:
            self.show_toast(f"Error: {e}", is_error=True)

    @staticmethod
    def _format_date(date_str):
        if not date_str:
            return "\u2014"
        try:
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
            return dt.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            return "\u2014"

    # ── Security Section ────────────────────────────────────────────

    def _build_security_content(self, frame):
        card = ctk.CTkFrame(frame, fg_color=self.secondary_color,
                            corner_radius=8, border_width=1,
                            border_color=self.entry_border)
        card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(card, text="Change Password",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(12, 8))

        pw_inner = ctk.CTkFrame(card, fg_color="transparent")
        pw_inner.pack(fill="x", padx=15, pady=(0, 12))

        cur_row = self._make_pw_row(pw_inner, "Current Password")
        self._settings_cur_pw_entry = cur_row["entry"]
        self._settings_cur_pw_eye = cur_row["eye"]

        new_row = self._make_pw_row(pw_inner, "New Password")
        self._settings_new_pw_entry = new_row["entry"]
        self._settings_new_pw_eye = new_row["eye"]
        self._settings_new_pw_entry.bind(
            "<KeyRelease>", self._validate_sec_strength)

        self._settings_strength_frame = ctk.CTkFrame(pw_inner, fg_color="transparent")

        checks = [
            ("8+ characters", "len"),
            ("Uppercase letter", "upper"),
            ("Contains a number", "digit"),
            ("Special character", "special"),
        ]
        self._settings_strength_labels = {}
        for j, (text, _) in enumerate(checks):
            lbl = ctk.CTkLabel(self._settings_strength_frame, text=f"  {text}",
                               font=ctk.CTkFont(size=12),
                               text_color=self.text_color, anchor="w")
            lbl.grid(row=j // 2, column=j % 2, sticky="w", padx=(0, 20))
            self._settings_strength_labels[text] = lbl

        conf_row = self._make_pw_row(pw_inner, "Confirm Password")
        self._settings_conf_pw_entry = conf_row["entry"]
        self._settings_conf_pw_eye = conf_row["eye"]
        self._settings_conf_row = conf_row["row"]
        self._settings_conf_pw_entry.bind(
            "<KeyRelease>", self._validate_sec_match)
        self._settings_new_pw_entry.bind(
            "<KeyRelease>", self._validate_sec_match)

        self._settings_sec_error = ctk.CTkLabel(
            pw_inner, text="", font=self.inline_error_font,
            text_color=self.error_red)
        self._settings_sec_error.pack(anchor="w", pady=(2, 0))

        self._settings_pw_match_error = ctk.CTkLabel(
            pw_inner, text="", font=self.inline_error_font,
            text_color=self.error_red)
        self._settings_pw_match_error.pack(anchor="w", pady=(2, 0))

        self._settings_update_pw_btn = ctk.CTkButton(
            pw_inner, text="UPDATE PASSWORD",
            font=self.body_paragraph_font,
            fg_color=self.primary_color,
            hover_color=self.hover_color,
            text_color="white",
            command=self._update_password)
        self._settings_update_pw_btn.pack(pady=(6, 0))

        ctk.CTkFrame(frame, height=1, fg_color=self.entry_border).pack(
            fill="x", pady=(0, 15))

        danger_label = ctk.CTkLabel(frame, text="Danger Zone",
                                     font=self.body_paragraph_font,
                                     text_color=self.error_red)
        danger_label.pack(anchor="w", pady=(0, 8))

        danger_card = ctk.CTkFrame(frame, fg_color="transparent",
                                   corner_radius=8, border_width=2,
                                   border_color=self.error_red)
        danger_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(danger_card,
                     text="Once you delete your account, there is no "
                     "going back. Please be certain.",
                     font=self.body_light_font,
                     text_color=self.text_color,
                     wraplength=400).pack(
                         anchor="w", padx=15, pady=(12, 8))

        self._settings_delete_account_btn = ctk.CTkButton(
            danger_card, text="Delete Account",
            font=self.body_paragraph_font,
            fg_color=self.error_red,
            hover_color=self.error_red,
            text_color="white",
            command=self._confirm_delete_account)
        self._settings_delete_account_btn.pack(
            anchor="w", padx=15, pady=(0, 12))

    def _make_pw_row(self, parent, label_text):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(row, text=label_text,
                     font=self.body_description_font,
                     text_color=self.text_color).pack(anchor="w")

        input_frame = ctk.CTkFrame(row, fg_color="transparent")
        input_frame.pack(fill="x")

        entry = ctk.CTkEntry(input_frame, font=self.body_light_font,
                             fg_color="transparent",
                             text_color=self.text_color,
                             border_color=self.entry_border, show="\u2022")
        entry.pack(side="left", fill="x", expand=True)

        eye = ctk.CTkLabel(input_frame, text="", image=self.closed_eye_icon,
                           cursor="hand2")
        eye.pack(side="right", padx=(6, 0))
        eye.bind(
            "<Button-1>",
            lambda e, e2=entry, ey=eye: self._toggle_pw_visibility(e2, ey))

        return {"entry": entry, "eye": eye, "row": row}

    def _toggle_pw_visibility(self, entry, eye_label):
        if entry.cget("show") == "\u2022":
            entry.configure(show="")
            self._animate_eye(eye_label, self._eye_frames_open)
        else:
            entry.configure(show="\u2022")
            self._animate_eye(eye_label, self._eye_frames_closed)

    def _validate_sec_strength(self, event=None):
        pw = self._settings_new_pw_entry.get()
        if pw:
            if not self._settings_strength_frame.winfo_ismapped():
                self._settings_strength_frame.pack(fill="x", pady=(4, 6),
                                                    before=self._settings_conf_row)
        else:
            self._settings_strength_frame.pack_forget()
            return
        checks = {
            "8+ characters": len(pw) >= 8,
            "Uppercase letter": bool(re.search(r"[A-Z]", pw)),
            "Contains a number": bool(re.search(r"\d", pw)),
            "Special character": bool(re.search(r"[^a-zA-Z0-9]", pw)),
        }
        for text, passed in checks.items():
            lbl = self._settings_strength_labels.get(text)
            if lbl:
                prefix = "\u2713" if passed else "\u2717"
                color = self.primary_color if passed else self.error_red
                lbl.configure(text=f"{prefix} {text}", text_color=color)

    def _validate_sec_match(self, event=None):
        new = self._settings_new_pw_entry.get()
        conf = self._settings_conf_pw_entry.get()
        if conf and new != conf:
            self._settings_pw_match_error.configure(text="Passwords do not match.")
        else:
            self._settings_pw_match_error.configure(text="")

    def _update_password(self):
        current = self._settings_cur_pw_entry.get()
        new = self._settings_new_pw_entry.get()
        confirm = self._settings_conf_pw_entry.get()

        self._settings_sec_error.configure(text="")

        if not current or not new or not confirm:
            self._settings_sec_error.configure(text="All fields are required.")
            return
        if new != confirm:
            self._settings_sec_error.configure(text="Passwords do not match.")
            return
        if len(new) < 8:
            self._settings_sec_error.configure(
                text="Password must be at least 8 characters.")
            return

        accordion = self._settings_accordion
        btn = self._settings_update_pw_btn
        btn.configure(state="disabled", text="UPDATING...")

        def _do():
            try:
                resp = self.api.post(
                    "/auth/change-password",
                    json={"current_password": current,
                          "new_password": new},
                    timeout=10)
                self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                if resp.status_code == 200:
                    self.after(0, lambda: self._settings_cur_pw_entry.winfo_exists() and self._settings_cur_pw_entry.delete(0, "end"))
                    self.after(0, lambda: self._settings_new_pw_entry.winfo_exists() and self._settings_new_pw_entry.delete(0, "end"))
                    self.after(0, lambda: self._settings_conf_pw_entry.winfo_exists() and self._settings_conf_pw_entry.delete(0, "end"))
                    self.after(0, lambda: self._settings_pw_match_error.winfo_exists() and self._settings_pw_match_error.configure(text=""))
                    self.after(0, lambda: self.winfo_exists() and self._validate_sec_strength())
                    self.after(
                        0, lambda: self.winfo_exists() and self.show_toast(
                            "Password updated!", is_error=False))
                else:
                    try:
                        err = resp.json().get("detail",
                                              "Failed to update password.")
                    except Exception:
                        err = "Failed to update password."
                    self.after(
                        0,
                        lambda: self._settings_sec_error.winfo_exists() and self._settings_sec_error.configure(text=err))
                self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal", text="UPDATE PASSWORD"))
            except Exception as e:
                self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                self.after(
                    0, lambda: self._settings_sec_error.winfo_exists() and self._settings_sec_error.configure(
                        text=f"Error: {e}"))
                self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal", text="UPDATE PASSWORD"))

        accordion.show_progress()
        threading.Thread(target=_do, daemon=True).start()

    def _confirm_delete_account(self):
        dialog = ctk.CTkInputDialog(
            text='Type "DELETE" to confirm account deletion:',
            title="Delete Account")
        result = dialog.get_input()
        if result is None:
            return
        if result != "DELETE":
            self.show_toast("You must type DELETE to confirm.", is_error=True)
            return

        user_id = self.current_user.get("user_id")
        if not user_id:
            self.show_toast("Session error. Please log in again.", is_error=True)
            return

        accordion = self._settings_accordion
        btn = self._settings_delete_account_btn
        btn.configure(state="disabled")

        def _do():
            try:
                resp = self.api.delete(f"/users/{user_id}", timeout=10)
                self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                if resp.status_code == 200:
                    self.after(
                        0, lambda: self.winfo_exists() and self.show_toast(
                            "Account deleted.", is_error=False))
                    self.after(500, self._handle_logout)
                else:
                    try:
                        err = resp.json().get("detail",
                                              "Failed to delete account.")
                    except Exception:
                        err = "Failed to delete account."
                    self.after(0, lambda: self.winfo_exists() and self.show_toast(err, is_error=True))
                self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))
            except Exception as e:
                self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                self.after(
                    0, lambda: self.winfo_exists() and self.show_toast(
                        f"Error: {e}", is_error=True))
                self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))

        accordion.show_progress()
        threading.Thread(target=_do, daemon=True).start()

    # ── Verification Section (Tenant) ───────────────────────────────

    def _build_verification_content(self, frame):
        user = self.current_user
        vs = user.get("verification_status", "")
        is_verified = user.get("is_verified", False)

        if vs == "verified" or is_verified:
            status_color = self.primary_color
            status_text = "Verified"
            msg = "Your identity has been verified."
        elif vs == "pending":
            status_color = self.hover_color
            status_text = "Pending Review"
            msg = "Your documents are being reviewed."
        else:
            status_color = self.entry_border
            status_text = "Not Verified"
            msg = "Upload a valid ID document to verify your identity."

        status_card = ctk.CTkFrame(frame, fg_color=self.secondary_color,
                                   corner_radius=8, border_width=1,
                                   border_color=status_color)
        status_card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(status_card, text=status_text,
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(12, 4))
        ctk.CTkLabel(status_card, text=msg, font=self.body_light_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(0, 12))

        id_card = ctk.CTkFrame(frame, fg_color=self.secondary_color,
                               corner_radius=8, border_width=1,
                               border_color=self.entry_border)
        id_card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(id_card, text="Valid ID Document",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(id_card,
                     text="Accepted formats: JPG, PNG, PDF (max 5MB)",
                     font=self.body_description_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(0, 6))

        self._settings_id_file_label = ctk.CTkLabel(
            id_card, text="", font=self.body_light_font,
            text_color=self.text_color)
        self._settings_id_file_label.pack(anchor="w", padx=15)

        self._settings_id_error = ctk.CTkLabel(
            id_card, text="", font=self.inline_error_font,
            text_color=self.error_red)
        self._settings_id_error.pack(anchor="w", padx=15)

        self._settings_upload_id_btn = ctk.CTkButton(
            id_card, text="Upload ID",
            font=self.body_paragraph_font,
            fg_color=self.primary_color,
            hover_color=self.hover_color,
            text_color="white",
            command=self._pick_id_document)
        self._settings_upload_id_btn.pack(
            anchor="w", padx=15, pady=(0, 12))

        ctk.CTkFrame(frame, height=1, fg_color=self.entry_border).pack(
            fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="Linked Accounts",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(
                         anchor="w", pady=(0, 8))

        self._build_linked_accounts(frame, user.get("auth_provider", "email"))

    def _pick_id_document(self):
        path = filedialog.askopenfilename(
            title="Select ID Document",
            filetypes=[("Documents", "*.png *.jpg *.jpeg *.pdf")])
        if not path:
            return

        try:
            size = os.path.getsize(path)
            if size > 5 * 1024 * 1024:
                self._settings_id_error.configure(
                    text="File must be under 5MB.")
                return
            self._settings_id_error.configure(text="")
            self._settings_id_file_label.configure(
                text=f"Selected: {os.path.basename(path)}")

            user_id = self.current_user.get("user_id")
            if not user_id:
                self.show_toast("Session error. Please log in again.", is_error=True)
                return

            accordion = self._settings_accordion
            btn = self._settings_upload_id_btn
            btn.configure(state="disabled")

            def _do():
                try:
                    ext = os.path.splitext(path)[1].lower()
                    mime = {"png": "image/png", "jpg": "image/jpeg",
                            "jpeg": "image/jpeg",
                            "pdf": "application/pdf"}.get(ext.lstrip("."),
                                                          "application/octet-stream")
                    with open(path, "rb") as f:
                        resp = self.api.post(
                            f"/users/{user_id}/upload-id",
                            files={"file": (os.path.basename(path), f, mime)},
                            timeout=30)
                    self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                    if resp.status_code == 200:
                        try:
                            updated = resp.json()
                        except Exception:
                            self.after(0, lambda: self.winfo_exists() and self.show_toast("Failed to parse response.", is_error=True))
                            return
                        if not isinstance(updated, dict):
                            self.after(0, lambda: self.winfo_exists() and self.show_toast("Invalid response format.", is_error=True))
                            return
                        self.current_user.update(updated)
                        self.after(
                            0, lambda: self.winfo_exists() and self.show_toast(
                                "ID uploaded!", is_error=False))
                        self.after(
                            100,
                            lambda: self.winfo_exists() and self.show_account_settings())
                    else:
                        try:
                            err = resp.json().get("detail",
                                                  "Failed to upload ID.")
                        except Exception:
                            err = "Failed to upload ID."
                        self.after(
                            0,
                            lambda: self._settings_id_error.winfo_exists() and self._settings_id_error.configure(
                                text=err))
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))
                except Exception as e:
                    self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                    self.after(
                        0, lambda: self._settings_id_error.winfo_exists() and self._settings_id_error.configure(
                            text=f"Error: {e}"))
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))

            accordion.show_progress()
            threading.Thread(target=_do, daemon=True).start()
        except Exception as e:
            self._settings_id_error.configure(text=f"Error: {e}")

    # ── Documents Section (Owner) ───────────────────────────────────

    def _build_documents_content(self, frame):
        user = self.current_user
        vs = user.get("permit_status", "")
        is_verified = user.get("is_verified", False)

        if vs == "verified" or is_verified:
            status_color = self.primary_color
            status_text = "Verified"
            msg = "Your business permit has been verified."
        elif vs == "pending":
            status_color = self.hover_color
            status_text = "Pending Review"
            msg = "Your permit documents are being reviewed."
        else:
            status_color = self.entry_border
            status_text = "Not Uploaded"
            msg = "Upload your business permit to start listing properties."

        status_card = ctk.CTkFrame(frame, fg_color=self.secondary_color,
                                   corner_radius=8, border_width=1,
                                   border_color=status_color)
        status_card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(status_card, text=status_text,
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(12, 4))
        ctk.CTkLabel(status_card, text=msg, font=self.body_light_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(0, 12))

        permit_card = ctk.CTkFrame(frame, fg_color=self.secondary_color,
                                   corner_radius=8, border_width=1,
                                   border_color=self.entry_border)
        permit_card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(permit_card, text="Business Permit",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(permit_card,
                     text="Accepted formats: JPG, PNG, PDF (max 10MB)",
                     font=self.body_description_font,
                     text_color=self.text_color).pack(
                         anchor="w", padx=15, pady=(0, 6))

        self._settings_permit_file_label = ctk.CTkLabel(
            permit_card, text="", font=self.body_light_font,
            text_color=self.text_color)
        self._settings_permit_file_label.pack(anchor="w", padx=15)

        self._settings_permit_error = ctk.CTkLabel(
            permit_card, text="", font=self.inline_error_font,
            text_color=self.error_red)
        self._settings_permit_error.pack(anchor="w", padx=15)

        self._settings_upload_permit_btn = ctk.CTkButton(
            permit_card, text="Upload Permit",
            font=self.body_paragraph_font,
            fg_color=self.primary_color,
            hover_color=self.hover_color,
            text_color="white",
            command=self._pick_permit)
        self._settings_upload_permit_btn.pack(
            anchor="w", padx=15, pady=(0, 12))

        ctk.CTkFrame(frame, height=1, fg_color=self.entry_border).pack(
            fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="Linked Accounts",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(
                         anchor="w", pady=(0, 8))

        self._build_linked_accounts(frame, user.get("auth_provider", "email"))

    def _pick_permit(self):
        path = filedialog.askopenfilename(
            title="Select Business Permit",
            filetypes=[("Documents", "*.png *.jpg *.jpeg *.pdf")])
        if not path:
            return

        try:
            size = os.path.getsize(path)
            if size > 10 * 1024 * 1024:
                self._settings_permit_error.configure(
                    text="File must be under 10MB.")
                return
            self._settings_permit_error.configure(text="")
            self._settings_permit_file_label.configure(
                text=f"Selected: {os.path.basename(path)}")

            user_id = self.current_user.get("user_id")
            if not user_id:
                self.show_toast("Session error. Please log in again.", is_error=True)
                return

            accordion = self._settings_accordion
            btn = self._settings_upload_permit_btn
            btn.configure(state="disabled")

            def _do():
                try:
                    ext = os.path.splitext(path)[1].lower()
                    mime = {"png": "image/png", "jpg": "image/jpeg",
                            "jpeg": "image/jpeg",
                            "pdf": "application/pdf"}.get(ext.lstrip("."),
                                                          "application/octet-stream")
                    with open(path, "rb") as f:
                        resp = self.api.post(
                            f"/users/{user_id}/upload-permit",
                            files={"file": (os.path.basename(path), f, mime)},
                            timeout=30)
                    self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                    if resp.status_code == 200:
                        try:
                            updated = resp.json()
                        except Exception:
                            self.after(0, lambda: self.winfo_exists() and self.show_toast("Failed to parse response.", is_error=True))
                            return
                        if not isinstance(updated, dict):
                            self.after(0, lambda: self.winfo_exists() and self.show_toast("Invalid response format.", is_error=True))
                            return
                        self.current_user.update(updated)
                        self.after(
                            0, lambda: self.winfo_exists() and self.show_toast(
                                "Permit uploaded!", is_error=False))
                        self.after(
                            100,
                            lambda: self.winfo_exists() and self.show_account_settings())
                    else:
                        try:
                            err = resp.json().get("detail",
                                                  "Failed to upload permit.")
                        except Exception:
                            err = "Failed to upload permit."
                        self.after(
                            0,
                            lambda: self._settings_permit_error.winfo_exists() and self._settings_permit_error.configure(
                                text=err))
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))
                except Exception as e:
                    self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                    self.after(
                        0, lambda: self._settings_permit_error.winfo_exists() and self._settings_permit_error.configure(
                            text=f"Error: {e}"))
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))

            accordion.show_progress()
            threading.Thread(target=_do, daemon=True).start()
        except Exception as e:
            self._settings_permit_error.configure(text=f"Error: {e}")

    # ── Linked Accounts ─────────────────────────────────────────────

    def _build_linked_accounts(self, frame, auth_provider):
        acct_card = ctk.CTkFrame(frame, fg_color=self.secondary_color,
                                 corner_radius=8, border_width=1,
                                 border_color=self.entry_border)
        acct_card.pack(fill="x")

        row = ctk.CTkFrame(acct_card, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(row, text="Google", font=self.body_paragraph_font,
                     text_color=self.text_color).pack(side="left")

        is_google = auth_provider in ("google", "both")
        email = self.current_user.get("email", "")

        if is_google:
            badge = ctk.CTkLabel(row, text="Connected",
                                 fg_color=self.primary_color,
                                 text_color="white", corner_radius=4,
                                 font=ctk.CTkFont(size=11, weight="bold"))
            badge.pack(side="right", padx=(6, 0))

            ctk.CTkLabel(row, text=email, font=self.body_light_font,
                         text_color=self.text_color).pack(
                             side="right", padx=(0, 6))

            self._settings_unlink_google_btn = ctk.CTkButton(
                row, text="Unlink",
                font=self.body_description_font,
                fg_color=self.error_red,
                hover_color=self.error_red,
                text_color="white",
                width=60, height=28,
                command=self._unlink_google)
            self._settings_unlink_google_btn.pack(
                side="right", padx=(0, 6))
        else:
            badge = ctk.CTkLabel(row, text="Not linked",
                                 fg_color=self.entry_border,
                                 text_color=self.text_color,
                                 corner_radius=4,
                                 font=ctk.CTkFont(size=11, weight="bold"))
            badge.pack(side="right", padx=(6, 0))

            ctk.CTkLabel(row, text="Link your Google account",
                         font=self.body_light_font,
                         text_color=self.text_color).pack(
                             side="right", padx=(0, 6))

            ctk.CTkButton(row, text="Link",
                          font=self.body_description_font,
                          fg_color=self.primary_color,
                          hover_color=self.hover_color,
                          text_color="white",
                          width=60, height=28,
                          state="disabled").pack(side="right", padx=(0, 6))

    def _unlink_google(self):
        dialog = ctk.CTkInputDialog(
            text="Are you sure? Type UNLINK to confirm:",
            title="Unlink Google")
        result = dialog.get_input()
        if result != "UNLINK":
            return

        user_id = self.current_user.get("user_id")
        if not user_id:
            self.show_toast("Session error. Please log in again.", is_error=True)
            return

        accordion = self._settings_accordion
        btn = self._settings_unlink_google_btn
        btn.configure(state="disabled")

        def _do():
            try:
                resp = self.api.patch(
                    f"/users/{user_id}",
                    json={"auth_provider": "email"}, timeout=10)
                self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                if resp.status_code == 200:
                    try:
                        updated = resp.json()
                    except Exception:
                        self.after(0, lambda: self.winfo_exists() and self.show_toast("Failed to parse response.", is_error=True))
                        return
                    if not isinstance(updated, dict):
                        self.after(0, lambda: self.winfo_exists() and self.show_toast("Invalid response format.", is_error=True))
                        return
                    self.current_user.update(updated)
                    self.after(
                        0, lambda: self.winfo_exists() and self.show_toast(
                            "Google account unlinked.", is_error=False))
                    self.after(100, self.show_account_settings)
                else:
                    try:
                        err = resp.json().get("detail",
                                              "Failed to unlink Google.")
                    except Exception:
                        err = "Failed to unlink Google."
                    self.after(0, lambda: self.winfo_exists() and self.show_toast(err, is_error=True))
                self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))
            except Exception as e:
                self.after(0, lambda: accordion.winfo_exists() and accordion.hide_progress())
                self.after(
                    0, lambda: self.winfo_exists() and self.show_toast(
                        f"Error: {e}", is_error=True))
                self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))

        accordion.show_progress()
        threading.Thread(target=_do, daemon=True).start()

    # ── Navigation ──────────────────────────────────────────────────

    def _go_back_from_settings(self):
        role = self.current_user.get("role")
        if role == "admin":
            self.show_admin_dashboard()
        elif role == "owner":
            self.show_owner_dashboard()
        else:
            self.show_tenant_dashboard()
