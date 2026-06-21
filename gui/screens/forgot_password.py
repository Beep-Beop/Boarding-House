import re
import threading
import customtkinter as ctk
from requests.exceptions import ConnectionError


class ForgotPasswordMixin:
    def show_forgot_password_page(self):
        self.clear_container()
        self.geometry("630x700")
        self.resizable(False, False)

        self._reset_data = {}

        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        # Back button
        bk_btn_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        bk_btn_frame.pack(fill="x", pady=(15, 0))

        self.back_btn = ctk.CTkLabel(bk_btn_frame, text="", image=self.bk_btn_icon, cursor="hand2")
        self.back_btn.pack(side="left", padx=(15, 0))
        self.back_btn.bind("<Button-1>", lambda event: self.show_login_page())
        self.back_btn.bind("<Enter>", lambda event: self.back_btn.configure(image=self.bk_btn_hvr_icon))
        self.back_btn.bind("<Leave>", lambda event: self.back_btn.configure(image=self.bk_btn_icon))

        # Logo
        logo_label = ctk.CTkLabel(self.form_container, text=None, image=self.logo, width=140, height=32)
        logo_label.pack(pady=(20, 15))

        title_label = ctk.CTkLabel(self.form_container, text="FORGOT PASSWORD",
                                    font=self.alt_title_font, text_color=self.text_color)
        title_label.pack(pady=(0, 10))

        # --- Step container (swaps content) ---
        self.step_container = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.step_container.pack(pady=(30, 0))

        # Build all 3 steps
        self._build_step1()
        self._build_step2()
        self._build_step3()

        self._show_step(1)

    def _build_step1(self):
        self.step1_frame = ctk.CTkFrame(self.step_container, fg_color="transparent")

        desc = ctk.CTkLabel(self.step1_frame, text="Enter your email to receive a reset code.",
                            font=self.body_paragraph_font, text_color=self.text_color)
        desc.pack(pady=(0, 20))

        email_frame = ctk.CTkFrame(self.step1_frame, fg_color="transparent")
        email_frame.pack()

        email_label = ctk.CTkLabel(email_frame, text="Email", font=self.body_light_font, text_color=self.text_color)
        email_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        self.fp_email_fake_entry = ctk.CTkFrame(email_frame, width=400, height=50,
                                                 fg_color=self.fg_color, border_color=self.entry_border,
                                                 border_width=1, corner_radius=6)
        self.fp_email_fake_entry.pack()
        self.fp_email_fake_entry.pack_propagate(False)

        self.fp_email_entry = ctk.CTkEntry(self.fp_email_fake_entry, placeholder_text="example@gmail.com",
                                           height=24, font=self.body_light_font, fg_color="transparent",
                                           border_width=0, text_color=self.text_color)
        self.fp_email_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        self.fp_email_entry.bind("<Return>", lambda e: self._send_reset_code())

        self.fp_email_error = ctk.CTkLabel(email_frame, text="", text_color=self.error_red,
                                           font=self.inline_error_font)
        self.fp_email_error.pack(anchor="w", padx=(15, 0))

        self.fp_send_btn = ctk.CTkButton(self.step1_frame, text="SEND CODE", width=400, height=45,
                                          corner_radius=6, font=self.body_bold_font,
                                          fg_color=self.primary_color, hover_color=self.hover_color,
                                          text_color="#FFFFFF", command=self._send_reset_code)
        self.fp_send_btn.pack(pady=(25, 0))

    def _build_step2(self):
        self.step2_frame = ctk.CTkFrame(self.step_container, fg_color="transparent")

        desc = ctk.CTkLabel(self.step2_frame, text="Enter the 6-digit code sent to your email.",
                            font=self.body_paragraph_font, text_color=self.text_color)
        desc.pack(pady=(0, 20))

        code_frame = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        code_frame.pack()

        code_label = ctk.CTkLabel(code_frame, text="Verification Code", font=self.body_light_font,
                                  text_color=self.text_color)
        code_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        self.fp_code_fake_entry = ctk.CTkFrame(code_frame, width=400, height=50,
                                                fg_color=self.fg_color, border_color=self.entry_border,
                                                border_width=1, corner_radius=6)
        self.fp_code_fake_entry.pack()
        self.fp_code_fake_entry.pack_propagate(False)

        self.fp_code_entry = ctk.CTkEntry(self.fp_code_fake_entry, placeholder_text="000000",
                                          height=24, font=self.body_light_font, fg_color="transparent",
                                          border_width=0, text_color=self.text_color)
        self.fp_code_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        self.fp_code_entry.bind("<Return>", lambda e: self._verify_code())

        self.fp_code_error = ctk.CTkLabel(code_frame, text="", text_color=self.error_red,
                                          font=self.inline_error_font)
        self.fp_code_error.pack(anchor="w", padx=(15, 0))

        verify_btn = ctk.CTkButton(self.step2_frame, text="VERIFY CODE", width=400, height=45,
                                   corner_radius=6, font=self.body_bold_font,
                                   fg_color=self.primary_color, hover_color=self.hover_color,
                                   text_color="#FFFFFF", command=self._verify_code)
        verify_btn.pack(pady=(25, 0))

        back_step_btn = ctk.CTkButton(self.step2_frame, text="Back to email",
                                      font=self.body_paragraph_font,
                                      text_color=self.primary_color, fg_color="transparent",
                                      hover_color=self.hover_color_text,
                                      width=0, height=20, command=lambda: self._show_step(1))
        back_step_btn.pack(pady=(10, 0))

    def _build_step3(self):
        self.step3_frame = ctk.CTkFrame(self.step_container, fg_color="transparent")

        desc = ctk.CTkLabel(self.step3_frame, text="Enter your new password.",
                            font=self.body_paragraph_font, text_color=self.text_color)
        desc.pack(pady=(0, 20))

        pwd_frame = ctk.CTkFrame(self.step3_frame, fg_color="transparent")
        pwd_frame.pack()

        new_pwd_label = ctk.CTkLabel(pwd_frame, text="New Password", font=self.body_light_font,
                                     text_color=self.text_color)
        new_pwd_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        self.fp_new_pwd_fake_entry = ctk.CTkFrame(pwd_frame, width=400, height=50,
                                                   fg_color=self.fg_color, border_color=self.entry_border,
                                                   border_width=1, corner_radius=6)
        self.fp_new_pwd_fake_entry.pack()
        self.fp_new_pwd_fake_entry.pack_propagate(False)

        self.fp_new_pwd_entry = ctk.CTkEntry(self.fp_new_pwd_fake_entry, placeholder_text="New password",
                                             height=24, show="\u2022", font=self.body_light_font,
                                             fg_color="transparent", border_width=0, text_color=self.text_color)
        self.fp_new_pwd_entry.place(relx=0.46, rely=0.5, relwidth=0.82, anchor="center")
        self.fp_new_pwd_entry.bind("<KeyRelease>", self._validate_pwd_strength)

        self.fp_new_pwd_eye = ctk.CTkLabel(self.fp_new_pwd_fake_entry, image=self.closed_eye_icon,
                                           text="", cursor="hand2")
        self.fp_new_pwd_eye.place(relx=0.9, rely=0.5, anchor="center")

        def _toggle_new_pwd(e):
            vis = not getattr(self, "_fp_new_pwd_visible", False)
            self._fp_new_pwd_visible = vis
            if vis:
                self.fp_new_pwd_entry.configure(show="")
                self._animate_eye(self.fp_new_pwd_eye, self._eye_frames_open)
            else:
                self.fp_new_pwd_entry.configure(show="\u2022")
                self._animate_eye(self.fp_new_pwd_eye, self._eye_frames_closed)
        self.fp_new_pwd_eye.bind("<Button-1>", _toggle_new_pwd)

        # Requirement checklist
        self.fp_req_frame = ctk.CTkFrame(pwd_frame, fg_color="transparent")
        self.fp_req_frame.pack(anchor="w", padx=(25, 0), pady=(5, 5))

        self.fp_req_length = ctk.CTkLabel(self.fp_req_frame, text="\u2717  8+ characters",
                                          font=self.inline_error_font,
                                          text_color=self.entry_border)
        self.fp_req_length.pack(anchor="w")

        self.fp_req_upper = ctk.CTkLabel(self.fp_req_frame, text="\u2717  Uppercase letter",
                                         font=self.inline_error_font,
                                         text_color=self.entry_border)
        self.fp_req_upper.pack(anchor="w")

        self.fp_req_number = ctk.CTkLabel(self.fp_req_frame, text="\u2717  Number",
                                          font=self.inline_error_font,
                                          text_color=self.entry_border)
        self.fp_req_number.pack(anchor="w")

        self.fp_req_special = ctk.CTkLabel(self.fp_req_frame, text="\u2717  Special character",
                                           font=self.inline_error_font,
                                           text_color=self.entry_border)
        self.fp_req_special.pack(anchor="w")

        self.fp_new_pwd_error = ctk.CTkLabel(pwd_frame, text="", text_color=self.error_red,
                                             font=self.inline_error_font)
        self.fp_new_pwd_error.pack(anchor="w", padx=(15, 0))

        confirm_pwd_label = ctk.CTkLabel(pwd_frame, text="Confirm Password", font=self.body_light_font,
                                         text_color=self.text_color)
        confirm_pwd_label.pack(anchor="w", padx=(15, 0), pady=(15, 5))

        self.fp_confirm_pwd_fake_entry = ctk.CTkFrame(pwd_frame, width=400, height=50,
                                                       fg_color=self.fg_color, border_color=self.entry_border,
                                                       border_width=1, corner_radius=6)
        self.fp_confirm_pwd_fake_entry.pack()
        self.fp_confirm_pwd_fake_entry.pack_propagate(False)

        self.fp_confirm_pwd_entry = ctk.CTkEntry(self.fp_confirm_pwd_fake_entry, placeholder_text="Confirm password",
                                                 height=24, show="\u2022", font=self.body_light_font,
                                                 fg_color="transparent", border_width=0, text_color=self.text_color)
        self.fp_confirm_pwd_entry.place(relx=0.46, rely=0.5, relwidth=0.82, anchor="center")
        self.fp_confirm_pwd_entry.bind("<KeyRelease>", self._validate_pwd_match)

        self.fp_confirm_pwd_eye = ctk.CTkLabel(self.fp_confirm_pwd_fake_entry, image=self.closed_eye_icon,
                                               text="", cursor="hand2")
        self.fp_confirm_pwd_eye.place(relx=0.9, rely=0.5, anchor="center")

        def _toggle_confirm_pwd(e):
            vis = not getattr(self, "_fp_confirm_pwd_visible", False)
            self._fp_confirm_pwd_visible = vis
            if vis:
                self.fp_confirm_pwd_entry.configure(show="")
                self._animate_eye(self.fp_confirm_pwd_eye, self._eye_frames_open)
            else:
                self.fp_confirm_pwd_entry.configure(show="\u2022")
                self._animate_eye(self.fp_confirm_pwd_eye, self._eye_frames_closed)
        self.fp_confirm_pwd_eye.bind("<Button-1>", _toggle_confirm_pwd)

        self.fp_confirm_pwd_error = ctk.CTkLabel(pwd_frame, text="", text_color=self.error_red,
                                                 font=self.inline_error_font)
        self.fp_confirm_pwd_error.pack(anchor="w", padx=(15, 0))

        reset_btn = ctk.CTkButton(self.step3_frame, text="RESET PASSWORD", width=400, height=45,
                                  corner_radius=6, font=self.body_bold_font,
                                  fg_color=self.primary_color, hover_color=self.hover_color,
                                  text_color="#FFFFFF", command=self._reset_password)
        reset_btn.pack(pady=(25, 0))

        back_step_btn = ctk.CTkButton(self.step3_frame, text="Back to code",
                                      font=self.body_paragraph_font,
                                      text_color=self.primary_color, fg_color="transparent",
                                      hover_color=self.hover_color_text,
                                      width=0, height=20, command=lambda: self._show_step(2))
        back_step_btn.pack(pady=(10, 0))

    def _show_step(self, step):
        for frame in (self.step1_frame, self.step2_frame, self.step3_frame):
            frame.pack_forget()

        target = {1: self.step1_frame, 2: self.step2_frame, 3: self.step3_frame}[step]
        target.pack()

    def _send_reset_code(self):
        email = self.fp_email_entry.get().strip()
        self.fp_email_error.configure(text="")
        self.fp_email_fake_entry.configure(border_color=self.entry_border)

        if not email:
            self.fp_email_error.configure(text="Please enter your email.")
            self.fp_email_fake_entry.configure(border_color=self.error_red)
            return

        self.fp_send_btn.configure(state="disabled", text="SENDING...")

        def _handle_send_result(resp):
            if resp.status_code == 200:
                self._reset_data["email"] = email
                self.show_toast("Reset code sent!", is_error=False)
                self.fp_code_entry.delete(0, "end")
                self.fp_code_error.configure(text="")
                self.fp_code_fake_entry.configure(border_color=self.entry_border)
                self._show_step(2)
                self.fp_code_entry.focus()
            else:
                self.fp_email_error.configure(text=resp.json().get("detail", "Failed to send code."))
                self.fp_email_fake_entry.configure(border_color=self.error_red)

        def _do():
            try:
                resp = self.api.post("/auth/forgot-password", json={"email": email}, timeout=15)
                self.after(0, lambda: _handle_send_result(resp))
            except ConnectionError:
                self.after(0, lambda: self.fp_email_error.configure(text="Cannot connect to server."))
            finally:
                self.after(0, lambda: self.fp_send_btn.configure(state="normal", text="SEND CODE"))

        threading.Thread(target=_do, daemon=True).start()

    def _verify_code(self):
        code = self.fp_code_entry.get().strip()
        self.fp_code_error.configure(text="")
        self.fp_code_fake_entry.configure(border_color=self.entry_border)

        if not code or len(code) != 6 or not code.isdigit():
            self.fp_code_error.configure(text="Please enter a valid 6-digit code.")
            self.fp_code_fake_entry.configure(border_color=self.error_red)
            return

        email = self._reset_data.get("email", "")
        if not email:
            self._show_step(1)
            return

        def _handle_verify_result(resp):
            if resp.status_code == 200:
                self._reset_data["code"] = code
                self.fp_new_pwd_entry.delete(0, "end")
                self.fp_confirm_pwd_entry.delete(0, "end")
                self.fp_new_pwd_error.configure(text="")
                self.fp_confirm_pwd_error.configure(text="")
                self.fp_new_pwd_fake_entry.configure(border_color=self.entry_border)
                self.fp_confirm_pwd_fake_entry.configure(border_color=self.entry_border)
                self._show_step(3)
                self.fp_new_pwd_entry.focus()
            else:
                self.fp_code_error.configure(text=resp.json().get("detail", "Invalid code."))
                self.fp_code_fake_entry.configure(border_color=self.error_red)

        def _do():
            try:
                resp = self.api.post("/auth/verify-reset-code", json={"email": email, "code": code}, timeout=5)
                self.after(0, lambda: _handle_verify_result(resp))
            except ConnectionError:
                self.after(0, lambda: self.fp_code_error.configure(text="Cannot connect to server."))

        threading.Thread(target=_do, daemon=True).start()

    def _validate_pwd_strength(self, event=None):
        password = self.fp_new_pwd_entry.get()

        checks = [
            (self.fp_req_length,  len(password) >= 8,                          "8+ characters"),
            (self.fp_req_upper,   bool(re.search(r"[A-Z]", password)),         "Uppercase letter"),
            (self.fp_req_number,  bool(re.search(r"[0-9]", password)),         "Number"),
            (self.fp_req_special, bool(re.search(r"[^a-zA-Z0-9\s]", password)), "Special character"),
        ]
        for label, met, text in checks:
            if met:
                label.configure(text=f"\u2713  {text}", text_color="green")
            else:
                label.configure(
                    text=f"\u2717  {text}",
                    text_color=self.error_red if password else self.entry_border
                )

    def _validate_pwd_match(self, event=None):
        password = self.fp_new_pwd_entry.get()
        confirm = self.fp_confirm_pwd_entry.get()

        if not confirm:
            self.fp_confirm_pwd_fake_entry.configure(border_color=self.entry_border)
            self.fp_confirm_pwd_error.configure(text="")
        elif password != confirm:
            self.fp_confirm_pwd_fake_entry.configure(border_color=self.error_red)
            self.fp_confirm_pwd_error.configure(text="Passwords do not match")
        else:
            self.fp_confirm_pwd_fake_entry.configure(border_color="green")
            self.fp_confirm_pwd_error.configure(text="")

    def _reset_password(self):
        new_pwd = self.fp_new_pwd_entry.get()
        confirm_pwd = self.fp_confirm_pwd_entry.get()

        self.fp_new_pwd_error.configure(text="")
        self.fp_confirm_pwd_error.configure(text="")
        self.fp_new_pwd_fake_entry.configure(border_color=self.entry_border)
        self.fp_confirm_pwd_fake_entry.configure(border_color=self.entry_border)

        has_error = False

        if not new_pwd or len(new_pwd) < 8:
            self.fp_new_pwd_error.configure(text="Password must be at least 8 characters.")
            self.fp_new_pwd_fake_entry.configure(border_color=self.error_red)
            has_error = True

        if not re.search(r"[A-Z]", new_pwd):
            self.fp_new_pwd_error.configure(text="Password must contain an uppercase letter.")
            self.fp_new_pwd_fake_entry.configure(border_color=self.error_red)
            has_error = True

        if not re.search(r"[0-9]", new_pwd):
            self.fp_new_pwd_error.configure(text="Password must contain a number.")
            self.fp_new_pwd_fake_entry.configure(border_color=self.error_red)
            has_error = True

        if not re.search(r"[^a-zA-Z0-9\s]", new_pwd):
            self.fp_new_pwd_error.configure(text="Password must contain a special character.")
            self.fp_new_pwd_fake_entry.configure(border_color=self.error_red)
            has_error = True

        if new_pwd != confirm_pwd:
            self.fp_confirm_pwd_error.configure(text="Passwords do not match.")
            self.fp_confirm_pwd_fake_entry.configure(border_color=self.error_red)
            has_error = True

        if has_error:
            return

        email = self._reset_data.get("email", "")
        code = self._reset_data.get("code", "")

        def _handle_reset_result(resp):
            if resp.status_code == 200:
                self.show_toast("Password reset successfully!", is_error=False)
                self.after(2000, self.show_login_page)
            else:
                self.fp_new_pwd_error.configure(text=resp.json().get("detail", "Failed to reset password."))
                self.fp_new_pwd_fake_entry.configure(border_color=self.error_red)

        def _do():
            try:
                resp = self.api.post("/auth/reset-password", json={
                    "email": email,
                    "code": code,
                    "new_password": new_pwd
                }, timeout=5)
                self.after(0, lambda: _handle_reset_result(resp))
            except ConnectionError:
                self.after(0, lambda: self.fp_new_pwd_error.configure(text="Cannot connect to server."))

        threading.Thread(target=_do, daemon=True).start()
