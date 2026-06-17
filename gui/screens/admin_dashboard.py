import threading
import customtkinter as ctk
from datetime import datetime


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
        self._build_admin_sidebar()

        self._admin_content_wrapper = ctk.CTkFrame(
            self._admin_form_container, fg_color="transparent"
        )
        self._admin_content_wrapper.pack(
            fill="both", expand=True, padx=(260, 10), pady=20
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

        profile_frame = ctk.CTkFrame(nav, fg_color="transparent")
        profile_frame.pack(side="right", padx=25, pady=10)

        ctk.CTkLabel(profile_frame, text=None, image=self.pfp_placeholder,
                      width=25, height=25).pack(side="left", padx=(0, 12))

        text_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        text_frame.pack(side="left")

        user_name = getattr(self, "current_user", {}).get("name", "Admin")
        user_id = getattr(self, "current_user", {}).get("user_id", "?")

        ctk.CTkLabel(text_frame, text=user_name, font=self.body_light_font,
                      text_color=self.text_color).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(text_frame, text=f"UID: {user_id}", font=self.body_light_font,
                      text_color=self.text_color).grid(row=1, column=0, sticky="w")

        ctk.CTkLabel(text_frame, text="▾", font=self.body_light_font,
                      text_color=self.text_color).grid(row=0, column=1, padx=(4, 0), sticky="w")

        profile_frame.bind("<Button-1>", lambda e: self._admin_toggle_user_menu())
        profile_frame.configure(cursor="hand2")
        for child in profile_frame.winfo_children():
            child.bind("<Button-1>", lambda e: self._admin_toggle_user_menu())

        self._admin_nav_bar = nav
        self._admin_notif_frame = notif_frame

    # ── Sidebar ──

    def _build_admin_sidebar(self):
        sidebar = ctk.CTkFrame(
            self._admin_form_container,
            fg_color="transparent",
            width=250,
            corner_radius=0,
            border_color=self.entry_border,
            border_width=1,
        )
        sidebar.place(x=0, y=0, relheight=1.0)
        sidebar.pack_propagate(False)
        self._admin_sidebar = sidebar

        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(
            logo_frame, image=self.hamburg_menu_icon, text=None,
            fg_color="transparent", hover_color=self.hover_color,
            width=25, height=15, command=self._admin_animate_sidebar,
        ).pack(side="left", padx=15)

        ctk.CTkLabel(logo_frame, text=None, image=self.logo).pack(side="left")

        menu_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, pady=20)

        items = [
            ("dashboard", "Dashboard", self._build_admin_dashboard_content),
            ("users", "Manage User", self._build_admin_users_content),
            ("listings", "Manage Boarding Houses", self._build_admin_listings_content),
            ("bookings", "Bookings", self._build_admin_bookings_content),
            ("reviews", "Reviews & Feedback", self._build_admin_reviews_content),
            ("reports", "Reports", self._build_admin_reports_content),
            ("permits", "Permit Verifier", self._build_admin_permit_content),
            ("logs", "Admin Logs", self._build_admin_logs_content),
            ("admins", "Admin Account Creation", self._build_admin_management_content),
        ]

        self._admin_sidebar_btns = {}
        for i, (key, text, cmd) in enumerate(items):
            btn = ctk.CTkButton(
                menu_frame, text=text, width=230, height=40,
                hover_color=self.hover_color, fg_color="transparent",
                text_color=self.text_color, font=self.body_big_font,
                command=lambda k=key, cb=cmd: (
                    self._set_active_admin_sidebar_btn(k),
                    self._admin_clear_content(),
                    cb(),
                ),
                anchor="w",
            )
            btn.grid(row=i, column=0, padx=10, pady=(0, 10), sticky="ew")
            self._admin_sidebar_btns[key] = btn

        logout_btn = ctk.CTkButton(
            menu_frame, text="Logout", width=230, height=40,
            hover_color=self.hover_color, fg_color="transparent",
            text_color=self.text_color, font=self.body_big_font,
            command=self._handle_logout, anchor="w",
        )
        logout_btn.grid(row=len(items), column=0, padx=10, pady=(30, 0), sticky="ew")

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
        current_width = self._admin_sidebar.cget("width")

        if self._admin_is_sidebar_expanded:
            if current_width > 0:
                new_width = max(0, current_width - 20)
                self._admin_sidebar.configure(width=new_width)
                self._admin_content_wrapper.pack_configure(padx=(new_width + 10, 10))
                self.after(10, self._admin_animate_sidebar)
            else:
                self._admin_sidebar.place_forget()
                self._admin_is_sidebar_expanded = False
        else:
            if not self._admin_sidebar.winfo_ismapped():
                self._admin_sidebar.place(x=0, y=0, relheight=1.0)
            if current_width < 250:
                new_width = min(250, current_width + 20)
                self._admin_sidebar.configure(width=new_width)
                self._admin_content_wrapper.pack_configure(padx=(new_width + 10, 10))
                self.after(10, self._admin_animate_sidebar)
            else:
                self._admin_is_sidebar_expanded = True

    # ── User Menu ──

    def _admin_toggle_user_menu(self):
        if hasattr(self, "_admin_user_menu") and self._admin_user_menu and self._admin_user_menu.winfo_ismapped():
            self._admin_hide_user_menu()
        else:
            self._admin_show_user_menu()

    def _admin_show_user_menu(self):
        self._admin_hide_user_menu()
        menu = ctk.CTkFrame(
            self._admin_form_container, fg_color=self.secondary_color,
            corner_radius=6, border_width=1, border_color=self.entry_border, width=200,
        )
        self._admin_user_menu = menu

        px = self._admin_nav_bar.winfo_rootx() - self._admin_form_container.winfo_rootx()
        py = self._admin_nav_bar.winfo_rooty() - self._admin_form_container.winfo_rooty()
        ph = self._admin_nav_bar.winfo_height()
        menu.place(x=px + self._admin_nav_bar.winfo_width() - 200, y=py + ph + 5)
        menu.lift()

        items = [
            ("View Profile", self.menu_profile_icon, lambda: self._admin_menu_action(self.show_profile)),
            ("Change Password", self.menu_lock_icon, lambda: self._admin_menu_action(self.show_change_password)),
            ("Notifications", self.notification_icon, lambda: self._admin_menu_action(self.show_notifications_page)),
            None,
            ("Logout", self.menu_logout_icon, lambda: self._admin_menu_action(self._handle_logout)),
        ]
        for item in items:
            if item is None:
                ctk.CTkFrame(menu, height=1, fg_color=self.entry_border).pack(fill="x", padx=10, pady=5)
                continue
            text, icon, cmd = item
            ctk.CTkButton(
                menu, text=text, image=icon, font=self.body_paragraph_font,
                fg_color="transparent", text_color=self.text_color,
                hover_color=self.hover_color, anchor="w", height=36, command=cmd,
            ).pack(fill="x", padx=5, pady=2)

        self.bind_all("<Button-1>", self._admin_dismiss_user_menu, add="+")

    def _admin_hide_user_menu(self):
        if hasattr(self, "_admin_user_menu") and self._admin_user_menu:
            try:
                self._admin_user_menu.destroy()
            except Exception:
                pass
            self._admin_user_menu = None
        try:
            self.unbind_all("<Button-1>")
        except Exception:
            pass

    def _admin_dismiss_user_menu(self, event):
        if not hasattr(self, "_admin_user_menu") or not self._admin_user_menu:
            return
        x, y = event.x_root, event.y_root
        widget = self.winfo_containing(x, y)
        if widget and (self._admin_user_menu == widget or self._admin_user_menu in self._admin_get_all_children(widget)):
            return
        self._admin_hide_user_menu()

    def _admin_get_all_children(self, widget):
        children = []
        try:
            for child in widget.winfo_children():
                children.append(child)
                children.extend(self._admin_get_all_children(child))
        except Exception:
            pass
        return children

    def _admin_menu_action(self, callback):
        self._admin_hide_user_menu()
        callback()

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
                dropdown_fg_color=self.fg_color, text_color=self.text_color,
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
                                height=80, border_width=1, border_color=self.entry_border)
        welcome.pack(fill="x", pady=(0, 15))
        welcome.pack_propagate(False)
        inner = ctk.CTkFrame(welcome, fg_color="transparent")
        inner.pack(fill="both", padx=20, pady=15)
        accent = ctk.CTkFrame(inner, width=4, fg_color=self.primary_color, corner_radius=2)
        accent.pack(side="left", fill="y", padx=(0, 12))
        ctk.CTkLabel(inner, text=f"Welcome back, {user_name}!",
                      font=self.body_bold_paragraph_font,
                      text_color=self.text_color).pack(anchor="w")
        today_str = datetime.now().strftime("%A, %B %d, %Y")
        ctk.CTkLabel(inner, text=today_str, font=self.body_light_font,
                      text_color=self.text_color).pack(anchor="w")

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
            try:
                resp = self.api.get("/users/", timeout=5)
                if resp.status_code == 200:
                    users = resp.json()
                    data["total_users"] = str(len(users))
                    data["pending_permits"] = str(sum(
                        1 for u in users if u.get("status") == "active"))
            except Exception:
                pass
            try:
                resp = self.api.get("/boarding-houses/feed/dashboard?limit=500", timeout=5)
                if resp.status_code == 200:
                    listings = resp.json()
                    data["total_listings"] = str(len(listings))
                    data["pending_permits"] = str(sum(
                        1 for l in listings if not l.get("is_verified")))
            except Exception:
                pass
            try:
                resp = self.api.get("/bookings/stats", timeout=5)
                if resp.status_code == 200:
                    stats = resp.json()
                    data["active_bookings"] = str(stats.get("active_count", "0"))
            except Exception:
                pass
            try:
                resp = self.api.get("/reports/", timeout=5)
                if resp.status_code == 200:
                    reports = resp.json()
                    data["pending_reports"] = str(sum(
                        1 for r in reports if r.get("status") == "pending"))
            except Exception:
                pass
            self.after(0, lambda: self._admin_populate_dash_stats(data))

            try:
                resp_b = self.api.get("/bookings/all?limit=5", timeout=5)
                bookings = resp_b.json().get("bookings", []) if resp_b.status_code == 200 else []
            except Exception:
                bookings = []
            try:
                resp_l = self.api.get("/admin-logs/", timeout=5)
                logs = resp_l.json()[:5] if resp_l.status_code == 200 else []
            except Exception:
                logs = []
            self.after(0, lambda: self._admin_populate_dash_recent(bookings, logs))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_dash_stats(self, data):
        for key, lbl in self._admin_dash_stat_labels.items():
            val = data.get(key, "0")
            try:
                lbl.configure(text=val)
            except Exception:
                pass

    def _admin_populate_dash_recent(self, bookings, logs):
        for w in self._admin_dash_bookings_container.winfo_children():
            w.destroy()
        if bookings:
            for b in bookings[:5]:
                text = f"#{b.get('booking_id')} - {b.get('tenant_name', '?')} ({b.get('status', '?')})"
                ctk.CTkLabel(self._admin_dash_bookings_container, text=text,
                              font=self.body_description_font,
                              text_color=self.text_color).pack(anchor="w", pady=1)
        else:
            ctk.CTkLabel(self._admin_dash_bookings_container, text="No recent bookings",
                          font=self.body_light_font, text_color=self.text_color).pack(anchor="w")

        for w in self._admin_dash_logs_container.winfo_children():
            w.destroy()
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

        self._admin_users_table_container = ctk.CTkFrame(main, fg_color="transparent")
        self._admin_users_table_container.pack(fill="both", expand=True)

        self._admin_refresh_users()

    def _admin_refresh_users(self):
        for w in self._admin_users_table_container.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self._admin_users_table_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        loading = ctk.CTkLabel(scroll, text="Loading users...", font=self.body_paragraph_font,
                                text_color=self.text_color)
        loading.pack(pady=20)

        def _do():
            users = []
            try:
                resp = self.api.get("/users/", timeout=5)
                if resp.status_code == 200:
                    users = resp.json()
            except Exception:
                pass
            search = ""
            try:
                search = self._admin_users_search_entry.get().strip().lower()
            except Exception:
                pass
            if search:
                users = [u for u in users if
                         search in u.get("name", "").lower() or
                         search in u.get("email", "").lower()]
            self.after(0, lambda: self._admin_populate_users(scroll, users))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_users(self, scroll, users):
        for w in scroll.winfo_children():
            w.destroy()

        if not users:
            ctk.CTkLabel(scroll, text="No users found.", font=self.body_paragraph_font,
                          text_color=self.text_color).pack(pady=30)
            return

        headers = ["ID", "Name", "Email", "Role", "Status", "Actions"]
        self._admin_build_table_header(scroll, headers, col_weights=[0, 1, 1, 0, 0, 0])

        for i, user in enumerate(users):
            row_color = self.fg_color if i % 2 == 0 else self.secondary_color
            row = ctk.CTkFrame(scroll, fg_color=row_color, corner_radius=4)
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=str(user.get("user_id", "")), font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(row, text=user.get("name", ""), font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(row, text=user.get("email", ""), font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(row, text=user.get("role", ""), font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=3, padx=10, pady=5, sticky="w")

            status = user.get("status", "active")
            color = self._admin_status_colors.get(status, self.text_color)
            ctk.CTkLabel(row, text=status.capitalize(), font=self.body_description_font,
                          fg_color=color, text_color="white", corner_radius=4,
                          padx=8, pady=2).grid(row=0, column=4, padx=10, pady=5, sticky="w")

            uid = user.get("user_id")
            action_f = ctk.CTkFrame(row, fg_color="transparent")
            action_f.grid(row=0, column=5, padx=10, pady=5, sticky="w")
            if status != "banned":
                ctk.CTkButton(action_f, text="Ban", font=self.body_description_font,
                              fg_color=self.error_red, text_color="white",
                              width=50, height=25,
                              command=lambda uid=uid: self._admin_ban_user(uid)).pack(side="left", padx=2)
            else:
                ctk.CTkButton(action_f, text="Unban", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              width=50, height=25,
                              command=lambda uid=uid: self._admin_unban_user(uid)).pack(side="left", padx=2)

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
    #  SECTION 3: LISTINGS
    # ════════════════════════════════════

    def _build_admin_listings_content(self):
        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main, text="Boarding House Management", font=self.body_bold_font,
                      text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        self._admin_listings_search_entry, self._admin_listings_filter = \
            self._admin_build_search_bar(
                main, "Search by name...", self._admin_refresh_listings,
                has_filter=True, filter_values=["All", "active", "pending", "banned"])

        self._admin_listings_container = ctk.CTkFrame(main, fg_color="transparent")
        self._admin_listings_container.pack(fill="both", expand=True)

        self._admin_refresh_listings()

    def _admin_refresh_listings(self):
        for w in self._admin_listings_container.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self._admin_listings_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        loading = ctk.CTkLabel(scroll, text="Loading listings...", font=self.body_paragraph_font,
                                text_color=self.text_color)
        loading.pack(pady=20)

        def _do():
            listings = []
            try:
                resp = self.api.get("/boarding-houses/feed/dashboard?limit=500", timeout=5)
                if resp.status_code == 200:
                    listings = resp.json()
            except Exception:
                pass
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
            self.after(0, lambda: self._admin_populate_listings(scroll, listings))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_listings(self, scroll, listings):
        for w in scroll.winfo_children():
            w.destroy()

        if not listings:
            ctk.CTkLabel(scroll, text="No listings found.", font=self.body_paragraph_font,
                          text_color=self.text_color).pack(pady=30)
            return

        for listing in listings:
            card = ctk.CTkFrame(scroll, fg_color=self.secondary_color, corner_radius=6,
                                 border_width=1, border_color=self.entry_border)
            card.pack(fill="x", pady=3)
            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color=self.hover_color))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=self.secondary_color))

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(10, 2))
            name = listing.get("name", listing.get("bh_name", "Untitled"))
            ctk.CTkLabel(top, text=name, font=self.body_paragraph_font,
                          text_color=self.text_color).pack(side="left")

            status = listing.get("status", "unknown")
            color = self._admin_status_colors.get(status, self.text_color)
            ctk.CTkLabel(top, text=status.capitalize(), font=self.body_description_font,
                          fg_color=color, text_color="white", corner_radius=4,
                          padx=8, pady=2).pack(side="right")

            verified = listing.get("is_verified", False)
            if verified:
                ctk.CTkLabel(top, text="Verified", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              corner_radius=4, padx=8, pady=2).pack(side="right", padx=(0, 5))

            bottom = ctk.CTkFrame(card, fg_color="transparent")
            bottom.pack(fill="x", padx=15, pady=(2, 10))
            lid = listing.get("id", listing.get("listing_id"))
            ctk.CTkButton(bottom, text="View Detail", font=self.body_description_font,
                          fg_color=self.primary_color, hover_color=self.hover_color,
                          text_color="white", width=90, height=28, cursor="hand2",
                          command=lambda lid=lid: self._admin_show_listing_detail(lid)
                          ).pack(side="left", padx=(0, 5))

            if status != "banned":
                ctk.CTkButton(bottom, text="Ban", font=self.body_description_font,
                              fg_color=self.error_red, text_color="white",
                              width=60, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_ban_listing(lid)
                              ).pack(side="left", padx=(0, 5))
            else:
                ctk.CTkButton(bottom, text="Restore", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              width=60, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_restore_listing(lid)
                              ).pack(side="left", padx=(0, 5))

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
            try:
                resp = self.api.get(f"/boarding-houses/{listing_id}", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
            except Exception:
                pass
            self.after(0, lambda: self._admin_populate_listing_detail(main, data))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_listing_detail(self, parent, data):
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
            ("Permit URL:", data.get("permit_url", "N/A")),
            ("Created:", str(data.get("bh_created_at", ""))[:10] if data.get("bh_created_at") else "N/A"),
        ]:
            row_f = ctk.CTkFrame(right, fg_color="transparent")
            row_f.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row_f, text=label, font=self.body_light_font,
                          text_color=self.text_color, width=90).pack(side="left")
            ctk.CTkLabel(row_f, text=str(val), font=self.body_paragraph_font,
                          text_color=self.text_color).pack(side="left", padx=(10, 0))

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
            self.after(0, self._build_admin_listings_content)
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
            self.after(0, self._build_admin_listings_content)
        threading.Thread(target=_do, daemon=True).start()

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
            dropdown_fg_color=self.fg_color, text_color=self.text_color,
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

        loading = ctk.CTkLabel(self._admin_bookings_table, text="Loading bookings...",
                                font=self.body_paragraph_font, text_color=self.text_color)
        loading.pack(pady=20)

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
                pass
            try:
                resp = self.api.get(f"/bookings/all{params}", timeout=5)
                if resp.status_code == 200:
                    bookings_data = resp.json().get("bookings", [])
            except Exception:
                pass
            self.after(0, lambda: self._admin_populate_bookings(stats_data, bookings_data))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_bookings(self, stats, bookings):
        for w in self._admin_bookings_table.winfo_children():
            w.destroy()

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

        scroll = ctk.CTkScrollableFrame(self._admin_bookings_table, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        headers = ["ID", "Tenant", "Property", "Room", "Check-in", "Check-out", "Status", "Total", "Actions"]
        col_weights = [0, 1, 1, 0, 0, 0, 0, 0, 0]
        self._admin_build_table_header(scroll, headers, col_weights)

        for i, b in enumerate(bookings):
            row_color = self.fg_color if i % 2 == 0 else self.secondary_color
            row = ctk.CTkFrame(scroll, fg_color=row_color, corner_radius=4)
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=str(b.get("booking_id", "")), font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=0, padx=8, pady=5, sticky="w")

            ctk.CTkLabel(row, text=b.get("tenant_name", f"User #{b.get('user_id')}"),
                          font=self.body_light_font, text_color=self.text_color).grid(
                row=0, column=1, padx=8, pady=5, sticky="w")

            ctk.CTkLabel(row, text=b.get("property_name", "N/A"), font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=2, padx=8, pady=5, sticky="w")

            room_no = b.get("room_number", "?")
            ctk.CTkLabel(row, text=f"#{room_no}" if room_no else "?", font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=3, padx=8, pady=5, sticky="w")

            ci = str(b.get("check_in", "") or "")[:10]
            co = str(b.get("check_out", "") or "")[:10]
            ctk.CTkLabel(row, text=ci, font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=4, padx=8, pady=5, sticky="w")
            ctk.CTkLabel(row, text=co, font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=5, padx=8, pady=5, sticky="w")

            status = b.get("status", "unknown")
            color = self._admin_status_colors.get(status, self.text_color)
            ctk.CTkLabel(row, text=status.capitalize(), font=self.body_description_font,
                          fg_color=color, text_color="white",
                          corner_radius=4, padx=8, pady=2).grid(
                row=0, column=6, padx=8, pady=5, sticky="w")

            ctk.CTkLabel(row, text=f"\u20B1{b.get('total_price', '0')}", font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=7, padx=8, pady=5, sticky="w")

            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.grid(row=0, column=8, padx=8, pady=5, sticky="w")
            bid = b.get("booking_id")
            ctk.CTkButton(action_frame, text="View", font=self.body_description_font,
                          fg_color=self.primary_color, hover_color=self.hover_color,
                          text_color="white", width=50, height=24,
                          command=lambda bid=bid: self._admin_show_booking_detail(bid)
                          ).pack(side="left", padx=1)
            if status == "pending":
                ctk.CTkButton(action_frame, text="Approve", font=self.body_description_font,
                              fg_color="green", hover_color="darkgreen",
                              text_color="white", width=60, height=24,
                              command=lambda bid=bid: self._admin_booking_change_status(
                                  bid, "active")).pack(side="left", padx=1)
                ctk.CTkButton(action_frame, text="Cancel", font=self.body_description_font,
                              fg_color=self.error_red, hover_color="#b52e2a",
                              text_color="white", width=55, height=24,
                              command=lambda bid=bid: self._admin_booking_change_status(
                                  bid, "cancelled")).pack(side="left", padx=1)

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
                pass
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

        self._admin_reviews_container = ctk.CTkFrame(main, fg_color="transparent")
        self._admin_reviews_container.pack(fill="both", expand=True)

        loading = ctk.CTkLabel(self._admin_reviews_container, text="Loading reviews...",
                                font=self.body_paragraph_font, text_color=self.text_color)
        loading.pack(pady=20)

        def _do():
            reviews = []
            try:
                resp = self.api.get("/social/reviews/all", timeout=5)
                if resp.status_code == 200:
                    reviews = resp.json()
            except Exception:
                pass
            self.after(0, lambda: self._admin_populate_reviews(reviews))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_reviews(self, reviews):
        for w in self._admin_reviews_container.winfo_children():
            w.destroy()

        if not reviews:
            ctk.CTkLabel(self._admin_reviews_container, text="No reviews found.",
                          font=self.body_paragraph_font, text_color=self.text_color).pack(pady=30)
            return

        scroll = ctk.CTkScrollableFrame(self._admin_reviews_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        headers = ["ID", "Listing ID", "User ID", "Rating", "Comment", "Date", "Actions"]
        col_weights = [0, 0, 0, 0, 2, 0, 0]
        self._admin_build_table_header(scroll, headers, col_weights)

        for i, review in enumerate(reviews):
            row_color = self.fg_color if i % 2 == 0 else self.secondary_color
            row = ctk.CTkFrame(scroll, fg_color=row_color, corner_radius=4)
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=str(review.get("review_id", "")), font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=0, padx=8, pady=5, sticky="w")
            ctk.CTkLabel(row, text=str(review.get("listing_id", "")), font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=1, padx=8, pady=5, sticky="w")
            ctk.CTkLabel(row, text=str(review.get("user_id", "")), font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=2, padx=8, pady=5, sticky="w")

            rating = review.get("rating", 0)
            stars = "\u2605" * rating + "\u2606" * (5 - rating)
            ctk.CTkLabel(row, text=stars, font=self.body_paragraph_font,
                          text_color=self.primary_color).grid(row=0, column=3, padx=8, pady=5, sticky="w")

            comment = review.get("comment", "") or ""
            if len(comment) > 60:
                comment = comment[:60] + "..."
            ctk.CTkLabel(row, text=comment, font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=4, padx=8, pady=5, sticky="w")

            created = str(review.get("created_at", "") or "")[:10]
            ctk.CTkLabel(row, text=created, font=self.body_light_font,
                          text_color=self.text_color).grid(row=0, column=5, padx=8, pady=5, sticky="w")

            rid = review.get("review_id")
            ctk.CTkButton(row, text="Delete", font=self.body_description_font,
                          fg_color=self.error_red, text_color="white",
                          width=60, height=25,
                          command=lambda rid=rid: self._admin_delete_review(rid)
                          ).grid(row=0, column=6, padx=8, pady=5, sticky="w")

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
            dropdown_fg_color=self.fg_color, text_color=self.text_color,
            width=160, height=35, state="readonly",
            command=lambda c: self._admin_refresh_reports())
        self._admin_reports_filter.pack(side="left")
        self._admin_reports_filter.set("All")

        self._admin_reports_container = ctk.CTkFrame(main, fg_color="transparent")
        self._admin_reports_container.pack(fill="both", expand=True)

        self._admin_refresh_reports()

    def _admin_refresh_reports(self):
        for w in self._admin_reports_container.winfo_children():
            w.destroy()

        loading = ctk.CTkLabel(self._admin_reports_container, text="Loading reports...",
                                font=self.body_paragraph_font, text_color=self.text_color)
        loading.pack(pady=20)

        def _do():
            reports = []
            try:
                resp = self.api.get("/reports/", timeout=5)
                if resp.status_code == 200:
                    reports = resp.json()
            except Exception:
                pass
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
        for w in self._admin_reports_container.winfo_children():
            w.destroy()

        if not reports:
            ctk.CTkLabel(self._admin_reports_container, text="No reports found.",
                          font=self.body_paragraph_font, text_color=self.text_color).pack(pady=30)
            return

        scroll = ctk.CTkScrollableFrame(self._admin_reports_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for report in reports:
            rid = report.get("report_id")
            status = report.get("status", "pending")
            color = self._admin_status_colors.get(status, self.text_color)

            card = ctk.CTkFrame(scroll, fg_color=self.secondary_color, corner_radius=6,
                                 border_width=1, border_color=self.entry_border)
            card.pack(fill="x", pady=3)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(10, 2))

            info = f"Report #{rid} \u2014 {report.get('target_type')} #{report.get('target_id')}"
            ctk.CTkLabel(top, text=info, font=self.body_paragraph_font,
                          text_color=self.text_color).pack(side="left")
            ctk.CTkLabel(top, text=status.capitalize(), font=self.body_description_font,
                          fg_color=color, text_color="white",
                          corner_radius=4, padx=8, pady=2).pack(side="right")

            mid = ctk.CTkFrame(card, fg_color="transparent")
            mid.pack(fill="x", padx=15, pady=(2, 2))
            reason = report.get("reason", "") or ""
            if len(reason) > 200:
                reason = reason[:200] + "..."
            ctk.CTkLabel(mid, text=f"Reason: {reason}", font=self.body_light_font,
                          text_color=self.text_color, wraplength=600,
                          justify="left").pack(anchor="w")

            bottom = ctk.CTkFrame(card, fg_color="transparent")
            bottom.pack(fill="x", padx=15, pady=(2, 10))

            created = str(report.get("created_at", "") or "")[:16]
            ctk.CTkLabel(bottom, text=f"Reported: {created}", font=self.body_description_font,
                          text_color=self.text_color).pack(side="left")

            if status == "pending" or status == "reviewed":
                ctk.CTkButton(bottom, text="Resolve", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              width=80, height=28, cursor="hand2",
                              command=lambda rid=rid: self._admin_resolve_report(rid)
                              ).pack(side="right", padx=(5, 0))
                ctk.CTkButton(bottom, text="Dismiss", font=self.body_description_font,
                              fg_color=self.text_color, text_color="white",
                              width=80, height=28, cursor="hand2",
                              command=lambda rid=rid: self._admin_dismiss_report(rid)
                              ).pack(side="right", padx=(5, 0))

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
    #  SECTION 7: PERMIT VERIFIER
    # ════════════════════════════════════

    def _build_admin_permit_content(self):
        scroll = ctk.CTkScrollableFrame(self._admin_content_wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        main = ctk.CTkFrame(scroll, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main, text="Permit Verifier", font=self.body_bold_font,
                      text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        filter_frame = ctk.CTkFrame(main, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))
        self._admin_permit_filter = ctk.CTkComboBox(
            filter_frame, values=["All", "Unverified", "Verified"],
            font=self.body_light_font, fg_color=self.fg_color,
            border_color=self.entry_border, border_width=1,
            button_color=self.primary_color, button_hover_color=self.hover_color,
            dropdown_fg_color=self.fg_color, text_color=self.text_color,
            width=160, height=35, state="readonly",
            command=lambda c: self._admin_refresh_permits())
        self._admin_permit_filter.pack(side="left")
        self._admin_permit_filter.set("All")

        self._admin_permits_container = ctk.CTkFrame(main, fg_color="transparent")
        self._admin_permits_container.pack(fill="both", expand=True)

        self._admin_refresh_permits()

    def _admin_refresh_permits(self):
        for w in self._admin_permits_container.winfo_children():
            w.destroy()

        loading = ctk.CTkLabel(self._admin_permits_container, text="Loading listings...",
                                font=self.body_paragraph_font, text_color=self.text_color)
        loading.pack(pady=20)

        def _do():
            listings = []
            try:
                resp = self.api.get("/boarding-houses/feed/dashboard?limit=500", timeout=5)
                if resp.status_code == 200:
                    listings = resp.json()
            except Exception:
                pass
            filter_val = "All"
            try:
                filter_val = self._admin_permit_filter.get()
            except Exception:
                pass
            if filter_val == "Unverified":
                listings = [l for l in listings if not l.get("is_verified")]
            elif filter_val == "Verified":
                listings = [l for l in listings if l.get("is_verified")]
            self.after(0, lambda: self._admin_populate_permits(listings))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_permits(self, listings):
        for w in self._admin_permits_container.winfo_children():
            w.destroy()

        if not listings:
            ctk.CTkLabel(self._admin_permits_container, text="No listings found.",
                          font=self.body_paragraph_font, text_color=self.text_color).pack(pady=30)
            return

        scroll = ctk.CTkScrollableFrame(self._admin_permits_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for listing in listings:
            verified = listing.get("is_verified", False)
            name = listing.get("name", listing.get("bh_name", "Untitled"))
            lid = listing.get("id", listing.get("listing_id"))

            card = ctk.CTkFrame(scroll, fg_color=self.secondary_color, corner_radius=6,
                                 border_width=1, border_color=self.entry_border)
            card.pack(fill="x", pady=3)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(10, 2))
            ctk.CTkLabel(top, text=name, font=self.body_paragraph_font,
                          text_color=self.text_color).pack(side="left")

            status_text = "Verified" if verified else "Unverified"
            status_color = "green" if verified else self.hover_color
            ctk.CTkLabel(top, text=status_text, font=self.body_description_font,
                          fg_color=status_color, text_color="white",
                          corner_radius=4, padx=8, pady=2).pack(side="right")

            mid = ctk.CTkFrame(card, fg_color="transparent")
            mid.pack(fill="x", padx=15, pady=(2, 2))
            ctk.CTkLabel(mid, text=f"Listing ID: #{lid}", font=self.body_light_font,
                          text_color=self.text_color).pack(side="left")
            permit_url = listing.get("permit_url", "")
            if permit_url:
                ctk.CTkLabel(mid, text=f"Permit: {permit_url[:60]}...",
                              font=self.body_description_font,
                              text_color=self.text_color).pack(side="right")

            bottom = ctk.CTkFrame(card, fg_color="transparent")
            bottom.pack(fill="x", padx=15, pady=(2, 10))

            if not verified:
                ctk.CTkButton(bottom, text="Approve Permit", font=self.body_description_font,
                              fg_color="green", text_color="white",
                              width=120, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_approve_permit(lid)
                              ).pack(side="left", padx=(0, 5))
                ctk.CTkButton(bottom, text="Reject", font=self.body_description_font,
                              fg_color=self.error_red, text_color="white",
                              width=80, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_reject_permit(lid)
                              ).pack(side="left")
            else:
                ctk.CTkButton(bottom, text="Revoke", font=self.body_description_font,
                              fg_color=self.hover_color, text_color="white",
                              width=80, height=28, cursor="hand2",
                              command=lambda lid=lid: self._admin_revoke_permit(lid)
                              ).pack(side="left")

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
            self.after(0, self._admin_refresh_permits)

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
            self.after(0, self._admin_refresh_permits)

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
            self.after(0, self._admin_refresh_permits)

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

        container = ctk.CTkFrame(main, fg_color="transparent")
        container.pack(fill="both", expand=True)

        loading = ctk.CTkLabel(container, text="Loading admin logs...",
                                font=self.body_paragraph_font, text_color=self.text_color)
        loading.pack(pady=20)

        def _do():
            logs = []
            try:
                resp = self.api.get("/admin-logs/", timeout=5)
                if resp.status_code == 200:
                    logs = resp.json()
            except Exception:
                pass
            self.after(0, lambda: self._admin_populate_logs(container, logs))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_logs(self, parent, logs):
        for w in parent.winfo_children():
            w.destroy()

        if not logs:
            ctk.CTkLabel(parent, text="No admin logs found.",
                          font=self.body_paragraph_font, text_color=self.text_color).pack(pady=20)
            return

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for log in logs:
            card = ctk.CTkFrame(scroll, fg_color=self.secondary_color, corner_radius=4,
                                 border_width=1, border_color=self.entry_border)
            card.pack(fill="x", pady=2)

            ts = str(log.get("performed_at", "") or "")[:19]
            action = log.get("action", "?")
            target_type = log.get("target_type", "?")
            target_id = log.get("target_id", "?")
            info = f"{ts} \u2014 {action} \u2014 {target_type} #{target_id}"

            ctk.CTkLabel(card, text=info, font=self.body_light_font,
                          text_color=self.text_color).pack(side="left", padx=15, pady=8)

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
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
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

        loading = ctk.CTkLabel(self._admin_list_frame, text="Loading...",
                                font=self.body_light_font, text_color=self.text_color)
        loading.pack(pady=10)

        def _do():
            admins = []
            try:
                resp = self.api.get("/users/", timeout=5)
                if resp.status_code == 200:
                    all_users = resp.json()
                    admins = [u for u in all_users if u.get("role") == "admin"]
            except Exception:
                pass
            self.after(0, lambda: self._admin_populate_admin_list(admins))

        threading.Thread(target=_do, daemon=True).start()

    def _admin_populate_admin_list(self, admins):
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
