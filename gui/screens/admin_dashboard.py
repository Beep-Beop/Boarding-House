import io
import webbrowser
import threading
import tkinter as tk
import requests
import customtkinter as ctk
from tkinter import ttk
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image


class AdminDashboardMixin:
    _admin_status_colors = {}

    def show_admin_dashboard(self):
        print("[DEBUG] Showing: Admin Dashboard")
        self.clear_container()
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{int(w * 0.85)}x{int(h * 0.85)}")
        self.resizable(True, True)

        self._admin_is_sidebar_expanded = True
        self._admin_status_colors = {
            "active": self.primary_color,
            "pending": self.hover_color,
            "cancelled": self.error_red,
            "banned": self.error_red,
            "resolved": self.primary_color,
            "dismissed": self.text_color,
            "reviewed": self.hover_color,
            "verified": "green",
            "available": self.primary_color,
            "occupied": self.hover_color,
        }

        self._admin_form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self._admin_form_container.pack(pady=0, fill="both", expand=True)

        self._build_admin_nav()

        self._admin_body_frame = ctk.CTkFrame(self._admin_form_container, fg_color="transparent")
        self._admin_body_frame.pack(fill="both", expand=True)

        self._build_admin_sidebar()

        self._admin_content_wrapper = ctk.CTkFrame(
            self._admin_body_frame, fg_color="transparent"
        )
        self._admin_content_wrapper.pack(
            side="left", fill="both", expand=True, padx=(10, 10), pady=20
        )

        self._set_active_admin_sidebar_btn("dashboard")
        self._build_admin_dashboard_content()

    # ── Navbar ──

    def _build_admin_nav(self):
        nav = ctk.CTkFrame(
            self._admin_form_container,
            fg_color="transparent",
            height=60,
            border_width=1,
            border_color=self.entry_border,
        )
        nav.pack(side="top", fill="x")

        ctk.CTkButton(
            nav,
            image=self.hamburg_menu_icon,
            text=None,
            fg_color="transparent",
            hover_color=self.hover_color,
            width=25,
            height=15,
            command=self._admin_animate_sidebar,
        ).pack(side="left", padx=15, pady=(20, 25))

        ctk.CTkLabel(nav, text=None, image=self.logo).pack(side="left", pady=(15, 20))

        notif_frame = ctk.CTkFrame(nav, fg_color="transparent")
        notif_frame.pack(side="right", padx=(0, 5))

        notif_btn = ctk.CTkLabel(notif_frame, text="", image=self.notification_icon, cursor="hand2")
        notif_btn.pack(side="left", padx=5)
        notif_btn.bind("<Button-1>", lambda e: self.show_notifications_page())

        self._admin_notif_badge = ctk.CTkLabel(
            notif_frame, text="",
            width=16, height=16, corner_radius=8,
            fg_color=self.error_red, text_color="white",
            font=ctk.CTkFont(size=9, weight="bold"),
        )
        self._admin_notif_badge.place(x=18, y=-2)

        self._admin_profile_frame = ctk.CTkFrame(nav, fg_color="transparent")
        self._admin_profile_frame.pack(side="right", padx=25, pady=10)

        self._admin_nav_pfp = ctk.CTkLabel(self._admin_profile_frame, text=None,
                                            image=self.pfp_placeholder_sm,
                                            width=32, height=32, cursor="hand2")
        self._admin_nav_pfp.pack(side="left", padx=(0, 12))
        text_frame = ctk.CTkFrame(self._admin_profile_frame, fg_color="transparent")
        text_frame.pack(side="left")

        user_name = getattr(self, "current_user", {}).get("name", "Admin")

        ctk.CTkLabel(text_frame, text=user_name, font=self.body_light_font,
                      text_color=self.text_color).pack(side="left")

        self._admin_profile_chevron = ctk.CTkLabel(text_frame, text="▾",
                                                    font=self.body_light_font,
                                                    text_color=self.text_color)
        self._admin_profile_chevron.pack(side="left", padx=(4, 0))

        self._admin_profile_frame.configure(cursor="hand2")

        self._admin_nav_bar = nav
        self._admin_notif_frame = notif_frame

    # ── Sidebar ──

    def _build_admin_sidebar(self):
        sidebar = ctk.CTkFrame(
            self._admin_body_frame,
            fg_color="transparent",
            width=250,
            corner_radius=0,
            border_color=self.entry_border,
            border_width=1,
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self._admin_sidebar = sidebar

        menu_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, pady=20)

        items = [
            ("dashboard", "Dashboard",                   self._build_admin_dashboard_content),
            ("users",     "Manage User",                 self._build_admin_users_content),
            ("listings",  "Manage\nBoarding Houses",     self._build_admin_listings_content),
            ("bookings",  "Bookings",                    self._build_admin_bookings_content),
            ("reviews",   "Reviews &\nFeedback",         self._build_admin_reviews_content),
            ("reports",   "Reports",                     self._build_admin_reports_content),
            ("logs",      "Admin Logs",                  self._build_admin_logs_content),
            ("admins",    "Admin\nAccount Creation",     self._build_admin_management_content),
        ]

        self._admin_sidebar_btns = {}
        for i, (key, text, cmd) in enumerate(items):
            is_multi = "\n" in text
            btn = ctk.CTkButton(
                menu_frame, text=text, width=230, height=50 if is_multi else 40,
                hover_color=self.hover_color, fg_color="transparent",
                text_color=self.text_color, font=self.body_big_font,
                command=lambda k=key, cb=cmd: (
                    self._set_active_admin_sidebar_btn(k),
                    self._admin_clear_content(),
                    cb(),
                ),
                anchor="center",
            )
            btn.grid(row=i, column=0, padx=10, pady=(0, 10), sticky="ew")
            self._admin_sidebar_btns[key] = btn

    def _set_active_admin_sidebar_btn(self, active):
        for name, btn in self._admin_sidebar_btns.items():
            if name == active:
                btn.configure(fg_color=self.primary_color, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=self.text_color)

    def _admin_clear_content(self):
        for w in self._admin_content_wrapper.winfo_children():
            w.destroy()

    # ── Sidebar Animation ──

    def _admin_animate_sidebar(self):
        self._animate_sidebar_shared(
            self._admin_sidebar, '_admin_sidebar_width', '_admin_is_sidebar_expanded',
            self._admin_content_wrapper
        )

    # ── User Menu ──

    def _admin_toggle_user_menu(self):
        if hasattr(self, '_user_menu') and self._user_menu and self._user_menu.winfo_exists():
            self._hide_user_menu()
        else:
            self._show_user_menu(
                parent=self._admin_form_container,
                anchor=self._admin_profile_frame,
                form_container=self._admin_form_container,
                items=[
                    ("Account Settings", self.menu_profile_icon,  self.show_account_settings),
                    None,
                    ("Notifications",  self.notification_icon,  self.show_notifications_page),
                    None,
                    ("Logout",         self.menu_logout_icon,   self._handle_logout),
                ],
            )
            if hasattr(self, '_admin_profile_chevron'):
                self._admin_profile_chevron.configure(text="▴")

    # ── Helper: Stat Card Row ──

    def _admin_build_stat_cards(self, parent, cards):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 15))
        frame.grid_columnconfigure(tuple(range(len(cards))), weight=1, uniform="admin_stat")
        labels = {}
        for i, (title, key, accent) in enumerate(cards):
            card = ctk.CTkFrame(
                frame, fg_color=self.secondary_color,
                corner_radius=6, height=100,
                border_width=1, border_color=self.entry_border,
            )
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            card.pack_propagate(False)
            card.grid_propagate(False)
            accent_bar = ctk.CTkFrame(card, height=4, fg_color=accent, corner_radius=0)
            accent_bar.place(x=0, y=0, relwidth=1)
            ctk.CTkLabel(card, text=title, font=self.body_big_font,
                          text_color=self.primary_color).place(x=12, y=12)
            val_lbl = ctk.CTkLabel(card, text="...", font=self.body_bold_paragraph_font,
                                    text_color=accent)
            val_lbl.place(x=12, y=50)
            labels[key] = val_lbl
            card.bind("<Enter>", lambda e, c=card: c.configure(
                fg_color=self.hover_color, border_color=self.primary_color))
            card.bind("<Leave>", lambda e, c=card: c.configure(
                fg_color=self.secondary_color, border_color=self.entry_border))
        return labels

    # ── Helper: Data Table ──

    def _admin_build_table_header(self, parent, headers, col_weights=None):
        header_frame = ctk.CTkFrame(parent, fg_color=self.secondary_color, corner_radius=6)
        header_frame.pack(fill="x", pady=(0, 5))
        if col_weights is None:
            col_weights = [1] * len(headers)
        for j, h in enumerate(headers):
            ctk.CTkLabel(header_frame, text=h, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=0, column=j, padx=10, pady=8, sticky="w")
            header_frame.grid_columnconfigure(j, weight=col_weights[j], minsize=70)
        return header_frame

    def _admin_status_badge(self, parent, status, **kwargs):
        color = self._admin_status_colors.get(status.lower(), self.text_color)
        lbl = ctk.CTkLabel(
            parent, text=status.capitalize(), font=self.body_description_font,
            fg_color=color, text_color="white", corner_radius=4, padx=8, pady=2, **kwargs)
        return lbl

    # ── Loading Helpers ──

    def _admin_show_loading(self, parent):
        self._admin_hide_loading()
        self._admin_progress = ctk.CTkProgressBar(
            parent, mode="indeterminate",
            fg_color=self.entry_border, progress_color=self.primary_color)
        self._admin_progress.pack(fill="x", pady=(0, 10))
        self._admin_progress.start()

    def _admin_hide_loading(self):
        p = getattr(self, '_admin_progress', None)
        if p:
            try:
                p.stop()
                p.pack_forget()
            except Exception:
                pass
            self._admin_progress = None

    # ── Helper: Confirmation Dialog ──

    def _admin_confirm_action(self, prompt, title="Confirm"):
        dialog = ctk.CTkInputDialog(text=prompt, title=title)
        return dialog.get_input()

    # ── Helper: Search Bar ──

    def _admin_build_search_bar(self, parent, placeholder, search_cb, has_filter=False, filter_values=None):
        bg = ctk.CTkFrame(parent, fg_color=self.secondary_color, corner_radius=6, height=50)
        bg.pack(fill="x", pady=(0, 15))
        bg.pack_propagate(False)

        ctk.CTkLabel(bg, image=self.search_icon, text=None).pack(side="left", padx=(15, 10))

        entry = ctk.CTkEntry(
            bg, placeholder_text=placeholder, font=self.body_paragraph_font,
            fg_color="transparent", border_width=0)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

        if has_filter and filter_values:
            combo = ctk.CTkComboBox(
                bg, values=filter_values, width=140, height=32,
                font=self.body_paragraph_font, fg_color=self.fg_color,
                border_color=self.entry_border, border_width=1,
                button_color=self.primary_color, button_hover_color=self.hover_color,
                dropdown_fg_color=self.fg_color, dropdown_text_color=self.text_color,
                dropdown_hover_color=self.hover_color, dropdown_font=self.body_light_font,
                text_color=self.text_color,
                state="readonly")
            combo.pack(side="right", padx=(0, 15))
            combo.set("All")
        else:
            combo = None

        if search_cb:
            entry.bind("<KeyRelease>", lambda e: self._admin_debounce_search(search_cb))

        return entry, combo

    def _admin_debounce_search(self, cb):
        if hasattr(self, "_admin_search_timer"):
            try:
                self.after_cancel(self._admin_search_timer)
            except Exception:
                pass
        self._admin_search_timer = self.after(300, cb)

    # ════════════════════════════════════
    #  SECTION 1: DASHBOARD
    # ════════════════════════════════════

    def _build_admin_dashboard_content(self):
        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        user_name = getattr(self, "current_user", {}).get("name", "Admin")
        welcome = ctk.CTkFrame(main, fg_color=self.secondary_color, corner_radius=8,
                                height=90, border_width=1, border_color=self.entry_border)
        welcome.pack(fill="x", pady=(0, 15))
        welcome.pack_propagate(False)
        inner = ctk.CTkFrame(welcome, fg_color="transparent")
        inner.pack(fill="both", padx=20, pady=10)
        accent = ctk.CTkFrame(inner, width=4, fg_color=self.primary_color, corner_radius=2)
        accent.pack(side="left", fill="y", padx=(0, 12))
        ctk.CTkLabel(inner, text=f"Welcome back, {user_name}!",
                      font=self.body_bold_paragraph_font,
                      text_color=self.text_color).pack(anchor="w")
        today_str = datetime.now().strftime("%A, %B %d, %Y")
        ctk.CTkLabel(inner, text=today_str, font=self.body_light_font,
                      text_color=self.text_color).pack(anchor="w")

        self._admin_show_loading(main)

        stats_cards = [
            ("Total Users", "total_users", self.primary_color),
            ("Total Listings", "total_listings", self.hover_color),
            ("Active Bookings", "active_bookings", self.primary_color),
            ("Pending Reports", "pending_reports", self.error_red),
            ("Pending Permits", "pending_permits", self.hover_color),
        ]
        self._admin_dash_stat_labels = self._admin_build_stat_cards(main, stats_cards)

        recent_frame = ctk.CTkFrame(main, fg_color="transparent")
        recent_frame.pack(fill="x", pady=(0, 15))
        recent_frame.grid_columnconfigure((0, 1), weight=1, uniform="admin_recent")

        left_card = ctk.CTkFrame(recent_frame, fg_color=self.secondary_color,
                                  corner_radius=6, border_width=1, border_color=self.entry_border)
        left_card.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        ctk.CTkLabel(left_card, text="Recent Bookings", font=self.body_big_font,
                      text_color=self.primary_color).pack(anchor="w", padx=15, pady=(12, 10))
        self._admin_dash_bookings_container = ctk.CTkFrame(left_card, fg_color="transparent")
        self._admin_dash_bookings_container.pack(fill="x", padx=15, pady=(0, 12))
        ctk.CTkLabel(self._admin_dash_bookings_container, text="Loading...",
                      font=self.body_light_font, text_color=self.text_color).pack(anchor="w")

        right_card = ctk.CTkFrame(recent_frame, fg_color=self.secondary_color,
                                   corner_radius=6, border_width=1, border_color=self.entry_border)
        right_card.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        ctk.CTkLabel(right_card, text="Recent Admin Activity", font=self.body_big_font,
                      text_color=self.primary_color).pack(anchor="w", padx=15, pady=(12, 10))
        self._admin_dash_logs_container = ctk.CTkFrame(right_card, fg_color="transparent")
        self._admin_dash_logs_container.pack(fill="x", padx=15, pady=(0, 12))
        ctk.CTkLabel(self._admin_dash_logs_container, text="Loading...",
                      font=self.body_light_font, text_color=self.text_color).pack(anchor="w")

        self._admin_fetch_dashboard_stats()
        self._admin_fetch_notif_count()

    def _admin_fetch_dashboard_stats(self):
        def _do():
            data = {"total_users": "0", "total_listings": "0",
                    "active_bookings": "0", "pending_reports": "0", "pending_permits": "0"}
            bookings = []
            logs = []
            try:
                with ThreadPoolExecutor(max_workers=4) as pool:
                    f_users = pool.submit(lambda: self.api.get("/users/", timeout=5))
                    f_listings = pool.submit(lambda: self.api.get("/boarding-houses/admin/listings", timeout=5))
                    f_bookings = pool.submit(lambda: self.api.get("/bookings/stats", timeout=5))
                    f_reports = pool.submit(lambda: self.api.get("/reports/", timeout=5))

                    try:
                        resp = f_users.result()
                        if resp.status_code == 200:
                            users = resp.json()
                            data["total_users"] = str(len(users))
                            data["pending_permits"] = str(sum(1 for u in users if u.get("status") == "active"))
                    except Exception:
                        self.after(0, lambda: self.show_toast("Failed to load users. Check your connection.", is_error=True))

                    try:
                        resp = f_listings.result()
                        if resp.status_code == 200:
                            listings = resp.json()
                            data["total_listings"] = str(len(listings))
                            data["pending_permits"] = str(sum(1 for l in listings if not l.get("is_verified")))
                    except Exception:
                        self.after(0, lambda: self.show_toast("Failed to load listings. Check your connection.", is_error=True))

                    try:
                        resp = f_bookings.result()
                        if resp.status_code == 200:
                            stats = resp.json()
                            data["active_bookings"] = str(stats.get("active_count", "0"))
                    except Exception:
                        self.after(0, lambda: self.show_toast("Failed to load booking stats. Check your connection.", is_error=True))

                    try:
                        resp = f_reports.result()
                        if resp.status_code == 200:
                            reports = resp.json()
                            data["pending_reports"] = str(sum(1 for r in reports if r.get("status") == "pending"))
                    except Exception:
                        self.after(0, lambda: self.show_toast("Failed to load reports. Check your connection.", is_error=True))

                try:
                    resp_b = self.api.get("/bookings/all?limit=5", timeout=5)
                    bookings = resp_b.json().get("bookings", []) if resp_b.status_code == 200 else []
                except Exception:
                    self.after(0, lambda: self.show_toast("Failed to load recent bookings. Check your connection.", is_error=True))
                try:
                    resp_l = self.api.get("/admin-logs/", timeout=5)
                    logs = resp_l.json()[:5] if resp_l.status_code == 200 else []
                except Exception:
                    self.after(0, lambda: self.show_toast("Failed to load admin logs. Check your connection.", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load dashboard data. Check your connection.", is_error=True))

            self.after(0, lambda: (
                self._admin_hide_loading(),
                self._admin_populate_dash_stats(data),
                self._admin_populate_dash_recent(bookings, logs),
            ))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_dash_stats(self, data):
        for key, lbl in self._admin_dash_stat_labels.items():
            val = data.get(key, "0")
            try:
                lbl.configure(text=val)
            except Exception:
                pass

    def _admin_populate_dash_recent(self, bookings, logs):
        try:
            for w in self._admin_dash_bookings_container.winfo_children():
                w.destroy()
        except Exception:
            return
        if bookings:
            for b in bookings[:5]:
                text = f"#{b.get('booking_id')} - {b.get('tenant_name', '?')} ({b.get('status', '?')})"
                ctk.CTkLabel(self._admin_dash_bookings_container, text=text,
                              font=self.body_description_font,
                              text_color=self.text_color).pack(anchor="w", pady=1)
        else:
            ctk.CTkLabel(self._admin_dash_bookings_container, text="No recent bookings",
                          font=self.body_light_font, text_color=self.text_color).pack(anchor="w")

        try:
            for w in self._admin_dash_logs_container.winfo_children():
                w.destroy()
        except Exception:
            return
        if logs:
            for log in logs[:5]:
                ts = str(log.get("performed_at", "") or "")[:16]
                text = f"{ts} - {log.get('action', '?')}"
                ctk.CTkLabel(self._admin_dash_logs_container, text=text,
                              font=self.body_description_font,
                              text_color=self.text_color).pack(anchor="w", pady=1)
        else:
            ctk.CTkLabel(self._admin_dash_logs_container, text="No recent activity",
                          font=self.body_light_font, text_color=self.text_color).pack(anchor="w")

    # ════════════════════════════════════
    #  SECTION 2: USERS
    # ════════════════════════════════════

    def _build_admin_users_content(self):
        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main, text="User Management", font=self.body_bold_font,
                      text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        self._admin_users_search_entry, _ = self._admin_build_search_bar(
            main, "Search by name or email...", self._admin_refresh_users)

        card = ctk.CTkFrame(main, fg_color=self.secondary_color, corner_radius=6)
        card.pack(fill="both", expand=True, pady=(10, 0))
        self._admin_users_container = card

        self._admin_refresh_users()

    def _admin_refresh_users(self):
        card = self._admin_users_container
        for w in card.winfo_children():
            w.destroy()

        self._admin_show_loading(card)

        def _do():
            users = []
            try:
                resp = self.api.get("/users/", timeout=5)
                if resp.status_code == 200:
                    users = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load users. Check your connection.", is_error=True))
            search = ""
            try:
                search = self._admin_users_search_entry.get().strip().lower()
            except Exception:
                pass
            if search:
                users = [u for u in users if
                         search in u.get("name", "").lower() or
                         search in u.get("email", "").lower()]
            self.after(0, lambda: self._admin_populate_users(users))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_users(self, users):
        self._admin_hide_loading()
        card = self._admin_users_container
        for w in card.winfo_children():
            w.destroy()

        sticky_h = ["w", "w", "w", "w", "w", "ew"]
        card.grid_columnconfigure(0, weight=0, minsize=50)
        card.grid_columnconfigure(1, weight=1, minsize=160)
        card.grid_columnconfigure(2, weight=1, minsize=180)
        card.grid_columnconfigure(3, weight=0, minsize=80)
        card.grid_columnconfigure(4, weight=0, minsize=80)
        card.grid_columnconfigure(5, weight=0, minsize=160)

        headers = ["ID", "Name", "Email", "Role", "Status", "Actions"]
        for j, header in enumerate(headers):
            ctk.CTkLabel(card, text=header, font=self.body_bold_font,
                          text_color=self.text_color).grid(
                row=0, column=j, padx=15, pady=(15, 10), sticky=sticky_h[j])

        if not users:
            ctk.CTkLabel(card, text="No users found.",
                          font=self.body_paragraph_font,
                          text_color=self.text_color).grid(row=1, column=0, columnspan=6, padx=15, pady=20)
            return

        for r, user in enumerate(users):
            data_row = 1 + r * 2
            sep_row = data_row + 1
            is_last = r == len(users) - 1

            ctk.CTkLabel(card, text=str(user.get("user_id", "")), font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=0, padx=15, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=user.get("name", ""), font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=1, padx=10, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=user.get("email", ""), font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=2, padx=10, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=user.get("role", ""), font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=3, padx=10, pady=(7, 7), sticky="w")

            status = user.get("status", "active")
            s_color = self._admin_status_colors.get(status, self.text_color)
            ctk.CTkLabel(card, text=status.capitalize(), font=self.body_description_font,
                          fg_color=s_color, text_color="white",
                          corner_radius=4, padx=8, pady=2).grid(
                row=data_row, column=4, padx=15, pady=(7, 7), sticky="ew")

            uid = user.get("user_id")
            actions_f = ctk.CTkFrame(card, fg_color="transparent")
            actions_f.grid(row=data_row, column=5, padx=15, pady=(7, 7))
            if status != "banned":
                ctk.CTkButton(actions_f, text="Ban", font=self.body_description_font,
                              fg_color=self.error_red, text_color="white",
                              width=50, height=25,
                              command=lambda uid=uid: self._admin_ban_user(uid)).pack(side="left", padx=2)
            else:
                ctk.CTkButton(actions_f, text="Unban", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              width=50, height=25,
                              command=lambda uid=uid: self._admin_unban_user(uid)).pack(side="left", padx=2)

            if not is_last:
                ttk.Separator(card, orient="horizontal").grid(
                    row=sep_row, column=0, columnspan=6, padx=20, pady=4, sticky="ew")

    def _admin_ban_user(self, user_id):
        result = self._admin_confirm_action(f"Type BAN to ban user #{user_id}:", "Ban User")
        if result != "BAN":
            return
        try:
            resp = self.api.patch(f"/users/{user_id}/status?new_status=banned", timeout=10)
            if resp.status_code == 200:
                self.show_toast(f"User {user_id} banned", is_error=False)
            else:
                self.show_toast("Failed to ban user", is_error=True)
        except Exception:
            self.show_toast("Cannot connect to server", is_error=True)
        self._admin_refresh_users()

    def _admin_unban_user(self, user_id):
        try:
            resp = self.api.patch(f"/users/{user_id}/status?new_status=active", timeout=10)
            if resp.status_code == 200:
                self.show_toast(f"User {user_id} unbanned", is_error=False)
            else:
                self.show_toast("Failed to unban user", is_error=True)
        except Exception:
            self.show_toast("Cannot connect to server", is_error=True)
        self._admin_refresh_users()

    # ════════════════════════════════════
    #  SECTION 3: LISTINGS + PERMIT VERIFIER (COMBINED)
    # ════════════════════════════════════

    def _build_admin_listings_content(self):
        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main, text="Manage Boarding Houses & Permits",
                      font=self.body_bold_font,
                      text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        self._admin_listings_search_entry, self._admin_listings_filter = \
            self._admin_build_search_bar(
                main, "Search by name...", self._admin_refresh_listings,
                has_filter=True, filter_values=["All", "active", "pending", "banned"])

        card = ctk.CTkFrame(main, fg_color=self.secondary_color, corner_radius=6)
        card.pack(fill="both", expand=True, pady=(10, 0))
        self._admin_listings_container = card

        self._admin_refresh_listings()
        self._enable_scroll_refresh(scroll, self._admin_refresh_listings)

    def _admin_refresh_listings(self):
        card = self._admin_listings_container
        for w in card.winfo_children():
            w.destroy()

        self._admin_show_loading(card)

        def _do():
            listings = []
            try:
                resp = self.api.get("/boarding-houses/admin/listings", timeout=5)
                if resp.status_code == 200:
                    listings = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load listings. Check your connection.", is_error=True))
            search = ""
            status_filter = "All"
            try:
                search = self._admin_listings_search_entry.get().strip().lower()
            except Exception:
                pass
            try:
                status_filter = self._admin_listings_filter.get()
            except Exception:
                pass
            if search:
                listings = [l for l in listings if search in l.get("name", "").lower()]
            if status_filter != "All":
                listings = [l for l in listings if l.get("status") == status_filter]
            self.after(0, lambda: self._admin_populate_listings(listings))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_listings(self, listings):
        self._admin_hide_loading()
        card = self._admin_listings_container
        for w in card.winfo_children():
            w.destroy()

        sticky_h = ["w", "w", "w", "ew", "ew", "ew"]
        card.grid_columnconfigure(0, weight=2, minsize=160)
        card.grid_columnconfigure(1, weight=0, minsize=60)
        card.grid_columnconfigure(2, weight=1, minsize=120)
        card.grid_columnconfigure(3, weight=0, minsize=90)
        card.grid_columnconfigure(4, weight=0, minsize=100)
        card.grid_columnconfigure(5, weight=0, minsize=320)

        headers = ["Boarding House", "ID", "Location", "Status", "Verified", "Actions"]
        for j, header in enumerate(headers):
            ctk.CTkLabel(card, text=header, font=self.body_bold_font,
                          text_color=self.text_color).grid(
                row=0, column=j, padx=15, pady=(15, 10), sticky=sticky_h[j])

        if not listings:
            ctk.CTkLabel(card, text="No listings found.",
                          font=self.body_paragraph_font,
                          text_color=self.text_color).grid(row=1, column=0, columnspan=6, padx=15, pady=20)
            return

        for r, listing in enumerate(listings):
            data_row = 1 + r * 2
            sep_row = data_row + 1
            is_last = r == len(listings) - 1

            lid = listing.get("id", listing.get("listing_id"))
            name = listing.get("name", listing.get("bh_name", "Untitled"))
            location = listing.get("location", "Unknown")
            status = listing.get("status", "unknown")
            verified = listing.get("is_verified", False)

            ctk.CTkLabel(card, text=name, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=0, padx=15, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=f"#{lid}", font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=1, padx=10, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=location, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=2, padx=10, pady=(7, 7), sticky="w")

            s_color = self._admin_status_colors.get(status, self.text_color)
            ctk.CTkLabel(card, text=status.capitalize(), font=self.body_description_font,
                          fg_color=s_color, text_color="white",
                          corner_radius=4, padx=8, pady=2).grid(
                row=data_row, column=3, padx=15, pady=(7, 7), sticky="ew")

            v_text = "Verified" if verified else "Unverified"
            v_color = "green" if verified else self.hover_color
            ctk.CTkLabel(card, text=v_text, font=self.body_description_font,
                          fg_color=v_color, text_color="white",
                          corner_radius=4, padx=8, pady=2).grid(
                row=data_row, column=4, padx=15, pady=(7, 7), sticky="ew")

            actions_f = ctk.CTkFrame(card, fg_color="transparent")
            actions_f.grid(row=data_row, column=5, padx=15, pady=(7, 7))

            col = 0
            ctk.CTkButton(actions_f, text="Detail", font=self.body_description_font,
                          fg_color=self.primary_color, hover_color=self.hover_color,
                          text_color="white", width=65, height=28, cursor="hand2",
                          command=lambda lid=lid: self._admin_show_listing_detail(lid)
                          ).grid(row=0, column=col, padx=(0, 4)); col += 1

            if status == "pending":
                ctk.CTkButton(actions_f, text="Approve", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              width=70, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_approve_listing(lid)
                              ).grid(row=0, column=col, padx=(0, 4)); col += 1

            if status != "banned":
                ctk.CTkButton(actions_f, text="Ban", font=self.body_description_font,
                              fg_color=self.error_red, text_color="white",
                              width=55, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_ban_listing(lid)
                              ).grid(row=0, column=col, padx=(0, 2)); col += 1
            else:
                ctk.CTkButton(actions_f, text="Restore", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              width=65, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_restore_listing(lid)
                              ).grid(row=0, column=col, padx=(0, 4)); col += 1

            if not verified and status != "banned":
                ctk.CTkButton(actions_f, text="Verify Permit", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              width=95, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_approve_permit(lid)
                              ).grid(row=0, column=col, padx=(0, 4)); col += 1
                ctk.CTkButton(actions_f, text="Reject", font=self.body_description_font,
                              fg_color=self.error_red, text_color="white",
                              width=60, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_reject_permit(lid)
                              ).grid(row=0, column=col, padx=(0, 4)); col += 1
            elif verified:
                ctk.CTkButton(actions_f, text="Revoke", font=self.body_description_font,
                              fg_color=self.hover_color, text_color="white",
                              width=65, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_revoke_permit(lid)
                              ).grid(row=0, column=col, padx=(0, 4)); col += 1

            if not is_last:
                ttk.Separator(card, orient="horizontal").grid(
                    row=sep_row, column=0, columnspan=6, padx=20, pady=4, sticky="ew")

    def _admin_show_listing_detail(self, listing_id):
        self._admin_clear_content()
        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        back_btn = ctk.CTkLabel(header, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: (
            self._admin_clear_content(),
            self._build_admin_listings_content()))
        back_btn.bind("<Enter>", lambda e: back_btn.configure(image=self.bk_btn_hvr_icon))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(image=self.bk_btn_icon))
        ctk.CTkLabel(header, text="Listing Detail", font=self.alt_title_font,
                      text_color=self.text_color).pack(side="left", padx=10)

        loading = ctk.CTkLabel(main, text="Loading...", font=self.body_paragraph_font,
                                text_color=self.text_color)
        loading.pack(pady=30)

        def _do():
            data = None
            photos = []
            try:
                resp = self.api.get(f"/boarding-houses/{listing_id}", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load listing details. Check your connection.", is_error=True))
            try:
                resp = self.api.get(f"/photos/listing/{listing_id}", timeout=5)
                if resp.status_code == 200:
                    photos = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load photos. Check your connection.", is_error=True))
            self.after(0, lambda: self._admin_populate_listing_detail(main, data, photos))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_listing_detail(self, parent, data, photos=None):
        for w in parent.winfo_children():
            w.destroy()
        if not data:
            ctk.CTkLabel(parent, text="Failed to load listing details.",
                          font=self.body_paragraph_font, text_color=self.error_red).pack(pady=20)
            return

        name = data.get("bh_name", "Untitled")
        status = data.get("status", "unknown")
        verified = data.get("is_verified", False)
        color = self._admin_status_colors.get(status, self.text_color)

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        back_btn = ctk.CTkLabel(header, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: (
            self._admin_clear_content(),
            self._build_admin_listings_content()))
        back_btn.bind("<Enter>", lambda e: back_btn.configure(image=self.bk_btn_hvr_icon))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(image=self.bk_btn_icon))
        ctk.CTkLabel(header, text=name, font=self.alt_title_font,
                      text_color=self.text_color).pack(side="left", padx=10)

        hero = ctk.CTkFrame(parent, fg_color=self.secondary_color, corner_radius=6)
        hero.pack(fill="x", pady=(0, 15))
        inner = ctk.CTkFrame(hero, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(inner, text=name, font=self.body_bold_paragraph_font,
                      text_color=self.text_color).pack(side="left")
        ctk.CTkLabel(inner, text=status.capitalize(), font=self.body_paragraph_font,
                      fg_color=color, text_color="white",
                      corner_radius=4, padx=12, pady=4).pack(side="left", padx=(15, 0))
        if verified:
            ctk.CTkLabel(inner, text="Verified", font=self.body_paragraph_font,
                          fg_color="green", text_color="white",
                          corner_radius=4, padx=12, pady=4).pack(side="left", padx=(5, 0))
        else:
            ctk.CTkLabel(inner, text="Not Verified", font=self.body_paragraph_font,
                          fg_color=self.hover_color, text_color="white",
                          corner_radius=4, padx=12, pady=4).pack(side="left", padx=(5, 0))

        # ── Photo Gallery ──
        self._admin_build_photo_gallery(parent, photos or [])

        body = ctk.CTkFrame(parent, fg_color="transparent")
        body.pack(fill="x")
        body.grid_columnconfigure((0, 1), weight=1, uniform="detcol")

        left = ctk.CTkFrame(body, fg_color=self.secondary_color, corner_radius=6)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 15))
        ctk.CTkLabel(left, text="Property Details", font=self.body_big_font,
                      text_color=self.primary_color).pack(anchor="w", padx=15, pady=(15, 10))
        for label, val in [
            ("Type:", data.get("property_type", "N/A")),
            ("Price Range:", data.get("price_range", "N/A")),
            ("Min Stay:", f"{data.get('min_stay_months', 1)} months"),
            ("Description:", data.get("description", "N/A")),
            ("Rules:", data.get("rules", "N/A")),
        ]:
            row_f = ctk.CTkFrame(left, fg_color="transparent")
            row_f.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row_f, text=label, font=self.body_light_font,
                          text_color=self.text_color, width=100).pack(side="left")
            ctk.CTkLabel(row_f, text=str(val), font=self.body_paragraph_font,
                          text_color=self.text_color, wraplength=300,
                          justify="left").pack(side="left", padx=(10, 0), fill="x", expand=True)

        right = ctk.CTkFrame(body, fg_color=self.secondary_color, corner_radius=6)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 15))
        ctk.CTkLabel(right, text="Status & Info", font=self.body_big_font,
                      text_color=self.primary_color).pack(anchor="w", padx=15, pady=(15, 10))


        for label, val in [
            ("Listing ID:", f"#{data.get('listing_id', 'N/A')}"),
            ("Owner ID:", f"#{data.get('owner_id', 'N/A')}"),
            ("Created:", str(data.get("bh_created_at", ""))[:10] if data.get("bh_created_at") else "N/A"),
        ]:
            row_f = ctk.CTkFrame(right, fg_color="transparent")
            row_f.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row_f, text=label, font=self.body_light_font,
                          text_color=self.text_color, width=90).pack(side="left")
            ctk.CTkLabel(row_f, text=str(val), font=self.body_paragraph_font,
                          text_color=self.text_color).pack(side="left", padx=(10, 0))

        # Permit section
        permit_url = data.get("permit_url", "")
        pf = ctk.CTkFrame(right, fg_color="transparent")
        pf.pack(fill="x", padx=15, pady=(10, 5))
        ctk.CTkLabel(pf, text="Permit Document:", font=self.body_light_font,
                      text_color=self.text_color).pack(anchor="w")
        if permit_url:
            permit_img = ctk.CTkLabel(right, text="Loading...", font=self.body_description_font,
                                       fg_color=self.entry_border, height=150)
            permit_img.pack(fill="x", padx=15, pady=(5, 5))

            def load_permit():
                try:
                    resp = requests.get(permit_url, timeout=10)
                    pil = Image.open(io.BytesIO(resp.content)).copy()
                    self.after(0, lambda p=pil: (
                        setattr(permit_img, '_permit_img', ctk.CTkImage(p, size=(250, 150))),
                        permit_img.configure(image=permit_img._permit_img, text="")
                    ))
                except Exception:
                    self.after(0, lambda: permit_img.configure(text="[Not an image]"))

            threading.Thread(target=load_permit, daemon=True).start()
        else:
            ctk.CTkLabel(right, text="No permit document uploaded.",
                          font=self.body_description_font,
                          text_color=self.text_color).pack(anchor="w", padx=15, pady=(0, 10))

    def _admin_build_photo_gallery(self, parent, photos):
        gallery_frame = ctk.CTkFrame(parent, fg_color="transparent")
        gallery_frame.pack(fill="x", pady=(0, 15))

        if not photos:
            empty = ctk.CTkFrame(
                gallery_frame, fg_color=self.secondary_color,
                corner_radius=6, height=200,
            )
            empty.pack(fill="x")
            empty.pack_propagate(False)
            inner_empty = ctk.CTkFrame(empty, fg_color="transparent")
            inner_empty.place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkLabel(
                inner_empty, text="No Photos Available",
                font=self.body_paragraph_font, text_color=self.text_color,
            ).pack()
            return gallery_frame

        container = ctk.CTkFrame(gallery_frame, fg_color=self.secondary_color, corner_radius=6)
        container.pack(fill="x")

        canvas = tk.Canvas(
            container, height=470, highlightthickness=0,
            bg=self.secondary_color[0],
        )
        canvas.pack(side="top", fill="x")

        h_scrollbar = ctk.CTkScrollbar(
            container, orientation="horizontal",
            command=canvas.xview,
        )
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.configure(xscrollcommand=h_scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color="transparent")
        canvas.create_window((0, 0), window=inner, anchor="nw")

        def _update_scrollregion(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner.bind("<Configure>", _update_scrollregion)

        img_w, img_h = 600, 338

        for i, photo in enumerate(photos):
            url = photo.get("photo_url", "")
            if not url:
                continue
            card = ctk.CTkFrame(inner, fg_color=self.fg_color, corner_radius=4,
                                width=img_w + 16, height=img_h + 14)
            card.pack(side="left", padx=6, pady=10)
            card.pack_propagate(False)

            lbl = ctk.CTkLabel(card, text="", font=self.body_paragraph_font,
                               fg_color=self.entry_border)
            lbl.pack(fill="both", expand=True, padx=2, pady=2)

            def load(lb=lbl, u=url, w=img_w, h=img_h):
                try:
                    resp = requests.get(u, timeout=10)
                    pil = Image.open(io.BytesIO(resp.content)).copy()
                    self.after(0, lambda p=pil, lb=lb, w=w, h=h: self._admin_set_photo_image(lb, p, w, h, _update_scrollregion))
                except Exception:
                    self.after(0, lambda: lb.configure(text="Error", fg_color=self.error_red))

            threading.Thread(target=load, daemon=True).start()

        return gallery_frame

    def _admin_set_photo_image(self, label, pil_image, w, h, update_cb=None):
        try:
            ctk_image = ctk.CTkImage(pil_image, size=(w, h))
            label._ctk_img = ctk_image
            label.configure(image=ctk_image, text="")
            if update_cb:
                label.after(50, update_cb)
        except Exception:
            try:
                label.configure(text="Error", fg_color=self.error_red)
            except Exception:
                pass

    def _admin_ban_listing(self, listing_id):
        result = self._admin_confirm_action(f"Type BAN to ban listing #{listing_id}:", "Ban Listing")
        if result != "BAN":
            return
        def _do():
            try:
                resp = self.api.patch(f"/boarding-houses/{listing_id}", json={"status": "banned"}, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self.show_toast(f"Listing {listing_id} banned", is_error=False))
                else:
                    self.after(0, lambda: self.show_toast("Failed to ban listing", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, self._admin_refresh_listings)
        threading.Thread(target=_do, daemon=True).start()

    def _admin_restore_listing(self, listing_id):
        def _do():
            try:
                resp = self.api.patch(f"/boarding-houses/{listing_id}", json={"status": "active"}, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self.show_toast(f"Listing {listing_id} restored", is_error=False))
                else:
                    self.after(0, lambda: self.show_toast("Failed to restore listing", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, self._admin_refresh_listings)
        threading.Thread(target=_do, daemon=True).start()

    def _admin_approve_listing(self, listing_id):
        result = self._admin_confirm_action(
            f"Type APPROVE to approve listing #{listing_id} (this will also verify the permit):", "Approve Listing")
        if result != "APPROVE":
            return

        def _do():
            try:
                resp = self.api.patch(f"/boarding-houses/{listing_id}",
                                      json={"status": "active", "is_verified": True}, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self.show_toast(
                        f"Listing {listing_id} approved & permit verified", is_error=False))
                else:
                    self.after(0, lambda: self.show_toast("Failed to approve listing", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, self._admin_refresh_listings)
        threading.Thread(target=_do, daemon=True).start()

    def _admin_show_listing_actions(self, listing_id, current_status, is_verified):
        popup = ctk.CTkToplevel(self)
        popup.title("")
        popup.geometry("220x280+{}+{}".format(
            popup.winfo_pointerx() - 20, popup.winfo_pointery() - 20))
        popup.resizable(False, False)
        popup.transient(self)
        popup.attributes("-topmost", True)
        popup.focus_force()

        main = ctk.CTkFrame(popup, fg_color=self.secondary_color, corner_radius=6)
        main.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(main, text=f"Listing #{listing_id}",
                      font=self.body_paragraph_font, text_color=self.text_color).pack(pady=(10, 5))

        sep = ctk.CTkFrame(main, height=1, fg_color=self.entry_border)
        sep.pack(fill="x", padx=10, pady=2)

        def _cmd(label, fn):
            return lambda: (popup.destroy(), fn())

        # Approve (only if pending)
        if current_status == "pending":
            ctk.CTkButton(main, text="Approve Listing + Permit",
                          font=self.body_description_font,
                          fg_color="green", text_color="white",
                          anchor="w", cursor="hand2",
                          command=_cmd("Approve", lambda: self._admin_approve_listing(listing_id))
                          ).pack(fill="x", padx=10, pady=2)

        # Ban / Restore
        if current_status != "banned":
            ctk.CTkButton(main, text="Ban Listing",
                          font=self.body_description_font,
                          fg_color=self.error_red, text_color="white",
                          anchor="w", cursor="hand2",
                          command=_cmd("Ban", lambda: self._admin_ban_listing(listing_id))
                          ).pack(fill="x", padx=10, pady=2)
        else:
            ctk.CTkButton(main, text="Restore Listing",
                          font=self.body_description_font,
                          fg_color="green", text_color="white",
                          anchor="w", cursor="hand2",
                          command=_cmd("Restore", lambda: self._admin_restore_listing(listing_id))
                          ).pack(fill="x", padx=10, pady=2)

        # Permit actions
        if not is_verified:
            ctk.CTkButton(main, text="Approve Permit Only",
                          font=self.body_description_font,
                          fg_color="green", text_color="white",
                          anchor="w", cursor="hand2",
                          command=_cmd("Approve Permit",
                                       lambda: self._admin_approve_permit(listing_id))
                          ).pack(fill="x", padx=10, pady=2)
            ctk.CTkButton(main, text="Reject Permit",
                          font=self.body_description_font,
                          fg_color=self.error_red, text_color="white",
                          anchor="w", cursor="hand2",
                          command=_cmd("Reject Permit",
                                       lambda: self._admin_reject_permit(listing_id))
                          ).pack(fill="x", padx=10, pady=2)
        else:
            ctk.CTkButton(main, text="Revoke Verification",
                          font=self.body_description_font,
                          fg_color=self.hover_color, text_color="white",
                          anchor="w", cursor="hand2",
                          command=_cmd("Revoke",
                                       lambda: self._admin_revoke_permit(listing_id))
                          ).pack(fill="x", padx=10, pady=2)

        ctk.CTkButton(main, text="View Detail",
                      font=self.body_description_font,
                      fg_color=self.primary_color, text_color="white",
                      anchor="w", cursor="hand2",
                      command=_cmd("Detail",
                                   lambda: self._admin_show_listing_detail(listing_id))
                      ).pack(fill="x", padx=10, pady=2)

    # ════════════════════════════════════
    #  SECTION 4: BOOKINGS
    # ════════════════════════════════════

    def _build_admin_bookings_content(self):
        self._admin_bookings_scroll = ctk.CTkScrollableFrame(
            self._admin_content_wrapper, fg_color="transparent")
        self._admin_bookings_scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(self._admin_bookings_scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        self._admin_bookings_state = {"view": "list"}
        self._admin_booking_refs = {}

        ctk.CTkLabel(main, text="All Bookings", font=self.body_bold_font,
                      text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        stats_cards = [
            ("Total Bookings", "total_bookings", self.primary_color),
            ("Pending", "pending_count", self.hover_color),
            ("Active", "active_count", self.primary_color),
            ("Cancelled", "cancelled_count", self.error_red),
        ]
        self._admin_bookings_stat_labels = self._admin_build_stat_cards(main, stats_cards)

        filter_frame = ctk.CTkFrame(main, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))

        self._admin_bookings_filter_status = ctk.CTkComboBox(
            filter_frame, values=["All", "pending", "active", "cancelled"],
            font=self.body_light_font, fg_color=self.fg_color,
            border_color=self.entry_border, border_width=1,
            button_color=self.primary_color, button_hover_color=self.hover_color,
            dropdown_fg_color=self.fg_color, dropdown_text_color=self.text_color,
            dropdown_hover_color=self.hover_color, dropdown_font=self.body_light_font,
            text_color=self.text_color,
            width=140, height=35, state="readonly")
        self._admin_bookings_filter_status.pack(side="left", padx=(0, 10))
        self._admin_bookings_filter_status.set("All")

        self._admin_bookings_search_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="Search by tenant or property...",
            font=self.body_light_font, fg_color=self.fg_color,
            border_color=self.entry_border, border_width=1,
            text_color=self.text_color, width=280, height=35)
        self._admin_bookings_search_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(filter_frame, text="Search", font=self.body_light_font,
                      fg_color=self.primary_color, hover_color=self.hover_color,
                      text_color="white", width=90, height=35,
                      command=self._admin_refresh_bookings).pack(side="left")

        self._admin_bookings_table = ctk.CTkFrame(main, fg_color="transparent")
        self._admin_bookings_table.pack(fill="both", expand=True)

        self._admin_refresh_bookings()

    def _admin_refresh_bookings(self):
        for w in self._admin_bookings_table.winfo_children():
            w.destroy()

        self._admin_show_loading(self._admin_bookings_table)

        def _do():
            status_filter = self._admin_bookings_filter_status.get()
            search_text = self._admin_bookings_search_entry.get().strip()
            params = f"?status={status_filter}&limit=200"
            if search_text:
                params += f"&search={search_text}"
            stats_data = {}
            bookings_data = []
            try:
                resp_stats = self.api.get("/bookings/stats", timeout=5)
                if resp_stats.status_code == 200:
                    stats_data = resp_stats.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load booking stats. Check your connection.", is_error=True))
            try:
                resp = self.api.get(f"/bookings/all{params}", timeout=5)
                if resp.status_code == 200:
                    bookings_data = resp.json().get("bookings", [])
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load bookings. Check your connection.", is_error=True))
            self.after(0, lambda: self._admin_populate_bookings(stats_data, bookings_data))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_bookings(self, stats, bookings):
        self._admin_hide_loading()
        try:
            for w in self._admin_bookings_table.winfo_children():
                w.destroy()
        except Exception:
            return

        if "total_bookings" in self._admin_bookings_stat_labels:
            self._admin_bookings_stat_labels["total_bookings"].configure(
                text=str(stats.get("total_bookings", "0")))
        if "pending_count" in self._admin_bookings_stat_labels:
            self._admin_bookings_stat_labels["pending_count"].configure(
                text=str(stats.get("pending_count", "0")))
        if "active_count" in self._admin_bookings_stat_labels:
            self._admin_bookings_stat_labels["active_count"].configure(
                text=str(stats.get("active_count", "0")))
        if "cancelled_count" in self._admin_bookings_stat_labels:
            self._admin_bookings_stat_labels["cancelled_count"].configure(
                text=str(stats.get("cancelled_count", "0")))

        if not bookings:
            ctk.CTkLabel(self._admin_bookings_table, text="No bookings found.",
                          font=self.body_paragraph_font, text_color=self.text_color).pack(pady=30)
            return

        card = ctk.CTkFrame(self._admin_bookings_table, fg_color=self.secondary_color, corner_radius=6)
        card.pack(fill="both", expand=True)

        sticky_h = ["w", "w", "w", "w", "w", "w", "w", "ew", "ew"]
        card.grid_columnconfigure(0, weight=0, minsize=50)
        card.grid_columnconfigure(1, weight=1, minsize=130)
        card.grid_columnconfigure(2, weight=1, minsize=130)
        card.grid_columnconfigure(3, weight=0, minsize=50)
        card.grid_columnconfigure(4, weight=0, minsize=90)
        card.grid_columnconfigure(5, weight=0, minsize=90)
        card.grid_columnconfigure(6, weight=0, minsize=80)
        card.grid_columnconfigure(7, weight=0, minsize=80)
        card.grid_columnconfigure(8, weight=0, minsize=240)

        headers = ["ID", "Tenant", "Property", "Room", "Check-in", "Check-out", "Status", "Total", "Actions"]
        for j, header in enumerate(headers):
            ctk.CTkLabel(card, text=header, font=self.body_bold_font,
                          text_color=self.text_color).grid(
                row=0, column=j, padx=12, pady=(15, 10), sticky=sticky_h[j])

        for r, b in enumerate(bookings):
            data_row = 1 + r * 2
            sep_row = data_row + 1
            is_last = r == len(bookings) - 1

            ctk.CTkLabel(card, text=str(b.get("booking_id", "")), font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=0, padx=12, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=b.get("tenant_name", f"User #{b.get('user_id')}"),
                          font=self.body_paragraph_font, text_color=self.text_color).grid(
                row=data_row, column=1, padx=10, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=b.get("property_name", "N/A"), font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=2, padx=10, pady=(7, 7), sticky="w")

            room_no = b.get("room_number", "?")
            ctk.CTkLabel(card, text=f"#{room_no}" if room_no else "?", font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=3, padx=10, pady=(7, 7), sticky="w")

            ci = str(b.get("check_in", "") or "")[:10]
            co = str(b.get("check_out", "") or "")[:10]
            ctk.CTkLabel(card, text=ci, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=4, padx=10, pady=(7, 7), sticky="w")
            ctk.CTkLabel(card, text=co, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=5, padx=10, pady=(7, 7), sticky="w")

            status = b.get("status", "unknown")
            s_color = self._admin_status_colors.get(status, self.text_color)
            ctk.CTkLabel(card, text=status.capitalize(), font=self.body_description_font,
                          fg_color=s_color, text_color="white",
                          corner_radius=4, padx=8, pady=2).grid(
                row=data_row, column=6, padx=15, pady=(7, 7), sticky="ew")

            ctk.CTkLabel(card, text=f"\u20B1{b.get('total_price', '0')}", font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=7, padx=10, pady=(7, 7), sticky="w")

            actions_f = ctk.CTkFrame(card, fg_color="transparent")
            actions_f.grid(row=data_row, column=8, padx=12, pady=(7, 7))
            bid = b.get("booking_id")
            col = 0
            ctk.CTkButton(actions_f, text="View", font=self.body_description_font,
                          fg_color=self.primary_color, hover_color=self.hover_color,
                          text_color="white", width=50, height=28, cursor="hand2",
                          command=lambda bid=bid: self._admin_show_booking_detail(bid)
                          ).grid(row=0, column=col, padx=(0, 4)); col += 1
            if status == "pending":
                ctk.CTkButton(actions_f, text="Approve", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              width=60, height=28, cursor="hand2",
                              command=lambda bid=bid: self._admin_booking_change_status(
                                  bid, "active")).grid(row=0, column=col, padx=(0, 4)); col += 1
                ctk.CTkButton(actions_f, text="Cancel", font=self.body_description_font,
                              fg_color=self.error_red, text_color="white",
                              width=55, height=28, cursor="hand2",
                              command=lambda bid=bid: self._admin_booking_change_status(
                                  bid, "cancelled")).grid(row=0, column=col, padx=(0, 4)); col += 1

            if not is_last:
                ttk.Separator(card, orient="horizontal").grid(
                    row=sep_row, column=0, columnspan=9, padx=20, pady=4, sticky="ew")

    # ── Booking Detail View ──

    def _admin_show_booking_detail(self, booking_id):
        self._admin_bookings_state["view"] = "detail"
        self._admin_bookings_state["detail_id"] = booking_id
        self._admin_clear_content()

        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        back_btn = ctk.CTkLabel(header, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: (
            self._admin_clear_content(), self._build_admin_bookings_content()))
        back_btn.bind("<Enter>", lambda e: back_btn.configure(image=self.bk_btn_hvr_icon))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(image=self.bk_btn_icon))
        ctk.CTkLabel(header, text=f"Booking #{booking_id}", font=self.alt_title_font,
                      text_color=self.text_color).pack(side="left", padx=10)

        loading = ctk.CTkLabel(main, text="Loading booking details...",
                                font=self.body_paragraph_font, text_color=self.text_color)
        loading.pack(pady=30)

        def _do():
            data = None
            try:
                resp = self.api.get(f"/bookings/{booking_id}/details", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load booking details. Check your connection.", is_error=True))
            self.after(0, lambda: self._admin_populate_booking_detail(main, data))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_booking_detail(self, parent, data):
        for w in parent.winfo_children():
            w.destroy()

        if not data:
            ctk.CTkLabel(parent, text="Failed to load booking details.",
                          font=self.body_paragraph_font, text_color=self.error_red).pack(pady=30)
            return

        status = data.get("status", "unknown")
        color = self._admin_status_colors.get(status, self.text_color)

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        back_btn = ctk.CTkLabel(header, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: (
            self._admin_clear_content(), self._build_admin_bookings_content()))
        back_btn.bind("<Enter>", lambda e: back_btn.configure(image=self.bk_btn_hvr_icon))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(image=self.bk_btn_icon))
        ctk.CTkLabel(header, text=f"Booking #{data.get('booking_id')}", font=self.alt_title_font,
                      text_color=self.text_color).pack(side="left", padx=10)

        hero = ctk.CTkFrame(parent, fg_color=self.secondary_color, corner_radius=6)
        hero.pack(fill="x", pady=(0, 15))
        inner = ctk.CTkFrame(hero, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(inner, text=f"Booking #{data.get('booking_id')}",
                      font=self.body_bold_paragraph_font,
                      text_color=self.text_color).pack(side="left")
        ctk.CTkLabel(inner, text=status.capitalize(), font=self.body_paragraph_font,
                      fg_color=color, text_color="white",
                      corner_radius=4, padx=12, pady=4).pack(side="left", padx=(15, 0))
        created = str(data.get("created_at", "") or "")[:19]
        updated = str(data.get("updated_at", "") or "")[:19]
        ctk.CTkLabel(inner, text=f"Created: {created}", font=self.body_light_font,
                      text_color=self.text_color).pack(side="right", padx=(10, 0))
        ctk.CTkLabel(inner, text=f"Updated: {updated}", font=self.body_light_font,
                      text_color=self.text_color).pack(side="right", padx=10)

        two_col = ctk.CTkFrame(parent, fg_color="transparent")
        two_col.pack(fill="x", pady=(0, 15))
        two_col.grid_columnconfigure((0, 1), weight=1, uniform="detcol")

        tenant_card = ctk.CTkFrame(two_col, fg_color=self.secondary_color, corner_radius=6)
        tenant_card.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        ctk.CTkLabel(tenant_card, text="Tenant", font=self.body_bold_paragraph_font,
                      text_color=self.primary_color).pack(anchor="w", padx=15, pady=(12, 5))
        for label, key in [("Name", "tenant_name"), ("Email", "tenant_email"),
                           ("Phone", "tenant_phone")]:
            val = data.get(key, "N/A") or "N/A"
            ctk.CTkLabel(tenant_card, text=f"{label}: {val}", font=self.body_light_font,
                          text_color=self.text_color).pack(anchor="w", padx=15, pady=2)

        prop_card = ctk.CTkFrame(two_col, fg_color=self.secondary_color, corner_radius=6)
        prop_card.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        ctk.CTkLabel(prop_card, text="Property", font=self.body_bold_paragraph_font,
                      text_color=self.primary_color).pack(anchor="w", padx=15, pady=(12, 5))
        for label, key in [("Name", "property_name"), ("Type", "property_type"),
                           ("Room #", "room_number"), ("Room Type", "room_type"),
                           ("Owner", "owner_name")]:
            val = data.get(key, "N/A") or "N/A"
            ctk.CTkLabel(prop_card, text=f"{label}: {val}", font=self.body_light_font,
                          text_color=self.text_color).pack(anchor="w", padx=15, pady=2)

        dates_card = ctk.CTkFrame(parent, fg_color=self.secondary_color, corner_radius=6)
        dates_card.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(dates_card, text="Booking Details", font=self.body_bold_paragraph_font,
                      text_color=self.primary_color).pack(anchor="w", padx=15, pady=(12, 5))
        dates_inner = ctk.CTkFrame(dates_card, fg_color="transparent")
        dates_inner.pack(fill="x", padx=15, pady=(0, 12))
        ci = str(data.get("check_in", "") or "")[:10]
        co = str(data.get("check_out", "") or "")[:10]
        ctk.CTkLabel(dates_inner,
                      text=f"Check-in: {ci}  |  Check-out: {co}  |  Total: \u20B1{data.get('total_price', '0')}",
                      font=self.body_paragraph_font, text_color=self.text_color).pack(anchor="w")
        if data.get("notes"):
            ctk.CTkLabel(dates_card, text=f"Notes: {data['notes']}", font=self.body_light_font,
                          text_color=self.text_color).pack(anchor="w", padx=15, pady=(0, 12))

        payment_card = ctk.CTkFrame(parent, fg_color=self.secondary_color, corner_radius=6)
        payment_card.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(payment_card, text="Payment", font=self.body_bold_paragraph_font,
                      text_color=self.primary_color).pack(anchor="w", padx=15, pady=(12, 5))
        payments = data.get("payments", [])
        if payments:
            p = payments[0]
            ctk.CTkLabel(payment_card,
                          text=f"Method: {p.get('method', 'N/A')}  |  Status: {p.get('status', 'N/A')}  |  Amount: \u20B1{p.get('amount', '0')}  |  Ref: {p.get('reference_no', 'N/A')}",
                          font=self.body_paragraph_font, text_color=self.text_color).pack(
                anchor="w", padx=15, pady=(0, 12))
        else:
            ctk.CTkLabel(payment_card, text="No payment records", font=self.body_light_font,
                          text_color=self.text_color).pack(anchor="w", padx=15, pady=(0, 12))

        history_card = ctk.CTkFrame(parent, fg_color=self.secondary_color, corner_radius=6)
        history_card.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(history_card, text="Status History", font=self.body_bold_paragraph_font,
                      text_color=self.primary_color).pack(anchor="w", padx=15, pady=(12, 5))
        history = data.get("history", [])
        if history:
            for h in history:
                ts = str(h.get("changed_at", "") or "")[:19]
                old = h.get("old_status") or "(new)"
                new = h.get("new_status", "?")
                ctk.CTkLabel(history_card, text=f"{ts}  {old} \u2192 {new}",
                              font=self.body_light_font,
                              text_color=self.text_color).pack(anchor="w", padx=15, pady=1)
        else:
            ctk.CTkLabel(history_card, text="No history records", font=self.body_light_font,
                          text_color=self.text_color).pack(anchor="w", padx=15, pady=(0, 12))

        if data.get("property_address"):
            addr_card = ctk.CTkFrame(parent, fg_color=self.secondary_color, corner_radius=6)
            addr_card.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(addr_card, text="Address", font=self.body_bold_paragraph_font,
                          text_color=self.primary_color).pack(anchor="w", padx=15, pady=(12, 5))
            ctk.CTkLabel(addr_card, text=data["property_address"], font=self.body_light_font,
                          text_color=self.text_color).pack(anchor="w", padx=15, pady=(0, 12))

        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 20))
        bid = data.get("booking_id")
        if status == "pending":
            ctk.CTkButton(action_frame, text="Approve Booking", font=self.body_big_font,
                          fg_color="green", hover_color="darkgreen",
                          text_color="white", height=40,
                          command=lambda: self._admin_detail_change_status(bid, "active")
                          ).pack(side="left", padx=(0, 10))
            ctk.CTkButton(action_frame, text="Cancel Booking", font=self.body_big_font,
                          fg_color=self.error_red, hover_color="#b52e2a",
                          text_color="white", height=40,
                          command=lambda: self._admin_detail_change_status(bid, "cancelled")
                          ).pack(side="left")
        elif status == "active":
            ctk.CTkButton(action_frame, text="Cancel Booking", font=self.body_big_font,
                          fg_color=self.error_red, hover_color="#b52e2a",
                          text_color="white", height=40,
                          command=lambda: self._admin_detail_change_status(bid, "cancelled")
                          ).pack(side="left")
        elif status == "cancelled":
            ctk.CTkButton(action_frame, text="Re-activate Booking", font=self.body_big_font,
                          fg_color=self.primary_color, hover_color=self.hover_color,
                          text_color="white", height=40,
                          command=lambda: self._admin_detail_change_status(bid, "pending")
                          ).pack(side="left")

    def _admin_booking_change_status(self, booking_id, new_status):
        result = self._admin_confirm_action(
            f"Type CONFIRM to {new_status} booking #{booking_id}:", "Confirm")
        if result != "CONFIRM":
            return

        def _do():
            try:
                resp = self.api.patch(
                    f"/bookings/{booking_id}/status",
                    json={"status": new_status, "changed_by_user_id": self.current_user.get("user_id", 0)},
                    timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self.show_toast(
                        f"Booking #{booking_id} {new_status}", is_error=False))
                else:
                    detail = resp.json().get("detail", "Failed")
                    self.after(0, lambda: self.show_toast(detail, is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, self._admin_refresh_bookings)

        threading.Thread(target=_do, daemon=True).start()

    def _admin_detail_change_status(self, booking_id, new_status):
        result = self._admin_confirm_action(
            f"Type CONFIRM to {new_status} booking #{booking_id}:", "Confirm")
        if result != "CONFIRM":
            return

        def _do():
            try:
                resp = self.api.patch(
                    f"/bookings/{booking_id}/status",
                    json={"status": new_status, "changed_by_user_id": self.current_user.get("user_id", 0)},
                    timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self.show_toast(
                        f"Booking #{booking_id} {new_status}", is_error=False))
                else:
                    detail = resp.json().get("detail", "Failed")
                    self.after(0, lambda: self.show_toast(detail, is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, lambda: self._admin_show_booking_detail(booking_id))

        threading.Thread(target=_do, daemon=True).start()

    # ════════════════════════════════════
    #  SECTION 5: REVIEWS
    # ════════════════════════════════════

    def _build_admin_reviews_content(self):
        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main, text="Reviews & Feedback", font=self.body_bold_font,
                      text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        card = ctk.CTkFrame(main, fg_color=self.secondary_color, corner_radius=6)
        card.pack(fill="both", expand=True, pady=(10, 0))
        self._admin_reviews_container = card

        self._admin_show_loading(card)

        def _do():
            reviews = []
            try:
                resp = self.api.get("/social/reviews/all", timeout=5)
                if resp.status_code == 200:
                    reviews = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load reviews. Check your connection.", is_error=True))
            self.after(0, lambda: self._admin_populate_reviews(reviews))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_reviews(self, reviews):
        self._admin_hide_loading()
        card = self._admin_reviews_container
        for w in card.winfo_children():
            w.destroy()

        if not reviews:
            ctk.CTkLabel(card, text="No reviews found.",
                          font=self.body_paragraph_font,
                          text_color=self.text_color).grid(row=1, column=0, columnspan=7, padx=15, pady=20)
            return

        sticky_h = ["w", "w", "w", "w", "w", "w", "ew"]
        card.grid_columnconfigure(0, weight=0, minsize=50)
        card.grid_columnconfigure(1, weight=0, minsize=70)
        card.grid_columnconfigure(2, weight=0, minsize=70)
        card.grid_columnconfigure(3, weight=0, minsize=100)
        card.grid_columnconfigure(4, weight=2, minsize=200)
        card.grid_columnconfigure(5, weight=0, minsize=90)
        card.grid_columnconfigure(6, weight=0, minsize=100)

        headers = ["ID", "Listing ID", "User ID", "Rating", "Comment", "Date", "Actions"]
        for j, header in enumerate(headers):
            ctk.CTkLabel(card, text=header, font=self.body_bold_font,
                          text_color=self.text_color).grid(
                row=0, column=j, padx=12, pady=(15, 10), sticky=sticky_h[j])

        for r, review in enumerate(reviews):
            data_row = 1 + r * 2
            sep_row = data_row + 1
            is_last = r == len(reviews) - 1

            ctk.CTkLabel(card, text=str(review.get("review_id", "")), font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=0, padx=12, pady=(7, 7), sticky="w")
            ctk.CTkLabel(card, text=str(review.get("listing_id", "")), font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=1, padx=10, pady=(7, 7), sticky="w")
            ctk.CTkLabel(card, text=str(review.get("user_id", "")), font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=2, padx=10, pady=(7, 7), sticky="w")

            rating = review.get("rating", 0)
            stars = "\u2605" * rating + "\u2606" * (5 - rating)
            ctk.CTkLabel(card, text=stars, font=self.body_paragraph_font,
                          text_color=self.primary_color).grid(
                row=data_row, column=3, padx=10, pady=(7, 7), sticky="w")

            comment = review.get("comment", "") or ""
            if len(comment) > 60:
                comment = comment[:60] + "..."
            ctk.CTkLabel(card, text=comment, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=4, padx=10, pady=(7, 7), sticky="w")

            created = str(review.get("created_at", "") or "")[:10]
            ctk.CTkLabel(card, text=created, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=5, padx=10, pady=(7, 7), sticky="w")

            rid = review.get("review_id")
            actions_f = ctk.CTkFrame(card, fg_color="transparent")
            actions_f.grid(row=data_row, column=6, padx=12, pady=(7, 7))
            ctk.CTkButton(actions_f, text="Delete", font=self.body_description_font,
                          fg_color=self.error_red, text_color="white",
                          width=60, height=28, cursor="hand2",
                          command=lambda rid=rid: self._admin_delete_review(rid)
                          ).pack(side="left", padx=2)

            if not is_last:
                ttk.Separator(card, orient="horizontal").grid(
                    row=sep_row, column=0, columnspan=7, padx=20, pady=4, sticky="ew")

    def _admin_delete_review(self, review_id):
        result = self._admin_confirm_action(
            f"Type DELETE to remove review #{review_id}:", "Delete Review")
        if result != "DELETE":
            return

        def _do():
            try:
                resp = self.api.delete(f"/social/reviews/{review_id}", timeout=10)
                if resp.status_code == 204:
                    self.after(0, lambda: self.show_toast("Review deleted", is_error=False))
                else:
                    self.after(0, lambda: self.show_toast("Failed to delete review", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, self._build_admin_reviews_content)

        threading.Thread(target=_do, daemon=True).start()

    # ════════════════════════════════════
    #  SECTION 6: REPORTS
    # ════════════════════════════════════

    def _build_admin_reports_content(self):
        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main, text="Report Queue", font=self.body_bold_font,
                      text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        filter_frame = ctk.CTkFrame(main, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))

        self._admin_reports_filter = ctk.CTkComboBox(
            filter_frame, values=["All", "pending", "reviewed", "resolved", "dismissed"],
            font=self.body_light_font, fg_color=self.fg_color,
            border_color=self.entry_border, border_width=1,
            button_color=self.primary_color, button_hover_color=self.hover_color,
            dropdown_fg_color=self.fg_color, dropdown_text_color=self.text_color,
            dropdown_hover_color=self.hover_color, dropdown_font=self.body_light_font,
            text_color=self.text_color,
            width=160, height=35, state="readonly",
            command=lambda c: self._admin_refresh_reports())
        self._admin_reports_filter.pack(side="left")
        self._admin_reports_filter.set("All")

        card = ctk.CTkFrame(main, fg_color=self.secondary_color, corner_radius=6)
        card.pack(fill="both", expand=True, pady=(10, 0))
        self._admin_reports_container = card

        self._admin_refresh_reports()

    def _admin_refresh_reports(self):
        card = self._admin_reports_container
        for w in card.winfo_children():
            w.destroy()

        self._admin_show_loading(card)

        def _do():
            reports = []
            try:
                resp = self.api.get("/reports/", timeout=5)
                if resp.status_code == 200:
                    reports = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load reports. Check your connection.", is_error=True))
            status_filter = "All"
            try:
                status_filter = self._admin_reports_filter.get()
            except Exception:
                pass
            if status_filter != "All":
                reports = [r for r in reports if r.get("status") == status_filter]
            self.after(0, lambda: self._admin_populate_reports(reports))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_reports(self, reports):
        self._admin_hide_loading()
        card = self._admin_reports_container
        for w in card.winfo_children():
            w.destroy()

        if not reports:
            ctk.CTkLabel(card, text="No reports found.",
                          font=self.body_paragraph_font,
                          text_color=self.text_color).grid(row=1, column=0, columnspan=7, padx=15, pady=20)
            return

        sticky_h = ["w", "w", "ew", "w", "w", "w", "ew"]
        card.grid_columnconfigure(0, weight=0, minsize=50)
        card.grid_columnconfigure(1, weight=0, minsize=100)
        card.grid_columnconfigure(2, weight=2, minsize=200)
        card.grid_columnconfigure(3, weight=0, minsize=100)
        card.grid_columnconfigure(4, weight=0, minsize=140)
        card.grid_columnconfigure(5, weight=0, minsize=160)
        card.grid_columnconfigure(6, weight=0, minsize=200)

        headers = ["ID", "Target", "Reason", "Status", "Date", "Reported By", "Actions"]
        for j, header in enumerate(headers):
            ctk.CTkLabel(card, text=header, font=self.body_bold_font,
                          text_color=self.text_color).grid(
                row=0, column=j, padx=12, pady=(15, 10), sticky=sticky_h[j])

        for r, report in enumerate(reports):
            data_row = 1 + r * 2
            sep_row = data_row + 1
            is_last = r == len(reports) - 1

            rid = report.get("report_id")
            status = report.get("status", "pending")
            s_color = self._admin_status_colors.get(status, self.text_color)
            reason = report.get("reason", "") or ""
            if len(reason) > 100:
                reason = reason[:100] + "..."

            ctk.CTkLabel(card, text=f"#{rid}", font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=0, padx=12, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=f"{report.get('target_type', '?')} #{report.get('target_id', '?')}",
                          font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=1, padx=10, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=reason, font=self.body_paragraph_font,
                          text_color=self.text_color, wraplength=250,
                          justify="left").grid(
                row=data_row, column=2, padx=10, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=status.capitalize(), font=self.body_description_font,
                          fg_color=s_color, text_color="white",
                          corner_radius=4, padx=8, pady=2).grid(
                row=data_row, column=3, padx=15, pady=(7, 7), sticky="ew")

            created = str(report.get("created_at", "") or "")[:16]
            ctk.CTkLabel(card, text=created, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=4, padx=10, pady=(7, 7), sticky="w")

            ctk.CTkLabel(card, text=report.get("reported_by_name", f"User #{report.get('reported_by')}"),
                          font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=5, padx=10, pady=(7, 7), sticky="w")

            actions_f = ctk.CTkFrame(card, fg_color="transparent")
            actions_f.grid(row=data_row, column=6, padx=12, pady=(7, 7))
            col = 0
            if status in ("pending", "reviewed"):
                ctk.CTkButton(actions_f, text="Resolve", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              width=70, height=28, cursor="hand2",
                              command=lambda rid=rid: self._admin_resolve_report(rid)
                              ).grid(row=0, column=col, padx=(0, 4)); col += 1
                ctk.CTkButton(actions_f, text="Dismiss", font=self.body_description_font,
                              fg_color=self.text_color, text_color="white",
                              width=70, height=28, cursor="hand2",
                              command=lambda rid=rid: self._admin_dismiss_report(rid)
                              ).grid(row=0, column=col, padx=(0, 4)); col += 1

            if not is_last:
                ttk.Separator(card, orient="horizontal").grid(
                    row=sep_row, column=0, columnspan=7, padx=20, pady=4, sticky="ew")

    def _admin_resolve_report(self, report_id):
        result = self._admin_confirm_action(
            f"Type RESOLVE to resolve report #{report_id}:", "Resolve Report")
        if result != "RESOLVE":
            return
        admin_id = self.current_user.get("user_id", 0)

        def _do():
            try:
                resp = self.api.patch(f"/reports/{report_id}",
                                      json={"status": "resolved", "resolved_by": admin_id}, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self.show_toast(f"Report {report_id} resolved", is_error=False))
                else:
                    self.after(0, lambda: self.show_toast("Failed to resolve report", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, self._admin_refresh_reports)

        threading.Thread(target=_do, daemon=True).start()

    def _admin_dismiss_report(self, report_id):
        result = self._admin_confirm_action(
            f"Type DISMISS to dismiss report #{report_id}:", "Dismiss Report")
        if result != "DISMISS":
            return
        admin_id = self.current_user.get("user_id", 0)

        def _do():
            try:
                resp = self.api.patch(f"/reports/{report_id}",
                                      json={"status": "dismissed", "resolved_by": admin_id}, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self.show_toast(f"Report {report_id} dismissed", is_error=False))
                else:
                    self.after(0, lambda: self.show_toast("Failed to dismiss report", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, self._admin_refresh_reports)

        threading.Thread(target=_do, daemon=True).start()

    # ════════════════════════════════════
    #  PERMIT ACTION METHODS (used by combined listings)
    # ════════════════════════════════════

    def _admin_approve_permit(self, listing_id):
        result = self._admin_confirm_action(
            f"Type APPROVE to verify permit for listing #{listing_id}:", "Approve Permit")
        if result != "APPROVE":
            return

        def _do():
            try:
                resp = self.api.patch(f"/boarding-houses/{listing_id}",
                                      json={"is_verified": True}, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self.show_toast(
                        f"Permit approved for listing #{listing_id}", is_error=False))
                else:
                    self.after(0, lambda: self.show_toast("Failed to approve permit", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, self._admin_refresh_listings)

        threading.Thread(target=_do, daemon=True).start()

    def _admin_reject_permit(self, listing_id):
        result = self._admin_confirm_action(
            f"Type REJECT to reject permit for listing #{listing_id}:", "Reject Permit")
        if result != "REJECT":
            return

        def _do():
            try:
                resp = self.api.patch(f"/boarding-houses/{listing_id}",
                                      json={"is_verified": False}, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self.show_toast(
                        f"Permit rejected for listing #{listing_id}", is_error=False))
                else:
                    self.after(0, lambda: self.show_toast("Failed to reject permit", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, self._admin_refresh_listings)

        threading.Thread(target=_do, daemon=True).start()

    def _admin_revoke_permit(self, listing_id):
        result = self._admin_confirm_action(
            f"Type REVOKE to revoke verification for listing #{listing_id}:", "Revoke Permit")
        if result != "REVOKE":
            return

        def _do():
            try:
                resp = self.api.patch(f"/boarding-houses/{listing_id}",
                                      json={"is_verified": False}, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self.show_toast(
                        f"Verification revoked for listing #{listing_id}", is_error=False))
                else:
                    self.after(0, lambda: self.show_toast("Failed to revoke", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            self.after(0, self._admin_refresh_listings)

        threading.Thread(target=_do, daemon=True).start()

    # ════════════════════════════════════
    #  SECTION 8: ADMIN LOGS
    # ════════════════════════════════════

    def _build_admin_logs_content(self):
        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main, text="Admin Logs", font=self.body_bold_font,
                      text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        card = ctk.CTkFrame(main, fg_color=self.secondary_color, corner_radius=6)
        card.pack(fill="both", expand=True, pady=(10, 0))
        self._admin_logs_container = card

        self._admin_show_loading(card)

        def _do():
            logs = []
            try:
                resp = self.api.get("/admin-logs/", timeout=5)
                if resp.status_code == 200:
                    logs = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load admin logs. Check your connection.", is_error=True))
            self.after(0, lambda: self._admin_populate_logs(logs))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_logs(self, logs):
        self._admin_hide_loading()
        card = self._admin_logs_container
        for w in card.winfo_children():
            w.destroy()

        if not logs:
            ctk.CTkLabel(card, text="No admin logs found.",
                          font=self.body_paragraph_font,
                          text_color=self.text_color).grid(row=1, column=0, columnspan=5, padx=15, pady=20)
            return

        sticky_h = ["w", "w", "w", "w", "w"]
        card.grid_columnconfigure(0, weight=0, minsize=140)
        card.grid_columnconfigure(1, weight=1, minsize=150)
        card.grid_columnconfigure(2, weight=0, minsize=100)
        card.grid_columnconfigure(3, weight=0, minsize=60)
        card.grid_columnconfigure(4, weight=1, minsize=150)

        headers = ["Timestamp", "Action", "Target Type", "Target ID", "Details"]
        for j, header in enumerate(headers):
            ctk.CTkLabel(card, text=header, font=self.body_bold_font,
                          text_color=self.text_color).grid(
                row=0, column=j, padx=12, pady=(15, 10), sticky=sticky_h[j])

        for r, log in enumerate(logs):
            data_row = 1 + r * 2
            sep_row = data_row + 1
            is_last = r == len(logs) - 1

            ts = str(log.get("performed_at", "") or "")[:19]
            action = log.get("action", "?")
            target_type = log.get("target_type", "?")
            target_id = log.get("target_id", "?")
            details = log.get("details", log.get("admin_name", "")) or ""

            ctk.CTkLabel(card, text=ts, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=0, padx=12, pady=(7, 7), sticky="w")
            ctk.CTkLabel(card, text=action, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=1, padx=10, pady=(7, 7), sticky="w")
            ctk.CTkLabel(card, text=target_type, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=2, padx=10, pady=(7, 7), sticky="w")
            ctk.CTkLabel(card, text=f"#{target_id}", font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=3, padx=10, pady=(7, 7), sticky="w")
            ctk.CTkLabel(card, text=details, font=self.body_paragraph_font,
                          text_color=self.text_color).grid(
                row=data_row, column=4, padx=10, pady=(7, 7), sticky="w")

            if not is_last:
                ttk.Separator(card, orient="horizontal").grid(
                    row=sep_row, column=0, columnspan=5, padx=20, pady=4, sticky="ew")

    # ════════════════════════════════════
    #  SECTION 9: ADMIN ACCOUNT MANAGEMENT
    # ════════════════════════════════════

    def _build_admin_management_content(self):
        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main, text="Admin Account Management", font=self.body_bold_font,
                      text_color=self.text_color).pack(anchor="w", pady=(0, 15))

        form = ctk.CTkFrame(main, fg_color=self.secondary_color, corner_radius=6)
        form.pack(fill="x", pady=(0, 20))

        self._admin_create_widgets = {}
        fields = [
            ("Full Name", "name", False),
            ("Email Address", "email", False),
            ("Password", "password", True),
        ]

        for label, key, is_password in fields:
            row = ctk.CTkFrame(form, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=8)

            ctk.CTkLabel(row, text=label, font=self.body_light_font,
                          text_color=self.text_color).pack(anchor="w", pady=(0, 3))

            entry_frame = ctk.CTkFrame(row, height=38, fg_color=self.fg_color,
                                        border_color=self.entry_border, border_width=1, corner_radius=6)
            entry_frame.pack(fill="x")
            entry_frame.pack_propagate(False)

            show_char = "\u2022" if is_password else ""
            entry = ctk.CTkEntry(entry_frame, placeholder_text=f"Enter {label.lower()}",
                                  height=26, font=self.body_light_font,
                                  fg_color="transparent", border_width=0,
                                  text_color=self.text_color, show=show_char)
            entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
            self._admin_create_widgets[key] = entry

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(anchor="center", padx=15, pady=15)
        self._admin_create_btn = ctk.CTkButton(
            btn_frame, text="CREATE ADMIN ACCOUNT", font=self.body_big_font,
            fg_color=self.primary_color, hover_color=self.hover_color,
            text_color="white", height=40, command=self._admin_create_account)
        self._admin_create_btn.pack(fill="x")

        self._admin_create_error = ctk.CTkLabel(form, text="", font=self.inline_error_font,
                                                  text_color=self.error_red)
        self._admin_create_error.pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkLabel(main, text="Existing Admins", font=self.body_bold_font,
                      text_color=self.text_color).pack(anchor="w", pady=(15, 10))

        self._admin_list_frame = ctk.CTkScrollableFrame(main, fg_color="transparent", height=200)
        self._admin_list_frame.pack(fill="x")

        self._admin_refresh_admin_list()

    def _admin_create_account(self):
        name = self._admin_create_widgets["name"].get().strip()
        email = self._admin_create_widgets["email"].get().strip()
        password = self._admin_create_widgets["password"].get()

        if not name or not email or not password:
            self._admin_create_error.configure(text="All fields are required")
            return
        if len(password) < 8:
            self._admin_create_error.configure(text="Password must be at least 8 characters")
            return
        if "@" not in email or "." not in email:
            self._admin_create_error.configure(text="Invalid email address")
            return

        self._admin_create_btn.configure(state="disabled", text="CREATING...")
        self._admin_create_error.configure(text="")

        def _do():
            try:
                resp = self.api.post("/auth/create-admin", json={
                    "name": name, "email": email, "password": password,
                }, timeout=10)
                if resp.status_code == 201:
                    self.after(0, self._admin_create_done)
                else:
                    detail = resp.json().get("detail", "Failed to create admin")
                    self.after(0, lambda: self._admin_create_error.configure(text=detail))
            except Exception:
                self.after(0, lambda: self._admin_create_error.configure(text="Cannot connect to server"))
            finally:
                self.after(0, lambda: self._admin_create_btn.configure(
                    state="normal", text="CREATE ADMIN ACCOUNT"))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_create_done(self):
        self.show_toast("Admin account created!", is_error=False)
        for widget in self._admin_create_widgets.values():
            widget.delete(0, "end")
        self._admin_refresh_admin_list()

    def _admin_refresh_admin_list(self):
        for w in self._admin_list_frame.winfo_children():
            w.destroy()

        self._admin_show_loading(self._admin_list_frame)

        def _do():
            admins = []
            try:
                resp = self.api.get("/users/", timeout=5)
                if resp.status_code == 200:
                    all_users = resp.json()
                    admins = [u for u in all_users if u.get("role") == "admin"]
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load admins. Check your connection.", is_error=True))
            self.after(0, lambda: self._admin_populate_admin_list(admins))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_admin_list(self, admins):
        self._admin_hide_loading()
        for w in self._admin_list_frame.winfo_children():
            w.destroy()

        if not admins:
            ctk.CTkLabel(self._admin_list_frame, text="No admin accounts found.",
                          font=self.body_light_font, text_color=self.text_color).pack(pady=10)
            return

        for admin in admins:
            card = ctk.CTkFrame(self._admin_list_frame, fg_color=self.secondary_color,
                                 corner_radius=4, border_width=1, border_color=self.entry_border)
            card.pack(fill="x", pady=2)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=10, pady=6)

            ctk.CTkLabel(inner, text=admin.get("name", ""), font=self.body_paragraph_font,
                          text_color=self.text_color).pack(side="left")
            ctk.CTkLabel(inner, text=admin.get("email", ""), font=self.body_light_font,
                          text_color=self.text_color).pack(side="left", padx=(10, 0))
            ctk.CTkLabel(inner, text=f"ID: {admin.get('user_id')}",
                          font=self.body_description_font,
                          text_color=self.text_color).pack(side="right")

    # ── Notifications ──

    def _admin_fetch_notif_count(self):
        user_id = getattr(self, "current_user", {}).get("user_id")
        if not user_id:
            return

        def _do():
            try:
                resp = self.api.get(f"/notifications/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    unread = sum(1 for n in data if not n.get("is_read", False))
                else:
                    unread = 0
            except Exception:
                unread = 0
            self.after(0, lambda: self._admin_update_notif_badge(unread))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_update_notif_badge(self, count):
        if count > 0:
            self._admin_notif_badge.configure(text=str(count) if count <= 99 else "99+")
        else:
            self._admin_notif_badge.configure(text="")
