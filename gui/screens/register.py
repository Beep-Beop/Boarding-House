import re
import requests
import datetime

from gui.screens.register_form import RegisterFormMixin
from gui.screens.register_validation import RegisterValidationMixin

PHONE_PREFIX = "09"
PHONE_LENGTH = 11


class RegisterMixin(RegisterFormMixin, RegisterValidationMixin):
    def attempt_register(self):
        f_name = self.first_name_entry.get().strip()
        l_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        if phone == "Enter your mobile number":
            phone = ""

        month = self.month_box.get()
        day = self.day_box.get()
        year = self.year_box.get()

        province = self.province_menu.get().strip()
        city = self.city_menu.get().strip()
        barangay = self.barangay_menu.get().strip()
        street = self.street_entry.get().strip()

        password = self.create_pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()

        error_labels = [
            self.first_name_error_lbl, self.last_name_error_lbl, self.dob_error_lbl,
            self.email_error_lbl, self.phone_error_lbl, self.province_error_lbl,
            self.city_error_lbl, self.barangay_error_lbl, self.street_error_lbl,
            self.create_pass_error_lbl, self.confirm_pass_error_lbl, self.tos_error_lbl
        ]
        for lbl in error_labels:
            lbl.configure(text="")

        self.first_name_bg_frame.configure(border_color=self.entry_border)
        self.last_name_bg_frame.configure(border_color=self.entry_border)
        self.dob_bg_frame.configure(border_color=self.entry_border)
        self.email_bg_frame.configure(border_color=self.entry_border)
        self.phone_bg_frame.configure(border_color=self.entry_border)
        self.province_menu.configure(border_color=self.entry_border)
        self.city_menu.configure(border_color=self.entry_border)
        self.barangay_menu.configure(border_color=self.entry_border)
        self.street_bg_frame.configure(border_color=self.entry_border)
        self.create_pass_bg_frame.configure(border_color=self.entry_border)
        self.confirm_pass_bg_frame.configure(border_color=self.entry_border)

        has_error = False

        # Validate Basic Fields Inline
        if not f_name:
            self.first_name_error_lbl.configure(text="First name is required.")
            self.first_name_bg_frame.configure(border_color=self.error_red)
            has_error = True
        if not l_name:
            self.last_name_error_lbl.configure(text="Last name is required.")
            self.last_name_bg_frame.configure(border_color=self.error_red)
            has_error = True

        if month == "MM" or day == "DD" or year == "YYYY":
            self.dob_error_lbl.configure(text="Please complete your Date of Birth selection.")
            self.dob_bg_frame.configure(border_color=self.error_red)
            has_error = True
        dob_string = f"{year}-{month}-{day}"
        if not has_error:
            try:
                datetime.datetime.strptime(dob_string, "%Y-%m-%d")
            except ValueError:
                self.dob_error_lbl.configure(text="Invalid date (e.g. Feb 30 doesn't exist).")
                self.dob_bg_frame.configure(border_color=self.error_red)
                has_error = True

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not email:
            self.email_error_lbl.configure(text="Email address is required.")
            self.email_bg_frame.configure(border_color=self.error_red)
            has_error = True
        elif not re.match(email_pattern, email):
            self.email_error_lbl.configure(text="Incorrect email format.")
            self.email_bg_frame.configure(border_color=self.error_red)
            has_error = True

        if not phone:
            self.phone_error_lbl.configure(text="Phone number is required.")
            self.phone_bg_frame.configure(border_color=self.error_red)
            has_error = True
        elif not phone.startswith(PHONE_PREFIX):
            self.phone_error_lbl.configure(text=f"Mobile numbers must start with {PHONE_PREFIX}.")
            self.phone_bg_frame.configure(border_color=self.error_red)
            has_error = True
        elif len(phone) != PHONE_LENGTH:
            self.phone_error_lbl.configure(text=f"Must be exactly {PHONE_LENGTH} digits ({PHONE_PREFIX}XXXXXXXXX).")
            self.phone_bg_frame.configure(border_color=self.error_red)
            has_error = True

        # Validate Location Options (Typos)
        matched_prov = [p for p in getattr(self, "province_options", []) if p.lower() == province.lower()]
        if not matched_prov or province.startswith("Select"):
            self.province_error_lbl.configure(text="\u26a0 Select a valid Province from the list.")
            self.province_menu.configure(border_color=self.error_red)
            has_error = True
        else:
            province = matched_prov[0]
            self.province_menu.set(province)

        matched_cit = [c for c in getattr(self, "city_options", []) if c.lower() == city.lower()]
        if not matched_cit or city.startswith("Select") or city.startswith("Loading"):
            self.city_error_lbl.configure(text="Select a valid City from the list.")
            self.city_menu.configure(border_color=self.error_red)
            has_error = True
        else:
            city = matched_cit[0]
            self.city_menu.set(city)

        matched_brgy = [b for b in getattr(self, "barangay_options", []) if b.lower() == barangay.lower()]
        if not matched_brgy or barangay.startswith("Select") or barangay.startswith("Loading"):
            self.barangay_error_lbl.configure(text="Select a valid Barangay from the list.")
            self.barangay_menu.configure(border_color=self.error_red)
            has_error = True
        else:
            barangay = matched_brgy[0]
            self.barangay_menu.set(barangay)

        if not street:
            self.street_error_lbl.configure(text="Street address is required.")
            self.street_bg_frame.configure(border_color=self.error_red)
            has_error = True

        if not password:
            self.create_pass_error_lbl.configure(text="Password is required.")
            self.create_pass_bg_frame.configure(border_color=self.error_red)
            has_error = True
        elif not (len(password) >= 8 and re.search(r"[A-Z]", password) and
                  re.search(r"[0-9]", password) and re.search(r"[^a-zA-Z0-9\s]", password)):
            missing = []
            if len(password) < 8:                           missing.append("8+ chars")
            if not re.search(r"[A-Z]", password):          missing.append("uppercase")
            if not re.search(r"[0-9]", password):          missing.append("number")
            if not re.search(r"[^a-zA-Z0-9\s]", password): missing.append("special char")
            self.create_pass_error_lbl.configure(text=f"Password needs: {', '.join(missing)}.")
            self.create_pass_bg_frame.configure(border_color=self.error_red)
            has_error = True
        if password != confirm_password:
            self.confirm_pass_error_lbl.configure(text="Passwords do not match.")
            self.confirm_pass_bg_frame.configure(border_color=self.error_red)
            has_error = True

        if not self.tos_and_pp_checkbox.get():
            self.tos_error_lbl.configure(text="You must agree to the Terms of Service.")
            has_error = True

        if has_error:
            return

        self.create_acc_btn.configure(state="disabled", text="CREATING ACCOUNT...")
        try:
            # 3. Live Database Check for Existing Registration
            try:
                response = self.api.get(f"/users/check-email?email={email}", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("exists"):
                        provider = data.get("provider")
                        if provider in ("google", "both"):
                            msg = "Already signed up with Google. Use Google login."
                        else:
                            msg = "This email is already registered."
                        self.email_error_lbl.configure(text=msg)
                        self.email_bg_frame.configure(border_color=self.error_red)
                        return
            except requests.exceptions.ConnectionError:
                pass

            # 4. Create Account Payload Submission
            full_name = f"{f_name} {l_name}"
            user_data = {
                "name": full_name,
                "email": email,
                "password": password,
                "role": self.selected_account_type,
                "phone": phone,
                "province": province,
                "city": city,
                "barangay": barangay,
                "street": street,
                "date_of_birth": dob_string
            }

            response = self.api.post("/users/", json=user_data)
            if response.status_code == 201:
                self.show_toast("Account created!", is_error=False)
                try:
                    self.api.post("/auth/send-verification", json={"email": email}, timeout=15)
                except Exception:
                    self.show_toast("Failed to send verification email. Check your connection.", is_error=True)
                self.show_email_verification_page(email=email)
            elif response.status_code == 400:
                error_msg = response.json().get("detail", "Registration failed.")
                self.show_toast(error_msg, is_error=True)
            else:
                self.show_toast("Server error. Try again later.", is_error=True)
        except requests.exceptions.ConnectionError:
            self.show_toast("Error: Is your backend server running?", is_error=True)
        finally:
            self.create_acc_btn.configure(state="normal", text="CREATE ACCOUNT")
