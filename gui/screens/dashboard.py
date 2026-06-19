import customtkinter as ctk
import requests
import threading
import calendar
from PIL import Image
import io
from src.logger import logger
from datetime import datetime, date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


class DashboardMixin:

    STATUS_COLORS = {
        "completed": ("#2E7D32", "#4CAF50"),
        "pending": ("#E65100", "#FF9800"),
        "failed": ("#C62828", "#EF5350"),
        "refunded": ("#1565C0", "#42A5F5"),
        "active": ("#2E7D32", "#4CAF50"),
        "cancelled": ("#757575", "#9E9E9E"),
        "confirmed": ("#1565C0", "#42A5F5"),
    }

    # ── Shell ──────────────────────────────────────────────────────

    def show_tenant_dashboard(self):
        print("[DEBUG] Showing: Tenant Dashboard")
        self.clear_container()

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{int(w * 0.85)}x{int(h * 0.85)}")
        self.resizable(True, True)

        self.is_sidebar_expanded = True
        self.is_search_expanded = False

        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        self._build_tenant_navbar()
        self._build_tenant_sidebar()

        self.content_wrapper = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.content_wrapper.pack(fill="both", expand=True, padx=(260, 10), pady=20)

        self.show_tenant_dashboard_content()
        self._fetch_notif_count()

    # ── Navbar ─────────────────────────────────────────────────────

    def _build_tenant_navbar(self):
        self.nav_bar_frame = ctk.CTkFrame(self.form_container,
                                          fg_color="transparent",
                                          height=60,
                                          border_width=1,
                                          border_color=self.entry_border)
        self.nav_bar_frame.pack(side="top", fill="x")

        self.bg_hamburg_menu = ctk.CTkButton(self.nav_bar_frame,
                                             image=self.hamburg_menu_icon,
                                             text=None,
                                             fg_color="transparent",
                                             hover_color=self.hover_color,
                                             width=25, height=15,
                                             command=self.animate_sidebar)
        self.bg_hamburg_menu.pack(side="left", padx=15, pady=(20, 25))

        self.bg_logo = ctk.CTkLabel(self.nav_bar_frame, text=None, image=self.logo)
        self.bg_logo.pack(side="left", pady=(15, 20))

        self.search_bg_frame = ctk.CTkFrame(self.nav_bar_frame,
                                            height=40, width=40,
                                            fg_color="transparent")
        self.search_bg_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.search_bg_frame.pack_propagate(False)

        self.search_btn = ctk.CTkButton(self.search_bg_frame, text=None,
                                        image=self.search_icon,
                                        width=40, height=40,
                                        fg_color="transparent",
                                        hover_color=self.hover_color,
                                        command=self.animate_search_bar)
        self.search_btn.pack(side="left")

        self.search_entry = ctk.CTkEntry(self.search_bg_frame,
                                         placeholder_text="Search for boarding houses, cities",
                                         font=self.body_light_font,
                                         height=40, border_width=0,
                                         fg_color="transparent")
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        self.notif_bell_frame = ctk.CTkFrame(self.nav_bar_frame, fg_color="transparent")
        self.notif_bell_frame.pack(side="right", padx=(0, 5))

        self.notif_bell_btn = ctk.CTkLabel(self.notif_bell_frame, text="",
                                           image=self.notification_icon, cursor="hand2")
        self.notif_bell_btn.pack(side="left", padx=5)
        self.notif_bell_btn.bind("<Button-1>", lambda e: self.show_notifications_page())

        self.notif_badge = ctk.CTkLabel(self.notif_bell_frame, text="",
                                        width=16, height=16, corner_radius=8,
                                        fg_color=self.error_red, text_color="white",
                                        font=ctk.CTkFont(size=9, weight="bold"))
        self.notif_badge.place(x=18, y=-2)

        self.profile_frame = ctk.CTkFrame(self.nav_bar_frame, fg_color="transparent")
        self.profile_frame.pack(side="right", padx=25, pady=10)

        self.nav_pfp = ctk.CTkLabel(self.profile_frame, text=None,
                                    image=self.pfp_placeholder_sm,
                                    width=32, height=32)
        self.nav_pfp.pack(side="left", padx=(0, 12))

        self.profile_text_frame = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        self.profile_text_frame.pack(side="left")

        user_name = getattr(self, 'current_user', {}).get('name', 'User')

        self.name_label = ctk.CTkLabel(self.profile_text_frame, text=user_name,
                                       font=self.body_light_font, text_color=self.text_color)
        self.name_label.pack(side="left")

        self.profile_chevron = ctk.CTkLabel(self.profile_text_frame, text="▾",
                                            font=self.body_light_font, text_color=self.text_color)
        self.profile_chevron.pack(side="left", padx=(4, 0))

        self.profile_frame.bind("<Button-1>", lambda e: self._toggle_user_menu())
        self.profile_frame.configure(cursor="hand2")
        for child in self.profile_frame.winfo_children():
            child.bind("<Button-1>", lambda e: self._toggle_user_menu())

    # ── Sidebar ────────────────────────────────────────────────────

    def _build_tenant_sidebar(self):
        self.sidebar_main_frame = ctk.CTkFrame(self.form_container,
                                               fg_color="transparent",
                                               width=250, corner_radius=0,
                                               border_color=self.entry_border,
                                               border_width=1)
        self.sidebar_main_frame.place(x=0, y=0, relheight=1.0)
        self.sidebar_main_frame.pack_propagate(False)

        self.sidebar_logo_frame = ctk.CTkFrame(self.sidebar_main_frame, fg_color="transparent")
        self.sidebar_logo_frame.pack(fill="x", pady=(20, 0))

        self.sidebar_hamburger_btn = ctk.CTkButton(self.sidebar_logo_frame,
                                                   image=self.hamburg_menu_icon,
                                                   text=None, fg_color="transparent",
                                                   hover_color=self.hover_color,
                                                   width=25, height=15,
                                                   command=self.animate_sidebar)
        self.sidebar_hamburger_btn.pack(side="left", padx=15)

        self.logo_image = ctk.CTkLabel(self.sidebar_logo_frame, text=None, image=self.logo)
        self.logo_image.pack(side="left")

        self.menu_btn_frame = ctk.CTkFrame(self.sidebar_main_frame, fg_color="transparent")
        self.menu_btn_frame.pack(fill="both", expand=True, pady=20)
        self.menu_btn_frame.grid_columnconfigure(0, weight=1)

        self.dashboard_btn = ctk.CTkButton(self.menu_btn_frame, text="Dashboard",
                                           width=230, height=40,
                                           hover_color=self.hover_color,
                                           fg_color=self.primary_color, text_color="white",
                                           font=self.body_big_font,
                                           command=self.show_tenant_dashboard_content)
        self.dashboard_btn.grid(row=0, column=0, padx=10, pady=(10, 30))

        self.explore_btn = ctk.CTkButton(self.menu_btn_frame, text="Explore",
                                         width=230, height=40,
                                         hover_color=self.hover_color,
                                         fg_color="transparent", text_color=self.text_color,
                                         font=self.body_big_font,
                                         command=self.show_tenant_explore_content)
        self.explore_btn.grid(row=1, column=0, padx=10, pady=(0, 30))

        self.viewing_btn = ctk.CTkButton(self.menu_btn_frame, text="Viewing",
                                         width=230, height=40,
                                         hover_color=self.hover_color,
                                         fg_color="transparent", text_color=self.text_color,
                                         font=self.body_big_font,
                                         command=self.show_tenant_viewings_content)
        self.viewing_btn.grid(row=2, column=0, padx=10, pady=(0, 30))

        self.favorite_btn = ctk.CTkButton(self.menu_btn_frame, text="Favorite",
                                          width=230, height=40,
                                          hover_color=self.hover_color,
                                          fg_color="transparent", text_color=self.text_color,
                                          font=self.body_big_font,
                                          command=self.show_tenant_favorites_content)
        self.favorite_btn.grid(row=3, column=0, padx=10, pady=(0, 30))

        self.bookings_btn = ctk.CTkButton(self.menu_btn_frame, text="My Bookings",
                                          width=230, height=40,
                                          hover_color=self.hover_color,
                                          fg_color="transparent", text_color=self.text_color,
                                          font=self.body_big_font,
                                          command=self.show_tenant_bookings_content)
        self.bookings_btn.grid(row=4, column=0, padx=10, pady=(0, 30))

        self.logout_btn = ctk.CTkButton(self.menu_btn_frame, text="Logout",
                                        width=230, height=40,
                                        hover_color=self.hover_color,
                                        fg_color="transparent", text_color=self.text_color,
                                        font=self.body_big_font,
                                        command=self._handle_logout)
        self.logout_btn.grid(row=5, column=0, padx=10, pady=(30, 0))

    def _set_active_sidebar_btn(self, active):
        buttons = {
            "dashboard": self.dashboard_btn,
            "explore": self.explore_btn,
            "viewing": self.viewing_btn,
            "favorite": self.favorite_btn,
            "bookings": self.bookings_btn,
        }
        for name, btn in buttons.items():
            if name == active:
                btn.configure(fg_color=self.primary_color, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=self.text_color)

    # ── Dashboard Content (default landing) ────────────────────────

    def show_tenant_dashboard_content(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_active_sidebar_btn("dashboard")

        main = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        main.pack(fill="both", expand=True)

        ctk.CTkLabel(main, text="Dashboard", font=self.alt_title_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 15))

        self._dash_progress = ctk.CTkProgressBar(main, mode="indeterminate",
                                                  fg_color=self.entry_border,
                                                  progress_color=self.primary_color)
        self._dash_progress.pack(fill="x", pady=(0, 10))
        self._dash_progress.start()

        self._dash_scroll = ctk.CTkScrollableFrame(main, fg_color="transparent")
        self._dash_scroll.pack(fill="both", expand=True)

        self._dash_lease_frame = ctk.CTkFrame(self._dash_scroll, fg_color="transparent")
        self._dash_lease_frame.pack(fill="x", pady=(0, 15))

        self._dash_stats_frame = ctk.CTkFrame(self._dash_scroll, fg_color="transparent")
        self._dash_stats_frame.pack(fill="x", pady=(0, 15))

        self._dash_payments_frame = ctk.CTkFrame(self._dash_scroll, fg_color="transparent")
        self._dash_payments_frame.pack(fill="x", pady=(0, 15))

        self._dash_actions_frame = ctk.CTkFrame(self._dash_scroll, fg_color="transparent")
        self._dash_actions_frame.pack(fill="x", pady=(0, 15))

        self._load_dashboard_data()

    def _load_dashboard_data(self):
        user_id = getattr(self, 'current_user', {}).get('user_id')

        def _do():
            bookings = []
            payments = []
            favorites = []
            try:
                with ThreadPoolExecutor(max_workers=3) as pool:
                    futures = {
                        pool.submit(self._fetch_json, f"/bookings/user/{user_id}"): "bookings",
                        pool.submit(self._fetch_json, f"/payments/user/{user_id}"): "payments",
                        pool.submit(self._fetch_json, f"/favorites/user/{user_id}"): "favorites",
                    }
                    for future in as_completed(futures):
                        key = futures[future]
                        try:
                            result = future.result()
                            if key == "bookings":
                                bookings = result
                            elif key == "payments":
                                payments = result
                            elif key == "favorites":
                                favorites = result
                        except Exception:
                            pass
            except Exception:
                try:
                    resp = self.api.get(f"/bookings/user/{user_id}", timeout=5)
                    if resp.status_code == 200:
                        bookings = resp.json()
                except Exception:
                    pass
                try:
                    resp = self.api.get(f"/payments/user/{user_id}", timeout=5)
                    if resp.status_code == 200:
                        payments = resp.json()
                except Exception:
                    pass
                try:
                    resp = self.api.get(f"/favorites/user/{user_id}", timeout=5)
                    if resp.status_code == 200:
                        favorites = resp.json()
                except Exception:
                    pass

            active = [b for b in bookings if b.get("status") == "active"]
            pending_b = [b for b in bookings if b.get("status") == "pending"]
            next_payment = None
            for p in payments:
                if p.get("status") == "pending":
                    next_payment = p
                    break

            self.after(0, lambda: self._build_dashboard_content(
                active, pending_b, payments, favorites, next_payment
            ))

        threading.Thread(target=_do, daemon=True).start()

    def _fetch_json(self, url):
        resp = self.api.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        return []

    def _build_dashboard_content(self, active_bookings, pending_bookings,
                                  payments, favorites, next_payment):
        if hasattr(self, '_dash_progress') and self._dash_progress:
            self._dash_progress.stop()
            self._dash_progress.pack_forget()
            self._dash_progress = None

        self._build_active_lease(self._dash_lease_frame, active_bookings)
        self._build_dash_stats(self._dash_stats_frame, active_bookings,
                               pending_bookings, favorites, next_payment)
        self._build_recent_payments(self._dash_payments_frame, payments)
        self._build_quick_actions(self._dash_actions_frame)

    # ── Dashboard Section 1: Active Lease Card ─────────────────────

    def _build_active_lease(self, parent, active_bookings):
        for w in parent.winfo_children():
            w.destroy()

        if active_bookings:
            b = active_bookings[0]
            card = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                corner_radius=8, height=110,
                                border_width=1, border_color=self.entry_border)
            card.pack(fill="x")
            card.pack_propagate(False)

            accent = ctk.CTkFrame(card, width=4, fg_color=self.primary_color,
                                  corner_radius=2)
            accent.pack(side="left", fill="y", padx=(0, 12))

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", padx=15, pady=12, expand=True)

            ctk.CTkLabel(inner, text="Active Lease",
                         font=self.body_bold_paragraph_font,
                         text_color=self.text_color).pack(anchor="w")

            room_info = f"Booking #{b.get('booking_id')} — Room #{b.get('room_id')}"
            ctk.CTkLabel(inner, text=room_info,
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(anchor="w")

            dates = f"{b.get('check_in', '?')} → {b.get('check_out', '?')}"
            if b.get("total_price") is not None:
                dates += f"  |  P{b['total_price']} total"
            ctk.CTkLabel(inner, text=dates,
                         font=self.body_light_font,
                         text_color=self.text_color).pack(anchor="w")

            badge = ctk.CTkLabel(inner, text="Active",
                                 fg_color=self.STATUS_COLORS["active"],
                                 text_color="white",
                                 corner_radius=4,
                                 font=ctk.CTkFont(size=11, weight="bold"),
                                 width=60)
            badge.pack(anchor="e")

            view_btn = ctk.CTkButton(card, text="View Details",
                                     font=self.body_description_font,
                                     fg_color="transparent",
                                     text_color=self.primary_color,
                                     hover_color=self.hover_color,
                                     cursor="hand2",
                                     command=self.show_tenant_bookings_content)
            view_btn.pack(side="right", padx=(0, 15), pady=(0, 10))
        else:
            card = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                corner_radius=8, height=90,
                                border_width=1, border_color=self.entry_border)
            card.pack(fill="x")
            card.pack_propagate(False)

            ctk.CTkLabel(card, text="You haven't booked a place yet",
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(pady=(10, 4))

            ctk.CTkButton(card, text="Browse Listings",
                          font=self.body_paragraph_font,
                          fg_color=self.primary_color,
                          hover_color=self.hover_color,
                          text_color="white",
                          cursor="hand2",
                          command=self.show_tenant_explore_content).pack(pady=(0, 10))

    # ── Dashboard Section 2: Stats Row ─────────────────────────────

    def _build_dash_stats(self, parent, active, pending_b, favorites, next_payment):
        for w in parent.winfo_children():
            w.destroy()

        parent.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="dashstats")

        stats = [
            ("Active Bookings", str(len(active)), self.primary_color),
            ("Pending Bookings", str(len(pending_b)), self.hover_color),
            ("Saved Favorites", str(len(favorites)), self.text_color),
            ("Next Payment", f"P{next_payment['amount']}" if next_payment else "—",
             self.error_red if next_payment else self.text_color),
        ]
        for i, (title, val, accent_color) in enumerate(stats):
            card = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                corner_radius=6, height=70,
                                border_width=1, border_color=self.entry_border)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            card.pack_propagate(False)
            card.grid_propagate(False)

            accent_bar = ctk.CTkFrame(card, height=3, fg_color=accent_color, corner_radius=0)
            accent_bar.place(x=0, y=0, relwidth=1)

            ctk.CTkLabel(card, text=title, font=self.body_description_font,
                         text_color=self.text_color).place(x=12, y=8)
            ctk.CTkLabel(card, text=val, font=self.body_bold_paragraph_font,
                         text_color=self.text_color).place(x=12, y=30)

    # ── Dashboard Section 3: Recent Payments ───────────────────────

    def _build_recent_payments(self, parent, payments):
        for w in parent.winfo_children():
            w.destroy()

        ctk.CTkLabel(parent, text="Recent Payments",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 8))

        recent = payments[:5]
        if not recent:
            ctk.CTkLabel(parent, text="No payments yet — payments will appear here once you book a place.",
                         font=self.body_light_font,
                         text_color=self.text_color).pack(pady=20)
            return

        for p in recent:
            row = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                               corner_radius=6, height=36,
                               border_width=1, border_color=self.entry_border)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            paid_at = p.get("paid_at", "—")[:10] if p.get("paid_at") else "—"
            ctk.CTkLabel(row, text=paid_at,
                         font=self.body_light_font,
                         text_color=self.text_color).pack(side="left", padx=12)

            ctk.CTkLabel(row, text=f"P{p['amount']}",
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=12)

            method = p.get("method", "—")
            ctk.CTkLabel(row, text=method.replace("_", " ").title(),
                         font=self.body_light_font,
                         text_color=self.text_color).pack(side="left", padx=12)

            status = p.get("status", "unknown")
            color = self.STATUS_COLORS.get(status, ("#757575", "#9E9E9E"))
            badge = ctk.CTkLabel(row, text=status.title(),
                                 fg_color=color, text_color="white",
                                 corner_radius=4,
                                 font=ctk.CTkFont(size=10, weight="bold"),
                                 width=60)
            badge.pack(side="right", padx=12)

    # ── Dashboard Section 4: Quick Actions ─────────────────────────

    def _build_quick_actions(self, parent):
        for w in parent.winfo_children():
            w.destroy()

        ctk.CTkLabel(parent, text="Quick Actions",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 8))

        actions = [
            ("Browse Listings", self.show_tenant_explore_content),
            ("My Bookings", self.show_tenant_bookings_content),
            ("Saved", self.show_tenant_favorites_content),
            ("Notifications", self.show_notifications_page),
        ]

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x")
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="actions")

        for i, (label, cmd) in enumerate(actions):
            card = ctk.CTkFrame(frame, fg_color=self.secondary_color,
                                corner_radius=8, height=70,
                                border_width=1, border_color=self.entry_border,
                                cursor="hand2")
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            card.pack_propagate(False)
            card.grid_propagate(False)

            ctk.CTkLabel(card, text=label,
                         font=self.body_paragraph_font,
                         text_color=self.primary_color).place(relx=0.5, rely=0.5,
                                                               anchor="center")

            card.bind("<Button-1>", lambda e, c=cmd: c())
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, c=cmd: c())

    # ── Explore Content ────────────────────────────────────────────

    def show_tenant_explore_content(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_active_sidebar_btn("explore")

        wrapper = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        wrapper.pack(fill="both", expand=True)

        user_name = getattr(self, 'current_user', {}).get('name', 'User')

        welcome_frame = ctk.CTkFrame(wrapper, fg_color=self.secondary_color,
                                     corner_radius=8, height=80,
                                     border_width=1, border_color=self.entry_border)
        welcome_frame.pack(fill="x", pady=(0, 15))
        welcome_frame.pack_propagate(False)

        inner_welcome = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        inner_welcome.pack(fill="both", padx=20, pady=15)

        accent = ctk.CTkFrame(inner_welcome, width=4, fg_color=self.primary_color,
                              corner_radius=2)
        accent.pack(side="left", fill="y", padx=(0, 12))

        welcome_text = f"Welcome back, {user_name}!"
        today_str = datetime.now().strftime("%A, %B %d, %Y")
        ctk.CTkLabel(inner_welcome, text=welcome_text,
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(anchor="w")
        ctk.CTkLabel(inner_welcome, text=today_str,
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w")

        stats_row_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        stats_row_frame.pack(fill="x", pady=(0, 15))
        stats_row_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="explorestats")

        stats_cards = [
            ("Active Bookings", "—", self.primary_color),
            ("Saved Favorites", "—", self.hover_color),
            ("Total Reviews", "—", self.text_color),
        ]
        self._stat_labels = {}
        for i, (title, val, accent_color) in enumerate(stats_cards):
            card = ctk.CTkFrame(stats_row_frame, fg_color=self.secondary_color,
                                corner_radius=6, height=70,
                                border_width=1, border_color=self.entry_border)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            card.pack_propagate(False)
            card.grid_propagate(False)

            accent_bar = ctk.CTkFrame(card, height=3, fg_color=accent_color, corner_radius=0)
            accent_bar.place(x=0, y=0, relwidth=1)

            ctk.CTkLabel(card, text=title, font=self.body_description_font,
                         text_color=self.text_color).place(x=12, y=8)
            val_lbl = ctk.CTkLabel(card, text=val, font=self.body_bold_paragraph_font,
                                   text_color=self.text_color)
            val_lbl.place(x=12, y=30)
            self._stat_labels[title] = val_lbl

        filter_scroll_frame = ctk.CTkScrollableFrame(wrapper, orientation="horizontal",
                                                      height=50, fg_color="transparent")
        filter_scroll_frame.pack(fill="x")

        filters = ["All", "Wi-Fi Included", "With Meals", "Furnished",
                   "Near University", "Pet Friendly", "Aircon"]
        self.filter_buttons = {}
        for f in filters:
            btn = ctk.CTkButton(filter_scroll_frame, text=f, height=32,
                                corner_radius=16, fg_color=self.secondary_color,
                                text_color=self.text_color, hover_color=self.hover_color,
                                command=lambda f_name=f: self.toggle_filter(f_name))
            btn.pack(side="left", padx=(0, 10))
            self.filter_buttons[f] = btn
        self.filter_buttons["All"].configure(fg_color=self.primary_color, text_color="white")

        self._search_progress = ctk.CTkProgressBar(wrapper, mode="indeterminate",
                                                    fg_color=self.entry_border,
                                                    progress_color=self.primary_color)
        self._search_error = ctk.CTkLabel(wrapper, text="",
                                           font=self.body_light_font,
                                           text_color=self.error_red)

        self.main_content_frame = ctk.CTkScrollableFrame(wrapper, fg_color="transparent")
        self.main_content_frame.pack(fill="both", expand=True)

        self.cards_grid_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.cards_grid_frame.pack(fill="x")
        self.cards_grid_frame.bind("<Configure>", lambda e: self._update_scroll_region())

        self._dashboard_offset = 0
        self._dashboard_limit = 20
        self.cards_list = []

        self.load_more_btn = ctk.CTkButton(self.main_content_frame, text="Load More",
                                           font=self.body_paragraph_font,
                                           fg_color=self.primary_color,
                                           hover_color=self.hover_color,
                                           text_color="white", width=200, height=40,
                                           command=self._load_more)
        self.load_more_btn.pack(pady=(20, 0))

        self._load_more_error = ctk.CTkLabel(self.main_content_frame, text="",
                                              font=self.body_light_font,
                                              text_color=self.text_color)
        self._load_more_error.pack(pady=(4, 0))

        self.main_content_frame.bind("<Configure>", self.reflow_cards)
        self.after(100, self.reflow_cards)

        self._load_initial_dashboard()
        self._fetch_dashboard_stats()

    # ── Bookings Content (in-page) ─────────────────────────────────

    def show_tenant_bookings_content(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_active_sidebar_btn("bookings")

        container = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(container, text="MY BOOKINGS", font=self.alt_title_font,
                     text_color=self.text_color).pack(pady=(0, 20))

        self._loading_bookings_label = ctk.CTkLabel(container, text="Loading...",
                                                     font=self.body_paragraph_font,
                                                     text_color=self.text_color)
        self._loading_bookings_label.pack(pady=40)

        self._bookings_container = container
        self._bookings_scroll = None

        user_id = getattr(self, 'current_user', {}).get('user_id')

        def _do():
            bookings = []
            try:
                resp = self.api.get(f"/bookings/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    bookings = resp.json()
            except Exception:
                pass
            self.after(0, lambda: self._populate_tenant_bookings(bookings))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_tenant_bookings(self, bookings):
        if hasattr(self, '_loading_bookings_label') and self._loading_bookings_label:
            self._loading_bookings_label.destroy()
            self._loading_bookings_label = None

        container = self._bookings_container

        if not bookings:
            ctk.CTkLabel(container, text="You have no bookings yet.",
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(pady=40)
            return

        if self._bookings_scroll:
            self._bookings_scroll.destroy()

        self._bookings_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self._bookings_scroll.pack(fill="both", expand=True)

        for b in bookings:
            card = ctk.CTkFrame(self._bookings_scroll, fg_color=self.secondary_color,
                                corner_radius=8, border_width=1,
                                border_color=self.entry_border)
            card.pack(fill="x", pady=5, padx=10)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=12)

            ctk.CTkLabel(info_frame,
                         text=f"Booking #{b.get('booking_id')} — Room #{b.get('room_id')}",
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(anchor="w")

            dates = f"{b.get('check_in', '?')} → {b.get('check_out', '?')}"
            if b.get("total_price") is not None:
                dates += f"  |  P{b['total_price']}"
            ctk.CTkLabel(info_frame, text=dates,
                         font=self.body_light_font,
                         text_color=self.text_color).pack(anchor="w")

            status = b.get("status", "unknown")
            color = self.STATUS_COLORS.get(status, ("#757575", "#9E9E9E"))
            badge = ctk.CTkLabel(info_frame, text=status.title(),
                                 fg_color=color, text_color="white",
                                 corner_radius=4,
                                 font=ctk.CTkFont(size=11, weight="bold"),
                                 width=60)
            badge.pack(anchor="w", pady=(4, 0))

            if b.get("status") == "pending":
                cancel_btn = ctk.CTkButton(card, text="Cancel Booking",
                                           fg_color=self.error_red,
                                           hover_color="#c9302c",
                                           text_color="white",
                                           font=self.body_paragraph_font,
                                           width=120, height=32,
                                           command=lambda bid=b.get("booking_id"): self._cancel_booking(bid))
                cancel_btn.pack(side="right", padx=15, pady=8)

    # ── Favorites Content ──────────────────────────────────────────

    def show_tenant_favorites_content(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_active_sidebar_btn("favorite")

        container = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(container, text="SAVED FAVORITES", font=self.alt_title_font,
                     text_color=self.text_color).pack(pady=(0, 20))

        loading = ctk.CTkLabel(container, text="Loading...",
                                font=self.body_paragraph_font,
                                text_color=self.text_color)
        loading.pack(pady=40)

        user_id = getattr(self, 'current_user', {}).get('user_id')

        def _do():
            items = []
            try:
                resp = self.api.get(f"/favorites/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    items = resp.json()
            except Exception:
                pass
            self.after(0, lambda: self._populate_favorites(container, loading, items))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_favorites(self, container, loading, items):
        loading.destroy()

        if not items:
            ctk.CTkLabel(container, text="You have no saved favorites yet.",
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for fav in items:
            card = ctk.CTkFrame(scroll, fg_color=self.secondary_color,
                                corner_radius=8, height=50,
                                border_width=1, border_color=self.entry_border)
            card.pack(fill="x", pady=3, padx=10)
            card.pack_propagate(False)

            listing_id = fav.get("listing_id", "?")
            saved_at = fav.get("saved_at", "?")[:10] if fav.get("saved_at") else "?"

            ctk.CTkLabel(card, text=f"Listing #{listing_id}",
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=15)

            ctk.CTkLabel(card, text=f"Saved: {saved_at}",
                         font=self.body_light_font,
                         text_color=self.text_color).pack(side="left", padx=15)

    # ── Viewing Content (60/40 split) ──────────────────────────────

    def show_tenant_viewings_content(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_active_sidebar_btn("viewing")

        self._viewings_progress = ctk.CTkProgressBar(self.content_wrapper, mode="indeterminate",
                                                      fg_color=self.entry_border,
                                                      progress_color=self.primary_color)
        self._viewings_progress.pack(fill="x", pady=(0, 10))
        self._viewings_progress.start()

        main = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        main.pack(fill="both", expand=True)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=6, uniform="viewsplit")
        main.grid_columnconfigure(1, weight=4, uniform="viewsplit")
        self._viewing_main = main

        self._viewing_left = ctk.CTkFrame(main, fg_color="transparent")
        self._viewing_left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self._viewing_left.grid_columnconfigure(0, weight=1)

        self._viewing_right = ctk.CTkFrame(main, fg_color="transparent")
        self._viewing_right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self._viewing_right.grid_columnconfigure(0, weight=1)

        self._viewing_year = datetime.now().year
        self._viewing_month = datetime.now().month
        self._user_viewings = []
        self._selected_date = None
        self._prop_listing_id = None

        self._render_calendar_viewings()

    def _render_calendar_viewings(self):
        user_id = getattr(self, 'current_user', {}).get('user_id')

        def _do():
            viewings = []
            try:
                resp = self.api.get(f"/viewings/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    viewings = resp.json()
            except Exception:
                pass
            self.after(0, lambda: self._on_viewings_fetched(viewings))

        threading.Thread(target=_do, daemon=True).start()

    def _on_viewings_fetched(self, viewings):
        if hasattr(self, '_viewings_progress') and self._viewings_progress:
            self._viewings_progress.stop()
            self._viewings_progress.pack_forget()
            self._viewings_progress = None

        self._user_viewings = viewings
        if not viewings:
            self._show_viewings_empty_state()
        else:
            if hasattr(self, '_viewings_overlay') and self._viewings_overlay:
                try:
                    self._viewings_overlay.destroy()
                except Exception:
                    pass
                self._viewings_overlay = None
            self._build_property_panel(self._viewing_right)
            self._build_calendar_grid(self._viewing_left, self._viewing_year, self._viewing_month)

    def _show_viewings_empty_state(self):
        if hasattr(self, '_viewings_overlay') and self._viewings_overlay:
            try:
                self._viewings_overlay.destroy()
            except Exception:
                pass

        overlay = ctk.CTkFrame(self._viewing_main, fg_color="transparent")
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.lift()
        self._viewings_overlay = overlay

        overlay.grid_rowconfigure(0, weight=1)
        overlay.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(overlay, fg_color=self.secondary_color,
                            corner_radius=12, border_width=1,
                            border_color=self.entry_border, width=300, height=260)
        card.grid(row=0, column=0)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="📋", font=ctk.CTkFont(size=36)).pack(pady=(35, 8))

        ctk.CTkLabel(card, text="No viewings yet",
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack()

        ctk.CTkLabel(card, text="Browse available listings to\nschedule your first viewing.",
                     font=self.body_paragraph_font,
                     text_color=self.text_color,
                     justify="center").pack(pady=(4, 20))

        ctk.CTkButton(card, text="Browse Listings",
                      font=self.body_paragraph_font,
                      fg_color=self.primary_color,
                      hover_color=self.hover_color,
                      width=160, height=38,
                      command=self.show_tenant_explore_content).pack()

    def _build_calendar_grid(self, parent, year, month):
        for w in parent.winfo_children():
            w.destroy()

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkButton(header, text="◀", width=40, height=32,
                      fg_color=self.secondary_color,
                      text_color=self.text_color,
                      hover_color=self.hover_color,
                      font=ctk.CTkFont(size=16),
                      command=self._prev_month).pack(side="left", padx=(0, 10))

        month_name = calendar.month_name[month]
        ctk.CTkLabel(header, text=f"{month_name} {year}",
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(side="left", expand=True)

        ctk.CTkButton(header, text="▶", width=40, height=32,
                      fg_color=self.secondary_color,
                      text_color=self.text_color,
                      hover_color=self.hover_color,
                      font=ctk.CTkFont(size=16),
                      command=self._next_month).pack(side="right", padx=(10, 0))

        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.grid(row=1, column=0, sticky="ew")
        for i in range(7):
            grid.grid_columnconfigure(i, weight=1, uniform="calday")

        days_labels = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, d in enumerate(days_labels):
            ctk.CTkLabel(grid, text=d, font=self.body_light_font,
                         text_color=self.text_color).grid(row=0, column=i, pady=(0, 4))

        cal = calendar.monthcalendar(year, month)
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                cell = ctk.CTkFrame(grid, border_width=1, height=56,
                                    fg_color="transparent",
                                    border_color=self.entry_border,
                                    cursor="hand2")
                cell.grid(row=r + 1, column=c, padx=1, pady=1, sticky="nsew")

                if self._date_has_viewing(year, month, day):
                    cell.configure(fg_color=self.secondary_color)

                ctk.CTkLabel(cell, text=str(day),
                             font=self.body_light_font,
                             text_color=self.text_color).pack(expand=True)

                cell.bind("<Button-1>", lambda e, d=day: self._on_date_selected(date(year, month, d)))

        self._show_date_detail_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self._show_date_detail_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))

    def _date_has_viewing(self, year, month, day):
        for v in self._user_viewings:
            v_date = v.get("scheduled_date", "")
            if isinstance(v_date, str) and v_date[:10] == f"{year:04d}-{month:02d}-{day:02d}":
                return True
        return False

    def _prev_month(self):
        if self._viewing_month == 1:
            self._viewing_month = 12
            self._viewing_year -= 1
        else:
            self._viewing_month -= 1
        self._build_calendar_grid(self._viewing_left, self._viewing_year, self._viewing_month)

    def _next_month(self):
        if self._viewing_month == 12:
            self._viewing_month = 1
            self._viewing_year += 1
        else:
            self._viewing_month += 1
        self._build_calendar_grid(self._viewing_left, self._viewing_year, self._viewing_month)

    def _on_date_selected(self, selected_date):
        self._selected_date = selected_date
        viewings_on_date = []
        for v in self._user_viewings:
            v_date = v.get("scheduled_date", "")
            v_date_str = v_date[:10] if isinstance(v_date, str) else ""
            target = selected_date.isoformat()
            if v_date_str == target:
                viewings_on_date.append(v)

        if viewings_on_date:
            first = viewings_on_date[0]
            self._show_property_for_listing(first.get("listing_id"))

        self._show_date_detail(viewings_on_date)

    def _show_date_detail(self, viewings_on_date):
        for w in self._show_date_detail_frame.winfo_children():
            w.destroy()

        if not viewings_on_date:
            ctk.CTkLabel(self._show_date_detail_frame,
                         text=f"No viewings on {self._selected_date}",
                         font=self.body_light_font,
                         text_color=self.text_color).pack(pady=20)
            return

        ctk.CTkLabel(self._show_date_detail_frame,
                     text=f"Viewings on {self._selected_date}",
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 8))

        for v in viewings_on_date:
            card = ctk.CTkFrame(self._show_date_detail_frame,
                                fg_color=self.secondary_color,
                                corner_radius=6, border_width=1,
                                border_color=self.entry_border)
            card.pack(fill="x", pady=3)
            card.pack_propagate(False)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            time_str = str(v.get("scheduled_time", ""))[:5] if v.get("scheduled_time") else "All day"
            listing_id = v.get("listing_id", "?")
            ctk.CTkLabel(info, text=f"Listing #{listing_id} — {time_str}",
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(anchor="w")

            status = v.get("status", "pending")
            color = self.STATUS_COLORS.get(status, ("#757575", "#9E9E9E"))
            badge = ctk.CTkLabel(info, text=status.title(),
                                 fg_color=color, text_color="white",
                                 corner_radius=4,
                                 font=ctk.CTkFont(size=10, weight="bold"),
                                 width=60)
            badge.pack(anchor="w", pady=(2, 0))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=(0, 10))

            ctk.CTkButton(btn_frame, text="View Property",
                          font=self.body_description_font,
                          width=80, height=28,
                          fg_color=self.primary_color,
                          command=lambda lid=listing_id: self._show_property_for_listing(lid)).pack(side="top", pady=(8, 2))

            if status in ("pending", "confirmed"):
                ctk.CTkButton(btn_frame, text="Cancel",
                              font=self.body_description_font,
                              width=60, height=24,
                              fg_color=self.error_red,
                              command=lambda vid=v.get("viewing_id"): self._cancel_viewing(vid)).pack(side="bottom", pady=(0, 6))

    def _cancel_viewing(self, viewing_id):
        def _do():
            try:
                resp = self.api.patch(f"/viewings/{viewing_id}/status",
                                      json={"status": "cancelled"}, timeout=5)
                if resp.status_code == 200:
                    self.after(0, lambda: self._viewing_cancel_done())
                else:
                    err = resp.json().get("detail", "Failed to cancel")
                    self.after(0, lambda: self.show_toast(err, is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def _viewing_cancel_done(self):
        self.show_toast("Viewing cancelled!", is_error=False)
        self.show_tenant_viewings_content()

    def _build_property_panel(self, parent):
        for w in parent.winfo_children():
            w.destroy()

        self._prop_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self._prop_scroll.pack(fill="both", expand=True)

        self._prop_image = ctk.CTkLabel(self._prop_scroll, text="", height=180,
                                        fg_color=self.secondary_color, corner_radius=6)
        self._prop_image.pack(fill="x", pady=(0, 10))

        self._prop_name = ctk.CTkLabel(self._prop_scroll, text="Select a date",
                                       font=self.body_bold_paragraph_font,
                                       text_color=self.text_color)
        self._prop_name.pack(anchor="w")

        self._prop_location = ctk.CTkLabel(self._prop_scroll, text="",
                                           font=self.body_light_font,
                                           text_color=self.text_color)
        self._prop_location.pack(anchor="w")

        self._prop_price = ctk.CTkLabel(self._prop_scroll, text="",
                                        font=self.body_paragraph_font,
                                        text_color=self.primary_color)
        self._prop_price.pack(anchor="w", pady=(4, 0))

        self._prop_rating_frame = ctk.CTkFrame(self._prop_scroll, fg_color="transparent")
        self._prop_rating_frame.pack(anchor="w", pady=(4, 0))

        self._prop_desc = ctk.CTkLabel(self._prop_scroll, text="",
                                       font=self.body_light_font,
                                       text_color=self.text_color, wraplength=280)
        self._prop_desc.pack(anchor="w", pady=(8, 0))

        self._prop_amenities_label = ctk.CTkLabel(self._prop_scroll, text="",
                                                  font=self.body_light_font,
                                                  text_color=self.text_color, wraplength=280)
        self._prop_amenities_label.pack(anchor="w", pady=(4, 0))

        self._prop_reviews_label = ctk.CTkLabel(self._prop_scroll, text="",
                                                font=self.body_light_font,
                                                text_color=self.text_color, wraplength=280)
        self._prop_reviews_label.pack(anchor="w", pady=(8, 0))

        self._prop_schedule_btn = ctk.CTkButton(self._prop_scroll, text="Schedule Viewing",
                                                 font=self.body_paragraph_font,
                                                 fg_color=self.primary_color,
                                                 height=36,
                                                 state="disabled")
        self._prop_schedule_btn.pack(fill="x", pady=(10, 0))

    def _show_property_for_listing(self, listing_id):
        self._prop_listing_id = listing_id

        def _do():
            listing_data = None
            reviews_data = []
            photos_data = []
            try:
                resp = self.api.get(f"/boarding-houses/{listing_id}", timeout=5)
                if resp.status_code == 200:
                    listing_data = resp.json()
            except Exception:
                pass
            try:
                resp = self.api.get(f"/boarding-houses/{listing_id}/reviews", timeout=5)
                if resp.status_code == 200:
                    reviews_data = resp.json()
            except Exception:
                pass
            try:
                resp = self.api.get(f"/photos/listing/{listing_id}", timeout=5)
                if resp.status_code == 200:
                    photos_data = resp.json()
            except Exception:
                pass
            self.after(0, lambda: self._populate_property_panel(listing_data, reviews_data, photos_data))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_property_panel(self, listing, reviews, photos):
        if not listing:
            self._prop_name.configure(text="Property not found")
            return

        self._prop_name.configure(text=listing.get("bh_name", "Unknown"))
        self._prop_location.configure(text=listing.get("location", ""))
        price = listing.get("price_range", "")
        self._prop_price.configure(text=f"P{price}" if price else "")
        self._prop_desc.configure(text=listing.get("description", ""))

        rating_text = f"Rating: {listing.get('rating', 'N/A')} / 5"
        self._prop_rating_frame.configure(text=rating_text) if hasattr(self._prop_rating_frame, 'configure') else None

        amenities = listing.get("amenities", "")
        self._prop_amenities_label.configure(text=f"Amenities: {amenities}" if amenities else "")

        if reviews:
            review_lines = []
            for r in reviews[:3]:
                reviewer = r.get("reviewer_name", "Anonymous")
                comment = r.get("review_text", "")
                rating = r.get("rating", "")
                review_lines.append(f"  ★{rating} — {reviewer}: {comment[:80]}")
            self._prop_reviews_label.configure(text="Reviews:\n" + "\n".join(review_lines))
        else:
            self._prop_reviews_label.configure(text="No reviews yet")

        if photos:
            photo_url = photos[0].get("photo_url", "")
            if photo_url:
                def load_main():
                    try:
                        img_data = requests.get(photo_url, timeout=3).content
                        pil_image = Image.open(io.BytesIO(img_data))
                        ctk_image = ctk.CTkImage(pil_image, size=(280, 180))
                        self._prop_image.configure(image=ctk_image, text="")
                    except Exception:
                        self._prop_image.configure(text="[Image]")
                threading.Thread(target=load_main, daemon=True).start()
        else:
            self._prop_image.configure(text="[No Image]")

        lid = listing.get("listing_id") or listing.get("id")
        self._prop_schedule_btn.configure(
            state="normal",
            command=lambda: self._schedule_viewing(lid)
        )

    # ── Schedule Viewing ───────────────────────────────────────────

    def _schedule_viewing(self, listing_id):
        if hasattr(self, '_schedule_overlay') and self._schedule_overlay:
            try:
                self._schedule_overlay.destroy()
            except Exception:
                pass

        overlay = ctk.CTkFrame(self.content_wrapper, fg_color="#00000080")
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.lift()
        self._schedule_overlay = overlay

        card = ctk.CTkFrame(overlay, fg_color=self.secondary_color,
                            corner_radius=12, border_width=1,
                            border_color=self.entry_border, width=350, height=280)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="Schedule a Viewing",
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(pady=(20, 8))

        ctk.CTkLabel(card, text="Pick a date:",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(pady=(0, 10))

        date_frame = ctk.CTkFrame(card, fg_color="transparent")
        date_frame.pack(pady=(0, 10))

        today = date.today()
        self._schedule_selected_date = today
        self._schedule_date_buttons = []

        for i in range(7):
            d = today + timedelta(days=i)
            label = "Today" if i == 0 else ("Tomorrow" if i == 1 else d.strftime("%a %d"))
            btn = ctk.CTkButton(date_frame, text=label,
                                font=self.body_description_font,
                                width=80, height=32,
                                fg_color=self.primary_color if i == 0 else self.secondary_color,
                                text_color="white" if i == 0 else self.text_color,
                                hover_color=self.hover_color,
                                command=lambda day=d, idx=i: self._pick_schedule_date(day, idx))
            btn.pack(side="left", padx=3)
            self._schedule_date_buttons.append(btn)

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(10, 15))

        ctk.CTkButton(btn_row, text="Cancel",
                      font=self.body_paragraph_font,
                      fg_color="transparent",
                      text_color=self.text_color,
                      hover_color=self.hover_color,
                      command=self._close_schedule_overlay).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btn_row, text="Confirm",
                      font=self.body_paragraph_font,
                      fg_color=self.primary_color,
                      text_color="white",
                      command=lambda: self._confirm_schedule(listing_id)).pack(side="right")

    def _pick_schedule_date(self, day, idx):
        self._schedule_selected_date = day
        for i, btn in enumerate(self._schedule_date_buttons):
            if i == idx:
                btn.configure(fg_color=self.primary_color, text_color="white")
            else:
                btn.configure(fg_color=self.secondary_color, text_color=self.text_color)

    def _close_schedule_overlay(self):
        if hasattr(self, '_schedule_overlay') and self._schedule_overlay:
            try:
                self._schedule_overlay.destroy()
            except Exception:
                pass
            self._schedule_overlay = None

    def _confirm_schedule(self, listing_id):
        selected = self._schedule_selected_date
        if not selected:
            self.show_toast("Please select a date", is_error=True)
            return

        def _do():
            try:
                resp = self.api.post("/viewings/", json={
                    "listing_id": listing_id,
                    "scheduled_date": selected.isoformat(),
                }, timeout=5)
                if resp.status_code == 201:
                    self.after(0, lambda: self._schedule_done())
                else:
                    err = resp.json().get("detail", "Failed to schedule viewing")
                    self.after(0, lambda: self.show_toast(err, is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def _schedule_done(self):
        self._close_schedule_overlay()
        self.show_toast("Viewing scheduled!", is_error=False)
        self.show_tenant_viewings_content()

    # ── Debug ──────────────────────────────────────────────────────

    def _debug_widget(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget:
            info = f"{widget.__class__.__name__}"
            parent = widget.master
            if parent:
                info += f" <- {parent.__class__.__name__}"
            try:
                txt = widget.cget("text") if hasattr(widget, "cget") else ""
                if txt:
                    info += f" text='{txt[:40]}'"
            except Exception:
                pass
            geom = f"x={event.x_root} y={event.y_root}"
            print(f"[DEBUG] {geom} | {info}")

    # ── Animation ──────────────────────────────────────────────────

    def animate_sidebar(self):
        current_width = self.sidebar_main_frame.cget("width")

        if self.is_sidebar_expanded:
            if current_width > 0:
                new_width = max(0, current_width - 20)
                self.sidebar_main_frame.configure(width=new_width)
                self.content_wrapper.pack_configure(padx=(new_width + 10, 10))
                self.after(10, self.animate_sidebar)
            else:
                self.sidebar_main_frame.place_forget()
                self.is_sidebar_expanded = False
                if hasattr(self, 'reflow_cards'):
                    self.reflow_cards()
        else:
            if not self.sidebar_main_frame.winfo_ismapped():
                self.sidebar_main_frame.place(x=0, y=0, relheight=1.0)
            if current_width < 250:
                new_width = min(250, current_width + 20)
                self.sidebar_main_frame.configure(width=new_width)
                self.content_wrapper.pack_configure(padx=(new_width + 10, 10))
                self.after(10, self.animate_sidebar)
            else:
                self.is_sidebar_expanded = True
                if hasattr(self, 'reflow_cards'):
                    self.reflow_cards()

    def animate_search_bar(self):
        current_width = self.search_bg_frame.cget("width")
        target_width = 800

        if not self.is_search_expanded:
            self.search_bg_frame.configure(fg_color=self.fg_color)

            if current_width < target_width:
                self.search_bg_frame.configure(width=min(target_width, current_width + 40))
                self.after(10, self.animate_search_bar)
            else:
                self.is_search_expanded = True
                self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 15))
                self.search_entry.focus()
        else:
            self.search_entry.pack_forget()
            if current_width > 40:
                self.search_bg_frame.configure(width=max(40, current_width - 40))
                self.after(10, self.animate_search_bar)
            else:
                self.search_bg_frame.configure(fg_color="transparent")
                self.is_search_expanded = False

    # ── Listing Cards ──────────────────────────────────────────────

    def create_listing_card(self, parent_frame, house_data):
        card = ctk.CTkFrame(parent_frame,
                            width=400, height=450,
                            fg_color=self.secondary_color,
                            corner_radius=12,
                            border_width=1, border_color=self.entry_border)
        card.pack_propagate(False)

        photo_url = house_data.get("photo_url")
        if photo_url:
            card_img = ctk.CTkLabel(card, text="", width=380, height=200,
                                    fg_color=self.fg_color, corner_radius=6)

            def load_image():
                try:
                    img_data = requests.get(photo_url, timeout=3).content
                    pil_image = Image.open(io.BytesIO(img_data))
                    ctk_image = ctk.CTkImage(pil_image, size=(380, 200))
                    self.after(0, lambda: card_img.configure(image=ctk_image))
                except Exception:
                    self.after(0, lambda: card_img.configure(text="[ Image Unavailable ]",
                                                             text_color=self.text_color))

            threading.Thread(target=load_image, daemon=True).start()
        else:
            card_img = ctk.CTkLabel(card, text="[ No Image ]", width=380, height=200,
                                    fg_color=self.fg_color, text_color=self.text_color,
                                    corner_radius=6)
        card_img.pack(pady=(10, 0), padx=5)

        card_name = ctk.CTkLabel(card, text=house_data["name"],
                                 font=self.body_bold_paragraph_font,
                                 text_color=self.text_color)
        card_name.pack(anchor="w", padx=15, pady=(10, 0))

        card_location = ctk.CTkLabel(card, text=house_data["location"],
                                     font=self.body_paragraph_font,
                                     text_color=self.text_color)
        card_location.pack(anchor="w", padx=15)

        card_amenities = ctk.CTkLabel(card, text=house_data["amenities"],
                                      font=self.body_paragraph_font,
                                      text_color=self.text_color)
        card_amenities.pack(anchor="w", padx=15)

        card_title = ctk.CTkLabel(card, text="Description",
                                  font=self.body_description_font,
                                  text_color=self.text_color)
        card_title.pack(anchor="w", padx=15, pady=(0, 5))

        card_bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
        card_bottom_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        listing_id = house_data.get("id")
        schedule_btn = ctk.CTkButton(card_bottom_frame, text="Schedule",
                                     font=self.body_description_font,
                                     width=70, height=25,
                                     fg_color=self.primary_color,
                                     command=lambda lid=listing_id: self._schedule_viewing(lid))
        schedule_btn.pack(side="left", padx=(0, 5))
        bookmark_btn = ctk.CTkButton(card_bottom_frame, text=None,
                                     image=self.bookmark_icon,
                                     width=25, height=25,
                                     fg_color="transparent",
                                     hover_color=self.hover_color,
                                     command=lambda lid=listing_id: self.toggle_bookmark(lid))
        bookmark_btn.pack(side="right")

        return card

    def reflow_cards(self, event=None):
        if not hasattr(self, 'main_content_frame'):
            return
        available_width = self.main_content_frame.winfo_width()
        if available_width <= 0:
            available_width = 800

        card_total_width = 440
        columns = max(1, available_width // card_total_width)

        if self.cards_list:
            columns = min(columns, len(self.cards_list))

        if (columns == getattr(self, "current_columns", None) and
            self.cards_list and
            all(card.winfo_manager() == "grid" for card in self.cards_list)):
            return

        self.current_columns = columns
        for index, card in enumerate(self.cards_list):
            row = index // columns
            col = index % columns
            card.grid(row=row, column=col, padx=20, pady=20)

        self.cards_grid_frame.update_idletasks()
        self._update_scroll_region()

    def _update_scroll_region(self):
        canvas = getattr(self.main_content_frame, "_parent_canvas", None)
        if canvas:
            try:
                canvas.configure(scrollregion=canvas.bbox("all"))
            except Exception:
                pass

    def _load_initial_dashboard(self):
        self._explore_progress = ctk.CTkProgressBar(self.cards_grid_frame, mode="indeterminate",
                                                     fg_color=self.entry_border,
                                                     progress_color=self.primary_color)
        self._explore_progress.pack(fill="x", padx=20, pady=20)
        self._explore_progress.start()

        def _do():
            try:
                response = self.api.get(
                    f"/boarding-houses/feed/dashboard?offset=0&limit={self._dashboard_limit}")
                if response.status_code == 200:
                    houses = response.json()
                    logger.info("Successfully loaded %d houses from the database!", len(houses))
                    self.after(0, lambda: self._populate_initial_cards(houses))
                else:
                    logger.warning("Backend error %s: %s", response.status_code, response.text)
                    self.after(0, lambda: self._show_dashboard_error(
                        "Something went wrong while loading listings. Please try again."))
            except (requests.ConnectionError, requests.Timeout):
                logger.warning("Backend is offline!")
                self.after(0, lambda: self._show_dashboard_error(
                    "Can't connect to the server right now. Check your connection and try again."))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_initial_cards(self, houses):
        if hasattr(self, '_explore_progress') and self._explore_progress:
            self._explore_progress.stop()
            self._explore_progress.pack_forget()
            self._explore_progress = None
        if hasattr(self, '_error_frame') and self._error_frame:
            self._error_frame.destroy()
            self._error_frame = None
        if not houses:
            return
        for house_data in houses:
            card_widget = self.create_listing_card(self.cards_grid_frame, house_data)
            self.cards_list.append(card_widget)
        self.reflow_cards()

    def _show_dashboard_error(self, message="Could not load listings"):
        if hasattr(self, '_explore_progress') and self._explore_progress:
            self._explore_progress.stop()
            self._explore_progress.pack_forget()
            self._explore_progress = None
        if hasattr(self, '_error_frame') and self._error_frame:
            self._error_frame.destroy()
            self._error_frame = None
        for card in self.cards_list:
            card.destroy()
        self.cards_list = []
        self._error_frame = ctk.CTkFrame(self.cards_grid_frame,
                                          fg_color=self.secondary_color,
                                          corner_radius=10, height=170,
                                          border_width=1, border_color=self.entry_border)
        self._error_frame.pack(fill="x", padx=20, pady=30)
        self._error_frame.pack_propagate(False)

        ctk.CTkLabel(self._error_frame, text="Oops!",
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(pady=(20, 0))
        ctk.CTkLabel(self._error_frame, text=message,
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(pady=(4, 8))
        ctk.CTkButton(self._error_frame, text="Try Again",
                       font=self.body_paragraph_font,
                       fg_color=self.primary_color,
                       hover_color=self.hover_color,
                       text_color="white",
                       width=120, height=40,
                       command=self._load_initial_dashboard).pack(pady=(0, 18))

    def _load_more(self):
        self._dashboard_offset += self._dashboard_limit
        self.load_more_btn.configure(state="disabled", text="Loading...")

        def _do():
            try:
                resp = self.api.get(
                    f"/boarding-houses/feed/dashboard?offset={self._dashboard_offset}&limit={self._dashboard_limit}",
                    timeout=10)
                if resp.status_code == 200:
                    houses = resp.json()
                    if not houses:
                        self._dashboard_offset -= self._dashboard_limit
                        self.after(0, lambda: self._load_more_done("No more listings", is_error=False))
                        return
                    self.after(0, lambda: self._append_cards(houses))
                else:
                    self._dashboard_offset -= self._dashboard_limit
                    self.after(0, lambda: self._load_more_done("Failed to load more"))
            except Exception:
                self._dashboard_offset -= self._dashboard_limit
                self.after(0, lambda: self._load_more_done("Failed to load more"))

        threading.Thread(target=_do, daemon=True).start()

    def _append_cards(self, houses):
        for house_data in houses:
            card_widget = self.create_listing_card(self.cards_grid_frame, house_data)
            self.cards_list.append(card_widget)
        self.reflow_cards()
        self.load_more_btn.configure(state="normal", text="Load More")

    def _load_more_done(self, msg, is_error=True):
        self.load_more_btn.configure(state="normal", text="Load More")
        if is_error:
            self._load_more_error.configure(text=msg, text_color=self.error_red)
            self.after(4000, lambda: self._load_more_error.configure(text=""))
        else:
            self._load_more_error.configure(text=msg, text_color=self.text_color)
            self.after(2000, lambda: self._load_more_error.configure(text=""))

    def _do_search(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        self.search_btn.configure(state="disabled")
        self._search_progress.pack(fill="x", padx=20, pady=(0, 10))
        self._search_progress.start()
        self._search_error.configure(text="")

        def _do():
            try:
                resp = self.api.get(f"/search/?q={query}", timeout=10)
                if resp.status_code == 200:
                    results = resp.json()
                    self.after(0, lambda: self._rebuild_cards(results))
                else:
                    self.after(0, lambda: self._search_error.configure(
                        text="Search failed — try a different query"))
            except Exception:
                self.after(0, lambda: self._search_error.configure(
                    text="Cannot connect to server"))
            finally:
                self.after(0, lambda: self._search_done())

        threading.Thread(target=_do, daemon=True).start()

    def _search_done(self):
        self._search_progress.stop()
        self._search_progress.pack_forget()
        self.search_btn.configure(state="normal")

    def toggle_filter(self, selected_filter):
        for name, btn in self.filter_buttons.items():
            btn.configure(fg_color=self.secondary_color, text_color=self.text_color)

        self.filter_buttons[selected_filter].configure(fg_color=self.primary_color,
                                                       text_color="white")

        if selected_filter == "All":
            self._load_initial_dashboard()
            return

        def _do():
            if not hasattr(self, "_amenity_map"):
                try:
                    resp = self.api.get("/amenities")
                    if resp.status_code == 200:
                        self._amenity_map = {a["amenity_name"]: a["amenity_id"]
                                             for a in resp.json()}
                except Exception:
                    self._amenity_map = {}

            amenity_id = self._amenity_map.get(selected_filter)
            if not amenity_id:
                self.after(0, lambda: self.show_toast(
                    "Could not load filter options", is_error=True))
                return

            try:
                resp = self.api.get(f"/search/?amenity_ids={amenity_id}")
                if resp.status_code == 200:
                    results = resp.json()
                    self.after(0, lambda: self._rebuild_cards(results))
                else:
                    self.after(0, lambda: self.show_toast(
                        "Filter failed — try again", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast(
                    "Cannot connect to server", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def toggle_bookmark(self, listing_id):
        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            self.show_toast("Please log in to bookmark listings", is_error=True)
            return

        def _do():
            try:
                resp = self.api.post("/favorites/toggle",
                                     json={"user_id": user_id, "listing_id": listing_id})
                if resp.status_code == 200:
                    action = resp.json().get("action", "")
                    self.after(0, lambda: self.show_toast(f"Bookmark {action}!", is_error=False))
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to toggle bookmark", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def _rebuild_cards(self, houses):
        if hasattr(self, '_error_frame') and self._error_frame:
            return
        for card in self.cards_list:
            card.destroy()
        self.cards_list = []
        if hasattr(self, '_empty_state') and self._empty_state:
            self._empty_state.destroy()
            self._empty_state = None
        if not houses:
            self._empty_state = ctk.CTkFrame(self.cards_grid_frame,
                                              fg_color=self.secondary_color,
                                              corner_radius=10, height=150,
                                              border_width=1,
                                              border_color=self.entry_border)
            self._empty_state.pack(fill="x", padx=20, pady=30)
            self._empty_state.pack_propagate(False)
            ctk.CTkLabel(self._empty_state, text="No listings found",
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(pady=(20, 0))
            ctk.CTkLabel(self._empty_state, text="Try adjusting your filters or search query",
                         font=self.body_light_font,
                         text_color=self.text_color).pack(pady=(4, 8))
            browse_btn = ctk.CTkButton(self._empty_state, text="Browse All",
                                       font=self.body_paragraph_font,
                                       fg_color=self.primary_color,
                                       hover_color=self.hover_color,
                                       text_color="white",
                                       width=120, height=40)
            browse_btn.configure(command=lambda: self._reset_to_all())
            browse_btn.pack(pady=(0, 18))
            return
        for house_data in houses:
            card_widget = self.create_listing_card(self.cards_grid_frame, house_data)
            self.cards_list.append(card_widget)
        self.reflow_cards()

    def _reset_to_all(self):
        if hasattr(self, 'filter_buttons') and "All" in self.filter_buttons:
            self.toggle_filter("All")
        self._load_initial_dashboard()

    # ── Cancel Booking ─────────────────────────────────────────────

    def _cancel_booking(self, booking_id):
        def _do():
            try:
                resp = self.api.patch(f"/bookings/{booking_id}/status", json={
                    "status": "cancelled"
                }, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self._cancel_done())
                else:
                    err = resp.json().get("detail", "Failed to cancel")
                    self.after(0, lambda: self.show_toast(err, is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def _cancel_done(self):
        self.show_toast("Booking cancelled!", is_error=False)
        self.show_tenant_bookings_content()

    # ── Notification Badge ─────────────────────────────────────────

    def _fetch_notif_count(self):
        user_id = getattr(self, 'current_user', {}).get('user_id')
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
            self.after(0, lambda: self._update_notif_badge(unread))

        threading.Thread(target=_do, daemon=True).start()

    def _update_notif_badge(self, count):
        if count > 0:
            self.notif_badge.configure(text=str(count) if count <= 99 else "99+")
        else:
            self.notif_badge.configure(text="")

    # ── User Menu ──────────────────────────────────────────────────

    def _toggle_user_menu(self):
        if hasattr(self, '_user_menu') and self._user_menu and self._user_menu.winfo_ismapped():
            self._hide_user_menu()
        else:
            self._show_user_menu(
                parent=self.form_container,
                anchor=self.profile_frame,
                form_container=self.form_container,
                items=[
                    ("Account Settings", self.menu_profile_icon,  self.show_account_settings),
                    None,
                    ("My Bookings",    self.menu_bookings_icon, self.show_tenant_bookings_content),
                    ("Notifications",  self.notification_icon,  self.show_notifications_page),
                    None,
                    ("Logout",         self.menu_logout_icon,   self._handle_logout),
                ],
            )
            if hasattr(self, 'profile_chevron'):
                self.profile_chevron.configure(text="▴")

    # ── Dashboard Stats (Explore) ──────────────────────────────────

    def _fetch_dashboard_stats(self):
        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            return

        def _do():
            bookings_count = "0"
            favorites_count = "0"
            try:
                resp = self.api.get(f"/bookings/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    bookings = resp.json()
                    bookings_count = str(len(bookings))
            except Exception:
                pass
            try:
                resp = self.api.get(f"/favorites/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    favorites = resp.json()
                    favorites_count = str(len(favorites))
            except Exception:
                pass
            self.after(0, lambda: self._update_stat_labels(bookings_count, favorites_count, "0"))

        threading.Thread(target=_do, daemon=True).start()

    def _update_stat_labels(self, bookings, favorites, reviews):
        if hasattr(self, '_stat_labels'):
            if "Active Bookings" in self._stat_labels:
                self._stat_labels["Active Bookings"].configure(text=bookings)
            if "Saved Favorites" in self._stat_labels:
                self._stat_labels["Saved Favorites"].configure(text=favorites)
            if "Total Reviews" in self._stat_labels:
                self._stat_labels["Total Reviews"].configure(text=reviews)
