import customtkinter as ctk


class EmailVerifyMixin:
    def show_email_verification_page(self, email: str = None):
        self.clear_container()
        self.geometry("630x700")
        self.resizable(False, False)

        self._verify_email = email or ""

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

        title_label = ctk.CTkLabel(self.form_container, text="CHECK YOUR EMAIL",
                                    font=self.alt_title_font, text_color=self.text_color)
        title_label.pack(pady=(0, 15))

        # Email icon (use a text emoji)
        icon_label = ctk.CTkLabel(self.form_container, text="\u2709\ufe0f",
                                  font=ctk.CTkFont(size=64), text_color=self.primary_color)
        icon_label.pack(pady=(20, 15))

        info_label = ctk.CTkLabel(self.form_container,
                                  text=f"We sent a verification link to:\n{self._verify_email}\n\n"
                                       "Click the link in the email to verify your account.",
                                  font=self.body_big_font, text_color=self.text_color,
                                  justify="center")
        info_label.pack(pady=(0, 10))

        hint_label = ctk.CTkLabel(self.form_container,
                                  text="Didn't receive the email? Check your spam folder.",
                                  font=self.body_light_font, text_color=self.text_color)
        hint_label.pack(pady=(0, 20))

        login_btn = ctk.CTkButton(self.form_container, text="I'M VERIFIED, LOG IN",
                                  width=400, height=45, corner_radius=6,
                                  font=self.body_bold_font,
                                  fg_color=self.primary_color, hover_color=self.hover_color,
                                  text_color="#FFFFFF", command=self.show_login_page)
        login_btn.pack(pady=(10, 10))

        resend_btn = ctk.CTkButton(self.form_container, text="Resend verification email",
                                   font=self.body_paragraph_font,
                                   text_color=self.primary_color, fg_color="transparent",
                                   hover_color=self.hover_color_text,
                                   width=0, height=20, command=self._resend_verification)
        resend_btn.pack(pady=(5, 0))

    def _resend_verification(self):
        if not self._verify_email:
            self.show_toast("No email to resend.", is_error=True)
            return
        try:
            resp = self.api.post("/auth/send-verification", json={"email": self._verify_email}, timeout=15)
            if resp.status_code == 200:
                self.show_toast("Verification email resent!", is_error=False)
            else:
                self.show_toast(resp.json().get("detail", "Failed to resend."), is_error=True)
        except Exception:
            self.show_toast("Cannot connect to server.", is_error=True)
