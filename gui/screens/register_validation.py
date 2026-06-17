import re
import requests
import threading

PHONE_PREFIX = "09"
PHONE_LENGTH = 11


class RegisterValidationMixin:
    def validate_email_realtime(self, event=None):
        email = self.email_entry.get().strip()
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if hasattr(self, "_email_check_timer") and self._email_check_timer:
            self.after_cancel(self._email_check_timer)
            self._email_check_timer = None

        if not email:
            self.email_bg_frame.configure(border_color=self.entry_border)
            self.email_error_lbl.configure(text="")
        elif re.match(pattern, email):
            self.email_bg_frame.configure(border_color=self.entry_border)
            self.email_error_lbl.configure(text="Checking availability\u2026")
            self._email_check_timer = self.after(600, lambda e=email: self._check_email_availability(e))
        else:
            self.email_bg_frame.configure(border_color=self.error_red)
            self.email_error_lbl.configure(text="\u26a0 Invalid email format.")

    def _check_email_availability(self, email):
        def fetch():
            if not self._screen_active:
                return
            try:
                response = self.api.get(f"/users/check-email?email={email}", timeout=3)
                if response.status_code == 200:
                    exists = response.json().get("exists", False)
                    def update():
                        try:
                            if not self._screen_active:
                                return
                            if not hasattr(self, "email_bg_frame") or not self.email_bg_frame.winfo_exists():
                                return
                            if self.email_entry.get().strip() != email:
                                return
                            if exists:
                                provider = response.json().get("provider")
                                if provider in ("google", "both"):
                                    msg = "\u26a0 Already signed up with Google. Use Google login."
                                else:
                                    msg = "\u26a0 Email already registered."
                                self.email_bg_frame.configure(border_color=self.error_red)
                                self.email_error_lbl.configure(text=msg)
                            else:
                                self.email_bg_frame.configure(border_color="green")
                                self.email_error_lbl.configure(text="")
                        except Exception:
                            pass
                    self.after(0, update)
            except requests.exceptions.RequestException:
                def clear_checking():
                    try:
                        if not self._screen_active:
                            return
                        if hasattr(self, "email_error_lbl") and self.email_error_lbl.winfo_exists():
                            if self.email_error_lbl.cget("text") == "Checking availability\u2026":
                                self.email_error_lbl.configure(text="")
                                self.email_bg_frame.configure(border_color="green")
                    except Exception:
                        pass
                self.after(0, clear_checking)
        threading.Thread(target=fetch, daemon=True).start()

    def validate_phone_realtime(self, event=None):
        phone = self.phone_entry.get().strip()

        if not phone or phone == "Enter your mobile number":
            self.phone_bg_frame.configure(border_color=self.entry_border)
            self.phone_error_lbl.configure(text="")
        elif not phone.startswith(PHONE_PREFIX):
            self.phone_bg_frame.configure(border_color=self.error_red)
            self.phone_error_lbl.configure(text=f"Phone numbers must start with {PHONE_PREFIX}.")
        elif len(phone) != PHONE_LENGTH:
            self.phone_bg_frame.configure(border_color=self.error_red)
            self.phone_error_lbl.configure(text=f"Must be {PHONE_LENGTH} digits. ({len(phone)}/{PHONE_LENGTH})")
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

    def validate_password_strength_realtime(self, event=None):
        if not hasattr(self, "req_length") or not self.req_length.winfo_exists():
            return
        password = self.create_pass_entry.get()
        checks = [
            (self.req_length,  len(password) >= 8,                          "8+ characters"),
            (self.req_upper,   bool(re.search(r"[A-Z]", password)),         "Uppercase letter"),
            (self.req_number,  bool(re.search(r"[0-9]", password)),         "Number"),
            (self.req_special, bool(re.search(r"[^a-zA-Z0-9\s]", password)), "Special character"),
        ]
        for label, met, text in checks:
            if met:
                label.configure(text=f"\u2713  {text}", text_color="green")
            else:
                label.configure(
                    text=f"\u2717  {text}",
                    text_color=self.error_red if password else self.entry_border
                )

    def validate_phone(self, text):
        if text == "":
            return True
        if not text.isdigit() or len(text) > 11:
            return False
        if len(text) >= 1 and text[0] != "0":
            return False
        if len(text) >= 2 and text[1] != "9":
            return False
        return True

    def _filter_phone_input(self, *args):
        val = self.phone_var.get()
        filtered = "".join(c for c in val if c.isdigit())[:PHONE_LENGTH]
        if filtered != val:
            self.phone_var.set(filtered)
