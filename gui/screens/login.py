import threading
import customtkinter as ctk
from requests.exceptions import ConnectionError
from gui.screens.google_auth import GoogleAuthHandler


class LoginMixin:
    def _make_fake_entry(self, parent, placeholder, entry_kwargs=None):
        frame = ctk.CTkFrame(parent, width=400, height=40,
                             fg_color=self.fg_color,
                             border_color=self.entry_border,
                             border_width=1, corner_radius=6)
        frame.pack()
        frame.pack_propagate(False)
        kwargs = {
            "placeholder_text": placeholder,
            "height": 24,
            "font": self.body_light_font,
            "fg_color": "transparent",
            "border_width": 0,
            "text_color": self.text_color,
        }
        if entry_kwargs:
            kwargs.update(entry_kwargs)
        entry = ctk.CTkEntry(frame, **kwargs)
        entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        return frame, entry

    def show_login_page(self):
        print("[DEBUG] Showing: Login Page")
        self.clear_container()

        self.geometry("630x700")
        self.resizable(False, False)

        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=40, fill="both", expand=True)

        # Logo
        logo_label = ctk.CTkLabel(self.form_container,
                                  text=None,
                                  image=self.logo,
                                  width=140,
                                  height=32
                                  )
        logo_label.pack(pady=(20, 15))

        welcome_label = ctk.CTkLabel(self.form_container,
                                     text="WELCOME TO",
                                     height=5,
                                     width=121,
                                     font=self.body_light_font,
                                     text_color=self.text_color
                                    )
        welcome_label.pack(pady=(0, 7))

        title_label = ctk.CTkLabel(self.form_container,
                                   text="BOARDING HOUSE FINDER",
                                   width=273,
                                   height=20,
                                   font=self.alt_title_font,
                                   text_color=self.text_color
                                   )
        title_label.pack(pady=(0, 10))

        notes_label = ctk.CTkLabel(self.form_container,
                                   text="Please enter your login details",
                                   width=213,
                                   height=5,
                                   font=self.body_paragraph_font,
                                   text_color=self.text_color
                                   )
        notes_label.pack(pady=(0, 7))

        # Email Row
        email_frame = ctk.CTkFrame(self.form_container,
                                   fg_color="transparent"
                                   )
        email_frame.pack(pady=(0, 15))

        self.email_label = ctk.CTkLabel(email_frame,
                                        text="Email",
                                        font=self.body_light_font,
                                        text_color=self.text_color
                                        )
        self.email_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        # THE "FAKE" ENTRY (Visual box user sees)
        self.email_fake_entry, self.email_entry = self._make_fake_entry(
            email_frame, "example@gmail.com"
        )

        self.login_email_error = ctk.CTkLabel(email_frame,
                                              text="",
                                              text_color=self.error_red,
                                              font=self.inline_error_font
                                              )
        self.login_email_error.pack(anchor="w", padx=(15, 0))

        # Password Row
        password_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        password_frame.pack(pady=(0, 10))

        self.password_label = ctk.CTkLabel(password_frame,
                                           text="Password",
                                           font=self.body_light_font,
                                           text_color=self.text_color
                                           )
        self.password_label.pack(anchor="w", padx=(15, 0), pady=(0, 5))

        self.password_fake_entry, self.password_entry = self._make_fake_entry(
            password_frame, "Password", {"show": "\u2022"}
        )
        self.password_entry.place_configure(relx=0.46, relwidth=0.82)
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

        self.password_eye = ctk.CTkLabel(self.password_fake_entry,
                                         image=self.closed_eye_icon,
                                         text="",
                                         cursor="hand2",
                                         )
        self.password_eye.place(relx=0.9, rely=0.5, anchor="center")

        def _toggle_password_visible(e):
            self._password_visible = not getattr(self, "_password_visible", False)
            if self._password_visible:
                self.password_entry.configure(show="")
                self._animate_eye(self.password_eye, self._eye_frames_open)
            else:
                self.password_entry.configure(show="\u2022")
                self._animate_eye(self.password_eye, self._eye_frames_closed)
        self.password_eye.bind("<Button-1>", _toggle_password_visible)

        self.login_password_error = ctk.CTkLabel(password_frame,
                                                 text="",
                                                 text_color=self.error_red,
                                                 font=self.inline_error_font
                                                 )
        self.login_password_error.pack(anchor="w", padx=(15, 0))

        actions_frame = ctk.CTkFrame(password_frame, fg_color="transparent", width=400, height=30)
        actions_frame.pack(fill="x", pady=(10, 0))

        # 2. Pack the checkbox to the LEFT
        self.remember_checkbox = ctk.CTkCheckBox(actions_frame,
                                                text="Remember me",
                                                font=self.body_paragraph_font,
                                                text_color=self.text_color,
                                                fg_color=self.primary_color,
                                                hover_color=self.hover_color,
                                                border_color=self.entry_border,
                                                border_width=2,
                                                checkbox_height=20,
                                                checkbox_width=20
                                                )
        self.remember_checkbox.pack(side="left")

        self.forgot_pwd_btn = ctk.CTkButton(actions_frame,
                                            text="Forgot Password?",
                                            font=self.body_paragraph_font,
                                            text_color=self.primary_color,
                                            fg_color="transparent",
                                            hover_color=self.hover_color_text,
                                            cursor="hand2",
                                            width=0,
                                            height=20,
                                            command=self.forgot_password)
        self.forgot_pwd_btn.pack(side="right")

        # Login Action
        self.login_btn = ctk.CTkButton(self.form_container,
                                  text="LOG IN",
                                  width=400,
                                  height=45,
                                  corner_radius=6,
                                  font=self.body_bold_font,
                                  fg_color=self.primary_color,
                                  hover_color=self.hover_color,
                                  text_color="#FFFFFF",
                                  command=self.attempt_login
                                  )
        self.login_btn.pack(pady=(10, 10))

        self.google_label = ctk.CTkLabel(self.form_container,
                                         text="Or Continue With",
                                         width=153,
                                         height=20,
                                         font=self.body_paragraph_font,
                                         text_color=self.text_color
                                         )
        self.google_label.pack(pady=(15, 0))

        self.google_btn = ctk.CTkLabel(self.form_container,
                                       text="",
                                       image=self.google_icon,
                                       cursor="hand2"
                                       )
        self.google_btn.pack(pady=(0, 0))
        self.google_btn.bind("<Button-1>", lambda event: self.start_google_login())

        self._google_hint_label = ctk.CTkLabel(
            self.form_container,
            text="",
            font=self.body_paragraph_font,
            text_color=self.primary_color,
        )

        register_frame = ctk.CTkFrame(self.form_container,
                                      fg_color="transparent"
                                      )
        register_frame.pack(pady=(0, 0))

        self.new_member_label = ctk.CTkLabel(register_frame,
                                             text="New member here?",
                                             font=self.body_paragraph_font,
                                             text_color=self.text_color,
                                             )
        self.new_member_label.pack(side="left", padx=(0, 5))

        self.register_btn = ctk.CTkButton(register_frame,
                                          text="Register Now",
                                          font=ctk.CTkFont(family="Poppins", size=15, weight="bold"),
                                          text_color=self.primary_color,
                                          fg_color="transparent",
                                          hover_color=self.hover_color_text,
                                          width=0,
                                          height=20,
                                          command=self.show_account_type
                                          )
        self.register_btn.pack(side="left")

    def attempt_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        self.login_email_error.configure(text="")
        self.login_password_error.configure(text="")
        self.email_fake_entry.configure(border_color=self.entry_border)
        self.password_fake_entry.configure(border_color=self.entry_border)

        has_error = False

        if not email:
            self.login_email_error.configure(text="Please enter your email.")
            self.email_fake_entry.configure(border_color=self.error_red)
            has_error = True

        if not password:
            self.login_password_error.configure(text="Please enter your password.")
            self.password_fake_entry.configure(border_color=self.error_red)
            has_error = True

        if has_error:
            return

        self.login_btn.configure(state="disabled", text="LOGGING IN...")
        print("[DEBUG] attempt_login: sending POST /auth/login")
        try:
            login_data = {
                "email": email,
                "password": password,
                "remember_me": bool(self.remember_checkbox.get())
            }

            response = self.api.post("/auth/login", json=login_data)

            if response.status_code == 200:
                user_info = response.json()
                print(f"[DEBUG] Login OK — role={user_info.get('role')}, routing to dashboard")
                self.access_token = user_info.get("access_token")
                self.api.access_token = self.access_token
                self.current_user = user_info

                if self.remember_checkbox.get():
                    self._save_session(user_info)

                role = user_info.get('role')
                if role == 'admin':
                    self.show_admin_dashboard()
                elif role == 'owner':
                    self.show_owner_dashboard()
                else:
                    self.show_tenant_dashboard()

            elif response.status_code in [401, 403]:
                error_msg = response.json().get("detail", "Login Failed.")
                auth_hint = response.headers.get("X-Auth-Hint")
                if auth_hint == "google_login":
                    self._google_hint_cleared = False
                    self.login_email_error.configure(text=error_msg)
                    self.login_password_error.configure(text="")
                    self.email_fake_entry.configure(border_color=self.error_red)
                    self.password_fake_entry.configure(border_color=self.entry_border)
                    self.google_btn.configure(fg_color=self.error_red)
                    self.after(2000, lambda: self.google_btn.configure(fg_color="transparent"))
                    self._google_hint_label.configure(text="\u2b06 Sign in with Google above")
                    self._google_hint_label.pack(pady=(0, 5))
                    self.email_entry.bind("<Key>", self._clear_google_hint, add="+")
                    self.password_entry.bind("<Key>", self._clear_google_hint, add="+")
                else:
                    self.login_email_error.configure(text=error_msg)
                    self.login_password_error.configure(text=error_msg)
                    self.email_fake_entry.configure(border_color=self.error_red)
                    self.password_fake_entry.configure(border_color=self.error_red)

            else:
                self.login_email_error.configure(text="Server error, Try again Later.")
        except ConnectionError:
            print("[DEBUG] Login failed: ConnectionError — backend unreachable")
            self.login_email_error.configure(text="Error: Cannot connect to backend server")
            self.email_fake_entry.configure(border_color=self.error_red)
        finally:
            if self.login_btn.winfo_exists():
                self.login_btn.configure(state="normal", text="LOG IN")

    def _save_session(self, user_info):
        import json, os
        session_dir = os.path.expanduser("~/.boarding-house")
        os.makedirs(session_dir, exist_ok=True)
        with open(os.path.join(session_dir, "session.json"), "w") as f:
            json.dump(user_info, f)

    def _load_session(self):
        import json, os
        path = os.path.expanduser("~/.boarding-house/session.json")
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def _clear_session(self):
        import os
        path = os.path.expanduser("~/.boarding-house/session.json")
        if os.path.exists(path):
            os.remove(path)

    def start_google_login(self):
        print("[DEBUG] Starting Google Login flow")
        def on_success(user_info):
            self.access_token = user_info.get("access_token")
            self.api.access_token = self.access_token
            self.current_user = user_info

            if self.remember_checkbox.get():
                self._save_session(user_info)

            if not user_info.get("account_setup_complete", False):
                self.show_google_account_type(user_info)
                return

            self.show_toast(f"Welcome, {user_info['name']}", is_error=False)
            role = user_info.get('role')
            if role == 'admin':
                self.show_admin_dashboard()
            elif role == 'owner':
                self.show_owner_dashboard()
            else:
                self.show_tenant_dashboard()

        def on_error(msg):
            self.show_toast(msg, is_error=True)

        GoogleAuthHandler(self.api, self, on_success, on_error).start()

    def _clear_google_hint(self, event=None):
        if getattr(self, "_google_hint_cleared", False):
            return
        self._google_hint_cleared = True
        self._google_hint_label.pack_forget()
        self._google_hint_label.configure(text="")
        self.google_btn.configure(fg_color="transparent")

    def forgot_password(self):
        self.show_forgot_password_page()


