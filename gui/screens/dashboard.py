import os
import sys
import customtkinter as ctk
import requests
import threading
import calendar
from tkinter import ttk
from PIL import Image
import io
from src.logger import logger
from datetime import datetime, date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote


class DashboardMixin:

    STATUS_COLORS = {
        "completed": ("#2E7D32", "#4CAF50"),
        "pending": ("#E65100", "#FF9800"),
        "failed": ("#C62828", "#EF5350"),
        "refunded": ("#1565C0", "#42A5F5"),
        "active": ("#2E7D32", "#4CAF50"),
        "cancelled": ("#757575", "#9E9E9E"),
        "confirmed": ("#1565C0", "#42A5F5"),
        "approved": ("#1565C0", "#42A5F5"),
        "move_in_requested": ("#00897B", "#26A69A"),
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

        self.body_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True)

        self._build_tenant_sidebar()

        self.content_wrapper = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.content_wrapper.pack(side="left", fill="both", expand=True, padx=(10, 10), pady=20)

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
                                    width=32, height=32, cursor="hand2")
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

        self.profile_frame.configure(cursor="hand2")

    # ── Sidebar ────────────────────────────────────────────────────

    def _build_tenant_sidebar(self):
        self.sidebar_main_frame = ctk.CTkFrame(self.body_frame,
                                               fg_color="transparent",
                                               width=250, corner_radius=0,
                                               border_color=self.entry_border,
                                               border_width=1)
        self.sidebar_main_frame.pack(side="left", fill="y")
        self.sidebar_main_frame.pack_propagate(False)

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
        if not user_id:
            self.show_toast("User session not found. Please log in again.", is_error=True)
            return

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
                            self.after(0, lambda k=key: self.show_toast(f"Failed to load {k}. Check your connection.", is_error=True))
            except Exception:
                try:
                    resp = self.api.get(f"/bookings/user/{user_id}", timeout=5)
                    if resp.status_code == 200:
                        bookings = resp.json()
                except Exception:
                    self.after(0, lambda: self.show_toast("Failed to load bookings. Check your connection.", is_error=True))
                try:
                    resp = self.api.get(f"/payments/user/{user_id}", timeout=5)
                    if resp.status_code == 200:
                        payments = resp.json()
                except Exception:
                    self.after(0, lambda: self.show_toast("Failed to load payments. Check your connection.", is_error=True))
                try:
                    resp = self.api.get(f"/favorites/user/{user_id}", timeout=5)
                    if resp.status_code == 200:
                        favorites = resp.json()
                except Exception:
                    self.after(0, lambda: self.show_toast("Failed to load favorites. Check your connection.", is_error=True))

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
        try:
            for w in parent.winfo_children():
                w.destroy()
        except Exception:
            pass

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

            room_info = f"Booking #{b.get('booking_id', '?')} — Room #{b.get('room_id', '?')}"
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
            ("Next Payment", f"P{next_payment.get('amount', '—')}" if next_payment else "—",
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

            ctk.CTkLabel(row, text=f"P{p.get('amount', '—')}",
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

        # Search bar (Explore tab only)
        self.search_bg_frame = ctk.CTkFrame(wrapper,
                                             height=40,
                                             fg_color=self.fg_color,
                                             corner_radius=6)
        self.search_bg_frame.pack(fill="x", pady=(0, 15))

        self.search_entry = ctk.CTkEntry(self.search_bg_frame,
                                         placeholder_text="Search for boarding houses, cities",
                                         font=self.body_light_font,
                                         height=40, border_width=0,
                                         fg_color="transparent")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(15, 5))
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        self.search_btn = ctk.CTkButton(self.search_bg_frame, text=None,
                                        image=self.search_icon,
                                        width=40, height=40,
                                        fg_color="transparent",
                                        hover_color=self.hover_color,
                                        command=self._do_search)
        self.search_btn.pack(side="right", padx=(0, 5))

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
        self._enable_scroll_refresh(self.main_content_frame, self._refresh_explore)

    # ── Bookings Content (in-page) ─────────────────────────────────

    def show_tenant_bookings_content(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_active_sidebar_btn("bookings")

        container = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(container, text="MY BOOKINGS", font=self.alt_title_font,
                     text_color=self.text_color).pack(pady=(0, 20))

        self._show_dash_loading(container)

        self._bookings_container = container
        self._bookings_scroll = None

        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            self.show_toast("User session not found. Please log in again.", is_error=True)
            return

        def _do():
            bookings = []
            try:
                resp = self.api.get(f"/bookings/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    bookings = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load bookings. Check your connection.", is_error=True))
            self.after(0, lambda: self._populate_tenant_bookings(bookings))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_tenant_bookings(self, bookings):
        self._hide_dash_loading()
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
                         text=f"Booking #{b.get('booking_id', '?')} — Room #{b.get('room_id', '?')}",
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(anchor="w")

            dates = f"{b.get('check_in', '?')} → {b.get('check_out', '?')}"
            if b.get("total_price") is not None:
                dates += f"  |  P{b['total_price']}"
            ctk.CTkLabel(info_frame, text=dates,
                         font=self.body_light_font,
                         text_color=self.text_color).pack(anchor="w")

            status = b.get("status", "unknown")
            move_in_req = b.get("move_in_requested", False)
            if move_in_req and status != "active":
                display_badge = "Move-in Requested"
                color = ("#00897B", "#26A69A")
            else:
                display_badge = status.title()
                color = self.STATUS_COLORS.get(status, ("#757575", "#9E9E9E"))
            badge = ctk.CTkLabel(info_frame, text=display_badge,
                                 fg_color=color, text_color="white",
                                 corner_radius=4,
                                 font=ctk.CTkFont(size=11, weight="bold"),
                                 width=60)
            badge.pack(anchor="w", pady=(4, 0))

            if move_in_req and status == "approved":
                ctk.CTkLabel(info_frame,
                             text="Waiting for owner to confirm your move-in",
                             font=self.body_light_font,
                             text_color=self.text_color).pack(anchor="w")

            bid = b.get('booking_id', '?')
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15, pady=8)

            if status in ("pending", "approved"):
                if status == "approved" and not move_in_req:
                    pay_btn = ctk.CTkButton(btn_frame, text="Pay & Request Move-in",
                                            fg_color=self.primary_color,
                                            hover_color=self.hover_color,
                                            text_color="white",
                                            font=ctk.CTkFont(size=16),
                                            width=200, height=32)
                    pay_btn.pack(side="right", padx=(8, 0))
                    total_price = b.get("total_price", 0)
                    pay_btn.configure(command=lambda b=bid, btn=pay_btn, crd=card, tp=total_price: self._show_payment_form(b, crd, btn, tp))

                cancel_btn = ctk.CTkButton(btn_frame, text="Cancel Booking",
                                           fg_color=self.error_red,
                                           hover_color=self.error_red,
                                           text_color="white",
                                           font=self.body_paragraph_font,
                                           width=120, height=32)
                cancel_btn.pack(side="right")
                cancel_btn.configure(command=lambda bid=bid, btn=cancel_btn: self._cancel_booking(bid, btn))

    # ── Favorites Content ──────────────────────────────────────────

    def show_tenant_favorites_content(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_active_sidebar_btn("favorite")

        self._favorites_container = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        self._favorites_container.pack(fill="both", expand=True)

        ctk.CTkLabel(self._favorites_container, text="SAVED FAVORITES", font=self.alt_title_font,
                     text_color=self.text_color).pack(pady=(0, 20))

        self._show_dash_loading(self._favorites_container)

        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            self.show_toast("User session not found. Please log in again.", is_error=True)
            return

        def _do():
            items = []
            try:
                resp = self.api.get(f"/favorites/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    items = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load favorites. Check your connection.", is_error=True))
            self.after(0, lambda: self._show_favorites(items))

        threading.Thread(target=_do, daemon=True).start()

    def _show_favorites(self, items):
        self._hide_dash_loading()
        container = self._favorites_container

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
        if not user_id:
            self.show_toast("User session not found. Please log in again.", is_error=True)
            return

        def _do():
            viewings = []
            try:
                resp = self.api.get(f"/viewings/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    viewings = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load viewings. Check your connection.", is_error=True))
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
                cancel_v_btn = ctk.CTkButton(btn_frame, text="Cancel",
                                             font=self.body_description_font,
                                             width=60, height=24,
                                             fg_color=self.error_red)
                cancel_v_btn.pack(side="bottom", pady=(0, 6))
                vid = v.get("viewing_id")
                cancel_v_btn.configure(command=lambda vid=vid, btn=cancel_v_btn: self._cancel_viewing(vid, btn))

    def _cancel_viewing(self, viewing_id, btn=None):
        dialog = ctk.CTkInputDialog(text="Type CANCEL to confirm cancellation:", title="Cancel Viewing")
        if dialog.get_input() != "CANCEL":
            return

        if btn:
            btn.configure(state="disabled", text="Cancelling...")

        def _do():
            try:
                resp = self.api.patch(f"/viewings/{viewing_id}/status",
                                      json={"status": "cancelled"}, timeout=5)
                if resp.status_code == 200:
                    self.after(0, lambda: self._viewing_cancel_done())
                else:
                    err = resp.json().get("detail", "Failed to cancel")
                    self.after(0, lambda: self.show_toast(err, is_error=True))
                    if btn:
                        self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal", text="Cancel"))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
                if btn:
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal", text="Cancel"))

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
                self.after(0, lambda: self.show_toast("Failed to load property details. Check your connection.", is_error=True))
            try:
                resp = self.api.get(f"/social/reviews/listing/{listing_id}", timeout=5)
                if resp.status_code == 200:
                    reviews_data = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load reviews. Check your connection.", is_error=True))
            try:
                resp = self.api.get(f"/photos/listing/{listing_id}", timeout=5)
                if resp.status_code == 200:
                    photos_data = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load photos. Check your connection.", is_error=True))
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

        self._schedule_confirm_btn = ctk.CTkButton(btn_row, text="Confirm",
                                                    font=self.body_paragraph_font,
                                                    fg_color=self.primary_color,
                                                    text_color="white")
        self._schedule_confirm_btn.pack(side="right")
        self._schedule_confirm_btn.configure(command=lambda: self._confirm_schedule(listing_id))

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

        if hasattr(self, '_schedule_confirm_btn') and self._schedule_confirm_btn:
            self._schedule_confirm_btn.configure(state="disabled", text="Scheduling...")

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
                    self.after(0, lambda: hasattr(self, '_schedule_confirm_btn') and self._schedule_confirm_btn and self._schedule_confirm_btn.winfo_exists() and self._schedule_confirm_btn.configure(state="normal", text="Confirm"))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
                self.after(0, lambda: hasattr(self, '_schedule_confirm_btn') and self._schedule_confirm_btn and self._schedule_confirm_btn.winfo_exists() and self._schedule_confirm_btn.configure(state="normal", text="Confirm"))

        threading.Thread(target=_do, daemon=True).start()

    def _schedule_done(self):
        if hasattr(self, '_schedule_confirm_btn') and self._schedule_confirm_btn:
            if self._schedule_confirm_btn.winfo_exists():
                self._schedule_confirm_btn.configure(state="normal", text="Confirm")
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

    # ── Loading ────────────────────────────────────────────────────

    def _show_dash_loading(self, parent=None):
        self._hide_dash_loading()
        parent = parent or self.content_wrapper
        self._dash_progress = ctk.CTkProgressBar(parent, mode="indeterminate",
                                                  fg_color=self.entry_border,
                                                  progress_color=self.primary_color)
        self._dash_progress.pack(fill="x", pady=(0, 10))
        self._dash_progress.start()

    def _hide_dash_loading(self):
        if hasattr(self, '_dash_progress') and self._dash_progress:
            self._dash_progress.stop()
            self._dash_progress.pack_forget()
            self._dash_progress = None

    # ── Animation ──────────────────────────────────────────────────

    def animate_sidebar(self):
        self._animate_sidebar_shared(
            self.sidebar_main_frame, '_sidebar_width', 'is_sidebar_expanded',
            self.content_wrapper,
            on_done=lambda: self.reflow_cards() if hasattr(self, 'reflow_cards') else None
        )

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
                    self.after(0, lambda: card_img.winfo_exists() and card_img.configure(image=ctk_image))
                except Exception:
                    self.after(0, lambda: card_img.winfo_exists() and card_img.configure(text="[ Image Unavailable ]",
                                                             text_color=self.text_color))

            threading.Thread(target=load_image, daemon=True).start()
        else:
            card_img = ctk.CTkLabel(card, text="[ No Image ]", width=380, height=200,
                                    fg_color=self.fg_color, text_color=self.text_color,
                                    corner_radius=6)
        card_img.pack(pady=(10, 0), padx=5)

        card_name = ctk.CTkLabel(card, text=house_data.get("name", "Unknown Property"),
                                 font=self.body_bold_paragraph_font,
                                 text_color=self.text_color)
        card_name.pack(anchor="w", padx=15, pady=(10, 0))

        card_location = ctk.CTkLabel(card, text=house_data.get("location", "Location not available"),
                                     font=self.body_paragraph_font,
                                     text_color=self.text_color)
        card_location.pack(anchor="w", padx=15)

        card_amenities = ctk.CTkLabel(card, text=house_data.get("amenities", ""),
                                      font=self.body_paragraph_font,
                                      text_color=self.text_color)
        card_amenities.pack(anchor="w", padx=15)

        card_title = ctk.CTkLabel(card, text="Description",
                                  font=self.body_description_font,
                                  text_color=self.text_color)
        card_title.pack(anchor="w", padx=15, pady=(0, 2))

        desc_text = house_data.get("desc", "No description available")
        font = self.body_paragraph_font
        max_width = 350 * 3
        if font.measure(desc_text) > max_width:
            while font.measure(desc_text + "...") > max_width and len(desc_text) > 0:
                desc_text = desc_text[:-1]
            desc_text += "..."
        card_desc = ctk.CTkLabel(card, text=desc_text,
                                 font=self.body_paragraph_font,
                                 text_color=self.text_color, wraplength=350, justify="left")
        card_desc.pack(anchor="w", padx=15, pady=(0, 5))

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
                                     )
        bookmark_btn.configure(command=lambda lid=listing_id, btn=bookmark_btn: self.toggle_bookmark(lid, btn))
        bookmark_btn.pack(side="right")

        # ── Make the entire card clickable to open property details ──
        card.configure(cursor="hand2")
        card.listing_id = listing_id

        def _on_card_click(event, lid=listing_id):
            self._open_property_details(lid)

        card.bind("<Button-1>", _on_card_click)
        for child in card.winfo_children():
            if not isinstance(child, ctk.CTkButton):
                child.bind("<Button-1>", _on_card_click)
            for grandchild in child.winfo_children():
                if not isinstance(grandchild, ctk.CTkButton):
                    grandchild.bind("<Button-1>", _on_card_click)

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
        # Clear previous widgets with safety check
        try:
            for w in self.cards_grid_frame.winfo_children():
                w.destroy()
        except Exception:
            pass
        
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

    def _refresh_explore(self):
        for card in self.cards_list:
            try:
                card.destroy()
            except Exception:
                pass
        self.cards_list = []
        if hasattr(self, '_error_frame') and self._error_frame:
            self._error_frame.destroy()
            self._error_frame = None
        self._load_initial_dashboard()

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
            self.after(4000, lambda: self._load_more_error.winfo_exists() and self._load_more_error.configure(text=""))
        else:
            self._load_more_error.configure(text=msg, text_color=self.text_color)
            self.after(2000, lambda: self._load_more_error.winfo_exists() and self._load_more_error.configure(text=""))

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
                resp = self.api.get(f"/search/?q={quote(query)}", timeout=10)
                if resp.status_code == 200:
                    results = resp.json()
                    self.after(0, lambda: self._rebuild_cards(results))
                else:
                    self.after(0, lambda: self._search_error.winfo_exists() and self._search_error.configure(
                        text="Search failed — try a different query"))
            except Exception:
                self.after(0, lambda: self._search_error.winfo_exists() and self._search_error.configure(
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
            btn.configure(state="disabled")
        self._search_progress.pack(fill="x", padx=20, pady=(0, 10))
        self._search_progress.start()

        for name, btn in self.filter_buttons.items():
            btn.configure(fg_color=self.secondary_color, text_color=self.text_color)

        self.filter_buttons[selected_filter].configure(fg_color=self.primary_color,
                                                       text_color="white")

        def _cleanup():
            self._search_progress.stop()
            self._search_progress.pack_forget()
            for name, btn in self.filter_buttons.items():
                btn.configure(state="normal")

        if selected_filter == "All":
            _cleanup()
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
                self.after(0, _cleanup)
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
            self.after(0, _cleanup)

        threading.Thread(target=_do, daemon=True).start()

    def toggle_bookmark(self, listing_id, btn=None):
        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            self.show_toast("Please log in to bookmark listings", is_error=True)
            return

        if btn:
            btn.configure(state="disabled")

        def _do():
            try:
                resp = self.api.post("/favorites/toggle",
                                     json={"user_id": user_id, "listing_id": listing_id})
                if resp.status_code == 200:
                    action = resp.json().get("action", "")
                    self.after(0, lambda: self.show_toast(f"Bookmark {action}!", is_error=False))
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to toggle bookmark", is_error=True))
            finally:
                if btn:
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal"))

        threading.Thread(target=_do, daemon=True).start()

    def _rebuild_cards(self, houses):
        if hasattr(self, '_error_frame') and self._error_frame:
            self._error_frame.destroy()
            self._error_frame = None
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

    def _cancel_booking(self, booking_id, btn=None):
        dialog = ctk.CTkInputDialog(text="Type CANCEL to confirm cancellation:", title="Cancel Booking")
        if dialog.get_input() != "CANCEL":
            return

        if btn:
            btn.configure(state="disabled", text="Cancelling...")

        def _do():
            try:
                user_id = getattr(self, 'current_user', {}).get('user_id', 0)
                resp = self.api.patch(f"/bookings/{booking_id}/status", json={
                    "status": "cancelled",
                    "changed_by_user_id": user_id
                }, timeout=10)
                if resp.status_code == 200:
                    self.after(0, lambda: self._cancel_done())
                else:
                    err = resp.json().get("detail", "Failed to cancel")
                    self.after(0, lambda: self.show_toast(err, is_error=True))
                    if btn:
                        self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal", text="Cancel Booking"))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
                if btn:
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal", text="Cancel Booking"))

        threading.Thread(target=_do, daemon=True).start()

    def _cancel_done(self):
        self.show_toast("Booking cancelled!", is_error=False)
        self.show_tenant_bookings_content()

    # ── Payment Form (Pay & Request Move-in) ──────────────────────

    def _show_payment_form(self, booking_id, card, pay_btn, total_price=0):
        pay_btn.pack_forget()
        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(side="right", padx=15, pady=8)
        form_frame._pay_form_ref = True

        method_combo = ctk.CTkComboBox(
            form_frame, values=["GCash", "Bank Transfer", "Cash", "Card"],
            width=140, height=32, font=self.body_paragraph_font,
            fg_color=self.fg_color, border_color=self.entry_border, border_width=1,
            button_color=self.primary_color, button_hover_color=self.hover_color,
            dropdown_fg_color=self.fg_color, dropdown_text_color=self.text_color,
            dropdown_hover_color=self.hover_color, dropdown_font=self.body_light_font,
            text_color=self.text_color
        )
        method_combo.set("GCash")
        method_combo.pack(side="left", padx=(0, 6))

        ref_entry = ctk.CTkEntry(
            form_frame, placeholder_text="Reference # (optional)",
            font=self.body_paragraph_font, width=140, height=32,
            fg_color=self.fg_color, border_color=self.entry_border, border_width=1,
            text_color=self.text_color
        )
        ref_entry.pack(side="left", padx=(0, 6))

        submit_btn = ctk.CTkButton(form_frame, text="Submit Payment",
                                   fg_color=self.primary_color,
                                   hover_color=self.hover_color,
                                   text_color="white",
                                   font=self.body_paragraph_font,
                                   height=32)
        submit_btn.pack(side="left", padx=(0, 4))

        cancel_link = ctk.CTkButton(form_frame, text="Cancel",
                                    fg_color="transparent",
                                    text_color=self.primary_color,
                                    hover_color=self.hover_color,
                                    font=self.body_paragraph_font,
                                    height=32, width=60)
        cancel_link.pack(side="left")

        submit_btn.configure(command=lambda: self._payment_submit(booking_id, form_frame, method_combo, ref_entry, submit_btn, cancel_link, pay_btn, total_price))
        cancel_link.configure(command=lambda: self._close_payment_form(form_frame, pay_btn))

    def _close_payment_form(self, form_frame, pay_btn):
        try:
            form_frame.destroy()
        except Exception:
            pass
        pay_btn.pack(side="right", padx=(8, 0))

    def _payment_submit(self, booking_id, form_frame, method_combo, ref_entry, submit_btn, cancel_link, pay_btn, total_price=0):
        method = method_combo.get().strip()
        ref_no = ref_entry.get().strip() or None

        if not method:
            self.show_toast("Please select a payment method.", is_error=True)
            return

        submit_btn.configure(state="disabled", text="Submitting...")

        def _do():
            try:
                resp = self.api.post("/payments/", json={
                    "booking_id": booking_id,
                    "amount": total_price,
                    "method": method,
                    "reference_no": ref_no,
                }, timeout=10)
                if resp.status_code not in (200, 201):
                    err = resp.json().get("detail", "Payment failed")
                    self.after(0, lambda: self.show_toast(err, is_error=True))
                    self.after(0, lambda: submit_btn.winfo_exists() and submit_btn.configure(state="normal", text="Submit Payment"))
                    return
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
                self.after(0, lambda: submit_btn.winfo_exists() and submit_btn.configure(state="normal", text="Submit Payment"))
                return

            try:
                user_id = getattr(self, 'current_user', {}).get('user_id', 0)
                resp2 = self.api.patch(f"/bookings/{booking_id}/status", json={
                    "status": "active",
                    "changed_by_user_id": user_id
                }, timeout=10)
                if resp2.status_code == 200:
                    self.after(0, lambda: self._payment_done(form_frame, pay_btn))
                else:
                    err2 = resp2.json().get("detail", "Failed to update booking")
                    self.after(0, lambda: self.show_toast(err2, is_error=True))
                    self.after(0, lambda: submit_btn.winfo_exists() and submit_btn.configure(state="normal", text="Submit Payment"))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
                self.after(0, lambda: submit_btn.winfo_exists() and submit_btn.configure(state="normal", text="Submit Payment"))

        threading.Thread(target=_do, daemon=True).start()

    def _payment_done(self, form_frame, pay_btn):
        try:
            form_frame.destroy()
        except Exception:
            pass
        self.show_toast("Payment submitted! Move-in request sent to owner.", is_error=False)
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
        if hasattr(self, '_user_menu') and self._user_menu and self._user_menu.winfo_exists():
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
                self.after(0, lambda: self.show_toast("Failed to load bookings. Check your connection.", is_error=True))
            try:
                resp = self.api.get(f"/favorites/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    favorites = resp.json()
                    favorites_count = str(len(favorites))
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load favorites. Check your connection.", is_error=True))
            self.after(0, lambda: self._update_stat_labels(bookings_count, favorites_count, "0"))

        threading.Thread(target=_do, daemon=True).start()

    def _update_stat_labels(self, bookings, favorites, reviews):
        if hasattr(self, '_stat_labels'):
            try:
                if "Active Bookings" in self._stat_labels:
                    self._stat_labels["Active Bookings"].configure(text=bookings)
            except Exception:
                pass
            try:
                if "Saved Favorites" in self._stat_labels:
                    self._stat_labels["Saved Favorites"].configure(text=favorites)
            except Exception:
                pass
            try:
                if "Total Reviews" in self._stat_labels:
                    self._stat_labels["Total Reviews"].configure(text=reviews)
            except Exception:
                pass



    # ── Property Details (full view on card click) ──────────────────

    def _open_property_details(self, listing_id):
        """Fetch listing data and render property details inside the dashboard content area."""
        # Clear content_wrapper and show loading
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()

        loading = ctk.CTkProgressBar(self.content_wrapper, mode="indeterminate",
                                      fg_color=self.entry_border,
                                      progress_color=self.primary_color)
        loading.pack(fill="x", pady=(0, 5))
        loading.start()

        self._prop_container = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        self._prop_container.pack(fill="both", expand=True)

        def _do():
            listing_data = None
            photos_data = []
            reviews_data = []
            owner_data = None
            rooms_data = []

            try:
                resp = self.api.get(f"/boarding-houses/{listing_id}", timeout=8)
                if resp.status_code == 200:
                    listing_data = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load property details. Check your connection.", is_error=True))

            try:
                resp = self.api.get(f"/photos/listing/{listing_id}", timeout=8)
                if resp.status_code == 200:
                    photos_data = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load photos. Check your connection.", is_error=True))

            try:
                resp = self.api.get(f"/social/reviews/listing/{listing_id}", timeout=8)
                if resp.status_code == 200:
                    reviews_data = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load reviews. Check your connection.", is_error=True))

            try:
                resp = self.api.get(f"/rooms/listing/{listing_id}", timeout=8)
                if resp.status_code == 200:
                    rooms_data = resp.json()
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load rooms. Check your connection.", is_error=True))

            if listing_data:
                owner_id = listing_data.get("owner_id")
                if owner_id:
                    try:
                        resp = self.api.get(f"/users/{owner_id}/public", timeout=5)
                        if resp.status_code == 200:
                            owner_data = resp.json()
                    except Exception:
                        self.after(0, lambda: self.show_toast("Failed to load owner info. Check your connection.", is_error=True))

            self.after(0, lambda: self._build_property_details_ui(
                loading, listing_data, photos_data, reviews_data, owner_data, rooms_data
            ))

        threading.Thread(target=_do, daemon=True).start()

    def _build_property_details_ui(self, loading, listing, photos, reviews, owner, rooms=None):
        """Build the full property details layout inside the dashboard content area."""
        if rooms is None:
            rooms = []
        loading.stop()
        loading.pack_forget()

        if not listing:
            ctk.CTkLabel(self._prop_container, text="Failed to load property details.",
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(expand=True)
            ctk.CTkButton(self._prop_container, text="← Back",
                          font=self.body_paragraph_font,
                          fg_color="transparent",
                          text_color=self.primary_color,
                          hover_color=self.hover_color,
                          cursor="hand2",
                          command=self.show_tenant_explore_content).pack(pady=10)
            return

        # Main scrollable container
        scroll = ctk.CTkScrollableFrame(self._prop_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # Back button row
        top_bar = ctk.CTkFrame(scroll, fg_color="transparent")
        top_bar.pack(fill="x", pady=(5, 10))
        ctk.CTkButton(top_bar, text="← Back to Listings",
                      font=self.body_paragraph_font,
                      fg_color="transparent",
                      text_color=self.primary_color,
                      hover_color=self.hover_color,
                      width=120,
                      cursor="hand2",
                      command=self.show_tenant_explore_content).pack(side="left")

        # ── Two-column layout ───────────────────────────────────────
        columns = ctk.CTkFrame(scroll, fg_color="transparent")
        columns.pack(fill="both", expand=True)
        columns.grid_columnconfigure(0, weight=1, uniform="proddetails")
        columns.grid_columnconfigure(1, weight=1, uniform="proddetails")

        left = ctk.CTkFrame(columns, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right = ctk.CTkFrame(columns, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right.grid_columnconfigure(0, weight=1)

        self._build_left_panel(left, listing, photos, reviews, rooms)
        self._build_right_panel(right, listing, owner, listing.get("listing_id") or listing.get("id"), rooms)

    # ── LEFT PANEL ──────────────────────────────────────────────────

    def _build_left_panel(self, parent, listing, photos, reviews, rooms=None):
        """Left side: images, name/price, address, rent, stars, info, reviews."""

        # ── Main Image ──────────────────────────────────────────────
        main_img_label = ctk.CTkLabel(parent, text="[ Loading image... ]",
                                       height=320,
                                       fg_color=self.secondary_color,
                                       corner_radius=8)
        main_img_label.pack(fill="x", pady=(0, 8))

        # ── Thumbnail Row ───────────────────────────────────────────
        thumb_row = ctk.CTkFrame(parent, fg_color="transparent")
        thumb_row.pack(fill="x", pady=(0, 15))

        sorted_photos = sorted(photos, key=lambda p: (not p.get("is_primary", False), p.get("sort_order", 0)))
        thumb_count = min(len(sorted_photos), 3)
        if thumb_count == 0:
            thumb_count = 1
        for col in range(thumb_count):
            thumb_row.grid_columnconfigure(col, weight=1, uniform="thumbs")

        for i in range(thumb_count):
            lbl = ctk.CTkLabel(thumb_row, text="", height=160,
                                fg_color=self.secondary_color, corner_radius=6,
                                cursor="hand2")
            lbl.grid(row=0, column=i, padx=3, sticky="ew")
            if i < len(sorted_photos):
                url = sorted_photos[i].get("photo_url", "")
                if url:
                    self._load_thumbnail(lbl, url, (260, 160))
                is_last = i == thumb_count - 1
                if is_last and len(sorted_photos) > 3:
                    lbl.configure(text=f"+{len(sorted_photos) - 3} more",
                                  font=self.body_paragraph_font,
                                  text_color=self.primary_color,
                                  compound="center")
                idx_capture = i
                lbl.bind("<Button-1>", lambda e, idx=idx_capture: self._show_photo_lightbox(
                    sorted_photos, idx))
            else:
                lbl.configure(text="[ No Image ]", font=self.body_description_font,
                              text_color=self.text_color)

        # Load main image (async)
        if sorted_photos:
            main_url = sorted_photos[0].get("photo_url", "")
            if main_url:
                def load_main():
                    try:
                        img_data = requests.get(main_url, timeout=5).content
                        pil_img = Image.open(io.BytesIO(img_data))
                        w, h = pil_img.size
                        target_w = 600
                        target_h = int((h / w) * target_w)
                        ctk_img = ctk.CTkImage(pil_img, size=(target_w, target_h))
                        self.after(0, lambda: main_img_label.configure(
                            image=ctk_img, text="", height=target_h))
                    except Exception:
                        self.after(0, lambda: main_img_label.configure(
                            text="[ Image Unavailable ]",
                            font=self.body_light_font,
                            text_color=self.text_color))
                threading.Thread(target=load_main, daemon=True).start()

        # ── Details Card ────────────────────────────────────────────
        details = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                border_width=1, border_color=self.entry_border,
                                corner_radius=8)
        details.pack(fill="x", pady=(0, 15))
        details.grid_columnconfigure(0, weight=1)
        details.grid_columnconfigure(1, weight=0)

        # Row 0: Name + Price
        prop_name = listing.get("bh_name", listing.get("name", "Unknown"))
        ctk.CTkLabel(details, text=prop_name,
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).grid(row=0, column=0, sticky="w",
                                                       padx=12, pady=(12, 2))

        # Calculate price_range from rooms if not in listing
        price = listing.get("price_range", "")
        if not price and rooms:
            prices = [float(r.get("price_per_month", 0)) for r in rooms 
                     if r.get("price_per_month") is not None]
            if prices:
                price = f"₱{min(prices):,.0f} - ₱{max(prices):,.0f}"
        
        ctk.CTkLabel(details, text=price if price else "Price TBA",
                     font=self.body_bold_paragraph_font,
                     text_color=self.primary_color).grid(row=0, column=1, sticky="e",
                                                          padx=12, pady=(12, 2))

        # Row 1: Address + Monthly Rent
        loc_parts = []
        if listing.get("location"):
            loc = listing["location"]
            if isinstance(loc, dict):
                parts = [loc.get(s, "") for s in ("street", "barangay", "city", "province")]
                loc_parts = [p for p in parts if p]
        address = ", ".join(loc_parts) if loc_parts else "Address not available"

        ctk.CTkLabel(details, text=address,
                     font=self.body_description_font,
                     text_color=self.text_color).grid(row=1, column=0, sticky="w",
                                                       padx=12, pady=(0, 2))

        ctk.CTkLabel(details, text="Monthly Rent",
                     font=self.body_description_font,
                     text_color=self.text_color).grid(row=1, column=1, sticky="e",
                                                       padx=12, pady=(0, 2))

        # Row 2: Separator
        sep = ttk.Separator(details, orient="horizontal")
        sep.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(6, 6))

        # Row 3: Stars + Rooms
        info_row = ctk.CTkFrame(details, fg_color="transparent")
        info_row.grid(row=3, column=0, columnspan=2, sticky="w", padx=12, pady=(8, 12))

        avg_rating = 0
        if reviews:
            avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews)
        rounded = round(avg_rating)

        star_frame = ctk.CTkFrame(info_row, fg_color="transparent")
        star_frame.pack(side="left")
        for s in range(5):
            star_img = self.yellow_star if s < rounded else self.grey_star
            ctk.CTkLabel(star_frame, text="", image=star_img,
                         width=16, height=16).pack(side="left", padx=1)

        ctk.CTkLabel(info_row, text=f" {avg_rating:.1f} ({len(reviews)} Reviews)",
                     font=self.body_description_font,
                     text_color=self.text_color).pack(side="left", padx=(4, 12))

        if rooms is None:
            rooms = []
        rooms_count = len(rooms) if rooms else 0
        ctk.CTkLabel(info_row, text=f"{rooms_count} Rooms Available",
                     font=self.body_description_font,
                     text_color=self.text_color).pack(side="left")

        # ── Property Description (outside card) ─────────────────────
        desc_section = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                     border_width=1, border_color=self.entry_border,
                                     corner_radius=8)
        desc_section.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(desc_section, text="Property Description",
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(anchor="w", padx=12, pady=(10, 4))

        desc_text = listing.get("description", "No description available.")
        ctk.CTkLabel(desc_section, text=desc_text,
                     font=self.body_light_font,
                     text_color=self.text_color,
                     wraplength=550, justify="left").pack(anchor="w", padx=12, pady=(4, 12))

        # ── Reviews Section (outside card) ──────────────────────────
        rev_section = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                    border_width=1, border_color=self.entry_border,
                                    corner_radius=8)
        rev_section.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(rev_section, text=f"Reviews ({len(reviews)})",
                     font=ctk.CTkFont(family="Poppins", size=20, weight="bold"),
                     text_color=self.text_color).pack(anchor="w", padx=12, pady=(10, 6))

        if reviews:
            for r in reviews[:5]:
                r_card = ctk.CTkFrame(rev_section, fg_color="transparent",
                                       border_width=1, border_color=self.entry_border,
                                       corner_radius=6)
                r_card.pack(fill="x", padx=12, pady=3)
                r_inner = ctk.CTkFrame(r_card, fg_color="transparent")
                r_inner.pack(fill="x", padx=10, pady=8)

                # ── Top row: avatar + name + stars ──
                top_row = ctk.CTkFrame(r_inner, fg_color="transparent")
                top_row.pack(fill="x")

                uname = r.get("user_name", f"User {r.get('user_id', '')}")
                initial = uname[0].upper() if uname else "?"
                avatar = ctk.CTkFrame(top_row, width=32, height=32,
                                       corner_radius=16,
                                       fg_color=self.primary_color)
                avatar.pack(side="left")
                avatar.pack_propagate(False)
                ctk.CTkLabel(avatar, text=initial,
                             font=ctk.CTkFont(size=14, weight="bold"),
                             text_color="white").place(relx=0.5, rely=0.5, anchor="center")

                ctk.CTkLabel(top_row, text=uname,
                             font=ctk.CTkFont(family="Poppins", size=20, weight="bold"),
                             text_color=self.text_color).pack(side="left", padx=(8, 0))

                r_rating = r.get("rating", 0)
                r_star_frame = ctk.CTkFrame(top_row, fg_color="transparent")
                r_star_frame.pack(side="right")
                for s in range(5):
                    img = self.yellow_star if s < r_rating else self.grey_star
                    ctk.CTkLabel(r_star_frame, text="", image=img,
                                 width=16, height=16).pack(side="left", padx=1)

                # ── Date row ──
                created = r.get("created_at")
                if created:
                    try:
                        dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
                        date_str = dt.strftime("%B %d, %Y")
                    except Exception:
                        date_str = str(created)[:10]
                else:
                    date_str = ""
                ctk.CTkLabel(r_inner, text=date_str,
                             font=self.body_description_font,
                             text_color=self.text_color).pack(anchor="w", pady=(2, 0))

                # ── Comment ──
                if r.get("comment"):
                    ctk.CTkLabel(r_inner, text=r["comment"],
                                 font=self.body_paragraph_font,
                                 text_color=self.text_color,
                                 wraplength=500, justify="left").pack(anchor="w", pady=(4, 0))
        else:
            ctk.CTkLabel(rev_section, text="No reviews yet.",
                         font=self.body_light_font,
                         text_color=self.text_color).pack(padx=12, pady=(4, 12))

        # ── Add/Edit Review form inside the same card ──────────────
        listing_id = listing.get("listing_id") or listing.get("id")
        current_user_id = getattr(self, 'current_user', {}).get('user_id')
        existing_review = None
        if current_user_id and reviews:
            for r in reviews:
                if r.get("user_id") == current_user_id:
                    existing_review = r
                    break

        ttk.Separator(rev_section, orient="horizontal").pack(fill="x", padx=12, pady=6)

        is_edit = existing_review is not None
        ctk.CTkLabel(rev_section, text="Edit Review" if is_edit else "Write a Review",
                     font=self.body_paragraph_font,
                     text_color=self.text_color).pack(anchor="w", padx=12)

        star_select_frame = ctk.CTkFrame(rev_section, fg_color="transparent")
        star_select_frame.pack(anchor="w", padx=12, pady=(4, 6))
        default_rating = existing_review.get("rating", 5) if existing_review else 5
        self._selected_review_stars = default_rating
        star_btns = []
        for s in range(1, 6):
            btn = ctk.CTkButton(star_select_frame, text="",
                                image=self.yellow_star,
                                width=30, height=30,
                                fg_color="transparent",
                                hover_color=self.hover_color,
                                cursor="hand2")
            btn.pack(side="left", padx=1)
            btn.configure(command=lambda val=s, btns=star_btns: self._set_review_stars(
                val, btns))
            star_btns.append(btn)

        self._set_review_stars(default_rating, star_btns)

        review_entry = ctk.CTkTextbox(rev_section, height=70,
                                       font=self.body_light_font,
                                       fg_color=self.fg_color,
                                       border_width=1,
                                       border_color=self.entry_border,
                                       corner_radius=6)
        review_entry.pack(fill="x", padx=12, pady=(0, 6))
        if existing_review and existing_review.get("comment"):
            review_entry.insert("1.0", existing_review["comment"])
        else:
            review_entry.insert("1.0", "Share your experience...")

        def _clear_placeholder(event):
            if review_entry.get("1.0", "end-1c").strip() == "Share your experience...":
                review_entry.delete("1.0", "end")
        review_entry.bind("<FocusIn>", _clear_placeholder)

        if is_edit:
            review_btn = ctk.CTkButton(rev_section, text="Update Review",
                                       font=self.body_paragraph_font,
                                       fg_color=self.primary_color,
                                       text_color="white",
                                       hover_color=self.hover_color,
                                       cursor="hand2")
            review_btn.configure(command=lambda btn=review_btn: self._update_review(
                existing_review["review_id"],
                listing_id,
                self._selected_review_stars,
                review_entry,
                btn))
            review_btn.pack(anchor="w", padx=12, pady=(0, 12))
        else:
            review_btn = ctk.CTkButton(rev_section, text="Submit Review",
                                       font=self.body_paragraph_font,
                                       fg_color=self.primary_color,
                                       text_color="white",
                                       hover_color=self.hover_color,
                                       cursor="hand2")
            review_btn.configure(command=lambda btn=review_btn: self._submit_review(
                listing_id,
                self._selected_review_stars,
                review_entry,
                btn))
            review_btn.pack(anchor="w", padx=12, pady=(0, 12))

    def _set_review_stars(self, val, btns):
        """Highlight star rating selector buttons up to `val`."""
        self._selected_review_stars = val
        for i, btn in enumerate(btns):
            if i < val:
                btn.configure(image=self.yellow_star)
            else:
                btn.configure(image=self.grey_star)

    # ── RIGHT PANEL ─────────────────────────────────────────────────

    def _build_right_panel(self, parent, listing, owner, listing_id, rooms=None):
        """Right side: Contact Owner, Amenities, House Rules, room picker, dates, booking."""
        if rooms is None:
            rooms = []

        def _make_card(parent, title):
            card = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                 corner_radius=8, border_width=1,
                                 border_color=self.entry_border)
            card.pack(fill="x", pady=(0, 12))
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=12, pady=(10, 4))
            ctk.CTkLabel(header, text=title,
                         font=self.body_paragraph_font,
                         text_color=self.text_color).pack(anchor="w")
            body = ctk.CTkFrame(card, fg_color="transparent")
            body.pack(fill="x", padx=12, pady=(0, 12))
            return body

        # ── 1. Contact Owner ────────────────────────────────────────
        body = _make_card(parent, "Contact Owner")

        import webbrowser

        if owner:
            name = owner.get("name", "Property Owner")
            phone = owner.get("phone", "")
            email = owner.get("email", "")

            ctk.CTkLabel(body, text=name,
                         font=self.body_bold_paragraph_font,
                         text_color=self.text_color).pack(anchor="w")

            contact_frame = ctk.CTkFrame(body, fg_color="transparent")
            contact_frame.pack(fill="x", pady=(6, 0))

            if phone:
                phone_frame = ctk.CTkFrame(contact_frame, fg_color="transparent")
                phone_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(phone_frame, text="📞  ",
                             font=self.body_paragraph_font).pack(side="left")
                phone_lbl = ctk.CTkLabel(phone_frame, text=phone,
                                          font=self.body_light_font,
                                          text_color=self.primary_color,
                                          cursor="hand2")
                phone_lbl.pack(side="left")
                phone_lbl.bind("<Button-1>", lambda e, p=phone: webbrowser.open(f"tel:{p}"))
            if email:
                email_frame = ctk.CTkFrame(contact_frame, fg_color="transparent")
                email_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(email_frame, text="✉️  ",
                             font=self.body_paragraph_font).pack(side="left")
                email_lbl = ctk.CTkLabel(email_frame, text=email,
                                          font=self.body_light_font,
                                          text_color=self.primary_color,
                                          cursor="hand2")
                email_lbl.pack(side="left")
                email_lbl.bind("<Button-1>", lambda e, em=email: webbrowser.open(f"mailto:{em}"))
        else:
            ctk.CTkLabel(body, text="Owner information not available",
                         font=self.body_light_font,
                         text_color=self.text_color).pack(anchor="w")

        # ── 2. Schedule Viewing ──────────────────────────────────────
        body = _make_card(parent, "Schedule a Viewing")
        ctk.CTkLabel(body, text="Arrange a time to visit this property in person.",
                     font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 8))
        ctk.CTkButton(body, text="Schedule Viewing",
                     font=self.body_paragraph_font,
                     fg_color=self.primary_color,
                     hover_color=self.hover_color,
                     text_color="white",
                     command=lambda: self._schedule_viewing(listing_id)).pack(fill="x")

        # ── 3. Amenities ────────────────────────────────────────────
        body = _make_card(parent, "Amenities")

        amenities_str = listing.get("amenities", "")
        if amenities_str and isinstance(amenities_str, str):
            amenity_list = [a.strip() for a in amenities_str.split(",") if a.strip()]
        else:
            amenity_list = ["Wi-Fi", "Aircon", "Kitchen"]

        for a in amenity_list:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text="✓  ",
                         font=self.body_paragraph_font,
                         text_color=self.primary_color).pack(side="left")
            ctk.CTkLabel(row, text=a,
                         font=self.body_light_font,
                         text_color=self.text_color).pack(side="left")

        # ── 4. Select Room ───────────────────────────────────────────
        room_card = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                  corner_radius=8, border_width=1,
                                  border_color=self.entry_border)
        room_card.pack(fill="x", pady=(0, 12))
        room_header = ctk.CTkFrame(room_card, fg_color="transparent")
        room_header.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(room_header, text="Select Room",
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(anchor="w")
        room_body = ctk.CTkFrame(room_card, fg_color="transparent")
        room_body.pack(fill="x", padx=12, pady=(0, 12))

        self._selected_room = None
        self._selected_room_price = 0

        if rooms:
            def _safe_float(val, default=0):
                try:
                    return float(val)
                except (TypeError, ValueError):
                    return default

            room_options = []
            for r in rooms:
                label = f"Room #{r.get('room_id')}"
                if r.get("room_type"):
                    label += f" ({r['room_type']})"
                label += f"  —  ₱{_safe_float(r.get('price_per_month', 0)):,.2f}/mo"
                room_options.append(label)
            
            self._selected_room = rooms[0]
            self._selected_room_price = _safe_float(rooms[0].get("price_per_month", 0))

            # Create entry box and dropdown
            room_entry = ctk.CTkComboBox(room_body, values=room_options,
                                         font=self.body_light_font,
                                         fg_color=self.fg_color,
                                         state="readonly")
            room_entry.set(room_options[0])
            room_entry.pack(fill="x")

            def _on_room_select(choice):
                try:
                    idx = room_options.index(choice)
                    self._selected_room = rooms[idx]
                    self._selected_room_price = _safe_float(rooms[idx].get("price_per_month", 0))
                    _update_fees()
                except ValueError:
                    pass

            room_dropdown = self._make_dropdown(room_entry, values=room_options,
                                               command=_on_room_select)
        else:
            ctk.CTkLabel(room_body, text="No rooms available for this property",
                         font=self.body_light_font,
                         text_color=self.text_color).pack(anchor="w")

        # ── 5. House Rules ──────────────────────────────────────────
        body = _make_card(parent, "House Rules")

        rules = listing.get("rules", "")
        if rules:
            for line in rules.split("\n"):
                if line.strip():
                    row = ctk.CTkFrame(body, fg_color="transparent")
                    row.pack(fill="x", pady=1)
                    ctk.CTkLabel(row, text="•  ",
                                 font=self.body_paragraph_font,
                                 text_color=self.text_color).pack(side="left")
                    ctk.CTkLabel(row, text=line.strip(),
                                 font=self.body_light_font,
                                 text_color=self.text_color,
                                 wraplength=700).pack(side="left")
        else:
            ctk.CTkLabel(body, text="No specific house rules listed.",
                         font=self.body_light_font,
                         text_color=self.text_color).pack(anchor="w")

        # ── 6. Check-in Date ────────────────────────────────────────
        checkin_card = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                                     corner_radius=8, border_width=1,
                                     border_color=self.entry_border)
        checkin_card.pack(fill="x", pady=(0, 12))
        checkin_header = ctk.CTkFrame(checkin_card, fg_color="transparent")
        checkin_header.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(checkin_header, text="Check-In Date",
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(anchor="w")
        body = ctk.CTkFrame(checkin_card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(0, 12))

        checkin_container = ctk.CTkFrame(body, fg_color="transparent")
        checkin_container.pack(fill="x")

        # ── Calendar pill → popup ──
        if getattr(sys, 'frozen', False):
            _cal_path = os.path.join(sys._MEIPASS, "assets", "calendar.png")
        else:
            _cal_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "calendar.png")
        cal_img = ctk.CTkImage(Image.open(_cal_path), size=(22, 22))
        self._selected_checkin_date = datetime.now().date()

        pill_frame = ctk.CTkFrame(checkin_container, fg_color=self.fg_color,
                                   corner_radius=20, border_width=1,
                                   border_color=self.entry_border)
        pill_frame.pack(anchor="w")

        pill_inner = ctk.CTkFrame(pill_frame, fg_color="transparent")
        pill_inner.pack(padx=12, pady=6)

        ctk.CTkLabel(pill_inner, text="", image=cal_img,
                     width=22, height=22).pack(side="left")

        date_lbl = ctk.CTkLabel(pill_inner,
                                 text=self._selected_checkin_date.strftime("%B %d, %Y"),
                                 font=self.body_paragraph_font,
                                 text_color=self.text_color)
        date_lbl.pack(side="left", padx=(8, 0))

        def _open_calendar():
            top = ctk.CTkToplevel(checkin_container)
            top.title("Select Date")
            top.geometry("320x300")
            top.resizable(False, False)
            top.transient(self)
            top.wait_visibility()
            top.grab_set()

            cy, cm, cd = self._selected_checkin_date.year, self._selected_checkin_date.month, self._selected_checkin_date.day

            nav_frame = ctk.CTkFrame(top, fg_color="transparent")
            nav_frame.pack(fill="x", padx=10, pady=(10, 4))

            month_lbl = ctk.CTkLabel(nav_frame, text="",
                                      font=self.body_paragraph_font,
                                      text_color=self.text_color)
            month_lbl.pack(side="left", expand=True)

            def _nav(delta):
                nonlocal cy, cm
                cm += delta
                if cm < 1:
                    cm = 12; cy -= 1
                elif cm > 12:
                    cm = 1; cy += 1
                _rebuild()

            def _rebuild():
                month_lbl.configure(text=f"{calendar.month_name[cm]} {cy}")
                for w in cal_grid.winfo_children():
                    w.destroy()
                for i, d in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
                    ctk.CTkLabel(cal_grid, text=d, font=ctk.CTkFont(size=11, weight="bold"),
                                 width=36).grid(row=0, column=i, padx=1, pady=1)
                for ri, week in enumerate(calendar.monthcalendar(cy, cm)):
                    for ci, day_num in enumerate(week):
                        if day_num == 0:
                            continue
                        bg = self.primary_color if day_num == cd else "transparent"
                        fg = "white" if bg != "transparent" else self.text_color
                        lbl = ctk.CTkLabel(cal_grid, text=str(day_num),
                                            font=self.body_light_font,
                                            text_color=fg, fg_color=bg,
                                            corner_radius=16, width=32, height=28,
                                            cursor="hand2")
                        lbl.grid(row=ri + 1, column=ci, padx=1, pady=1)
                        lbl.bind("<Button-1>", lambda e, d=day_num: _pick(d))

            def _pick(d):
                nonlocal cd
                cd = d
                self._selected_checkin_date = date(cy, cm, cd)
                date_lbl.configure(text=self._selected_checkin_date.strftime("%B %d, %Y"))
                top.destroy()

            ctk.CTkButton(nav_frame, text="◀", width=30,
                           fg_color="transparent", text_color=self.text_color,
                           hover_color=self.hover_color,
                           command=lambda: _nav(-1)).pack(side="left")
            ctk.CTkButton(nav_frame, text="▶", width=30,
                           fg_color="transparent", text_color=self.text_color,
                           hover_color=self.hover_color,
                           command=lambda: _nav(1)).pack(side="right")

            cal_grid = ctk.CTkFrame(top, fg_color="transparent")
            cal_grid.pack(padx=10, pady=4)
            _rebuild()

        pill_frame.bind("<Button-1>", lambda e: _open_calendar())
        pill_inner.bind("<Button-1>", lambda e: _open_calendar())
        date_lbl.bind("<Button-1>", lambda e: _open_calendar())

        # ── 7. Check-out Date ────────────────────────────────────────
        checkout_card = ctk.CTkFrame(checkin_card, fg_color="transparent")
        checkout_card.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(checkout_card, text="Check-Out Date",
                     font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(anchor="w", pady=(4, 0))
        checkout_container = ctk.CTkFrame(checkout_card, fg_color="transparent")
        checkout_container.pack(fill="x")

        self._selected_checkout_date = datetime.now().date() + timedelta(days=30)

        co_pill_frame = ctk.CTkFrame(checkout_container, fg_color=self.fg_color,
                                      corner_radius=20, border_width=1,
                                      border_color=self.entry_border)
        co_pill_frame.pack(anchor="w")

        co_pill_inner = ctk.CTkFrame(co_pill_frame, fg_color="transparent")
        co_pill_inner.pack(padx=12, pady=6)

        ctk.CTkLabel(co_pill_inner, text="", image=cal_img,
                     width=22, height=22).pack(side="left")

        co_date_lbl = ctk.CTkLabel(co_pill_inner,
                                    text=self._selected_checkout_date.strftime("%B %d, %Y"),
                                    font=self.body_paragraph_font,
                                    text_color=self.text_color)
        co_date_lbl.pack(side="left", padx=(8, 0))

        def _open_co_calendar():
            top = ctk.CTkToplevel(checkout_container)
            top.title("Select Date")
            top.geometry("320x300")
            top.resizable(False, False)
            top.transient(self)
            top.wait_visibility()
            top.grab_set()

            cy, cm, cd = self._selected_checkout_date.year, self._selected_checkout_date.month, self._selected_checkout_date.day

            nav_frame = ctk.CTkFrame(top, fg_color="transparent")
            nav_frame.pack(fill="x", padx=10, pady=(10, 4))

            month_lbl = ctk.CTkLabel(nav_frame, text="",
                                      font=self.body_paragraph_font,
                                      text_color=self.text_color)
            month_lbl.pack(side="left", expand=True)

            def _nav(delta):
                nonlocal cy, cm
                cm += delta
                if cm < 1:
                    cm = 12; cy -= 1
                elif cm > 12:
                    cm = 1; cy += 1
                _rebuild()

            def _rebuild():
                month_lbl.configure(text=f"{calendar.month_name[cm]} {cy}")
                for w in cal_grid.winfo_children():
                    w.destroy()
                for i, d in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
                    ctk.CTkLabel(cal_grid, text=d, font=ctk.CTkFont(size=11, weight="bold"),
                                 width=36).grid(row=0, column=i, padx=1, pady=1)
                for ri, week in enumerate(calendar.monthcalendar(cy, cm)):
                    for ci, day_num in enumerate(week):
                        if day_num == 0:
                            continue
                        bg = self.primary_color if day_num == cd else "transparent"
                        fg = "white" if bg != "transparent" else self.text_color
                        lbl = ctk.CTkLabel(cal_grid, text=str(day_num),
                                            font=self.body_light_font,
                                            text_color=fg, fg_color=bg,
                                            corner_radius=16, width=32, height=28,
                                            cursor="hand2")
                        lbl.grid(row=ri + 1, column=ci, padx=1, pady=1)
                        lbl.bind("<Button-1>", lambda e, d=day_num: _pick(d))

            def _pick(d):
                nonlocal cd
                cd = d
                self._selected_checkout_date = date(cy, cm, cd)
                co_date_lbl.configure(text=self._selected_checkout_date.strftime("%B %d, %Y"))
                _update_fees()
                top.destroy()

            ctk.CTkButton(nav_frame, text="◀", width=30,
                           fg_color="transparent", text_color=self.text_color,
                           hover_color=self.hover_color,
                           command=lambda: _nav(-1)).pack(side="left")
            ctk.CTkButton(nav_frame, text="▶", width=30,
                           fg_color="transparent", text_color=self.text_color,
                           hover_color=self.hover_color,
                           command=lambda: _nav(1)).pack(side="right")

            cal_grid = ctk.CTkFrame(top, fg_color="transparent")
            cal_grid.pack(padx=10, pady=4)
            _rebuild()

        co_pill_frame.bind("<Button-1>", lambda e: _open_co_calendar())
        co_pill_inner.bind("<Button-1>", lambda e: _open_co_calendar())
        co_date_lbl.bind("<Button-1>", lambda e: _open_co_calendar())

        # ── Monthly Rent & Fees ──
        rent_container = ctk.CTkFrame(body, fg_color="transparent")
        rent_container.pack(fill="x", pady=(12, 0))

        monthly_rent_lbl = ctk.CTkLabel(rent_container, text="",
                                         font=self.body_light_font,
                                         text_color=self.text_color)
        monthly_rent_lbl.pack(anchor="w")

        service_fee_lbl = ctk.CTkLabel(rent_container, text="",
                                        font=self.body_light_font,
                                        text_color=self.text_color)
        service_fee_lbl.pack(anchor="w")

        ttk.Separator(rent_container, orient="horizontal").pack(fill="x", pady=6)

        total_lbl = ctk.CTkLabel(rent_container, text="",
                                  font=self.body_paragraph_font,
                                  text_color=self.text_color)
        total_lbl.pack(anchor="w")

        def _update_fees():
            months = max(1, round((self._selected_checkout_date - self._selected_checkin_date).days / 30))
            monthly = self._selected_room_price if self._selected_room else 0
            fee = round(monthly * months * 0.05, 2)
            total = monthly * months + fee
            monthly_rent_lbl.configure(
                text=f"Monthly Rent: ₱{monthly:,.2f}  ×  {months} mo(s)" if months > 1
                     else f"Monthly Rent: ₱{monthly:,.2f}")
            service_fee_lbl.configure(text=f"Service Fee (5%): ₱{fee:,.2f}")
            total_lbl.configure(text=f"Total: ₱{total:,.2f}")

        _update_fees()

        # ── Request Booking button (outside card) ──
        booking_btn = ctk.CTkButton(parent, text="Request Booking",
                                     font=self.body_paragraph_font,
                                     fg_color=self.primary_color,
                                     text_color="white",
                                     hover_color=self.hover_color,
                                     cursor="hand2")
        booking_btn.pack(anchor="center", pady=(0, 12))

        def _request_booking():
            user_id = getattr(self, 'current_user', {}).get('user_id')
            if not user_id:
                self.show_toast("Please log in to book", is_error=True)
                return
            if not self._selected_room:
                self.show_toast("No room selected", is_error=True)
                return
            if self._selected_checkout_date <= self._selected_checkin_date:
                self.show_toast("Check-out must be after check-in", is_error=True)
                return
            months = max(1, round((self._selected_checkout_date - self._selected_checkin_date).days / 30))
            monthly = self._selected_room_price
            total_price = round(monthly * months * 1.05, 2)
            room_id = self._selected_room.get("room_id")
            if not room_id:
                self.after(0, lambda: self.show_toast("Room data is missing. Please try again.", is_error=True))
                booking_btn.configure(state="normal", text="Request Booking")
                return
            payload = {
                "user_id": user_id,
                "room_id": room_id,
                "check_in": self._selected_checkin_date.isoformat(),
                "check_out": self._selected_checkout_date.isoformat(),
                "total_price": total_price,
            }
            booking_btn.configure(state="disabled", text="Booking...")
            def _do_booking():
                try:
                    resp = self.api.post("/bookings/", json=payload, timeout=10)
                    if resp.status_code in (200, 201):
                        self.after(0, lambda: self.show_toast(
                            f"Booking requested! Room #{room_id} "
                            f"from {self._selected_checkin_date.isoformat()} "
                            f"to {self._selected_checkout_date.isoformat()}",
                            is_error=False))
                        self.after(700, self.show_tenant_bookings_content)
                    else:
                        detail = "Unknown error"
                        try:
                            detail = resp.json().get("detail", detail)
                        except Exception:
                            pass
                        self.after(0, lambda: self.show_toast(f"Booking failed: {detail}", is_error=True))
                except Exception as e:
                    self.after(0, lambda: self.show_toast(f"Cannot connect: {e}", is_error=True))
                finally:
                    self.after(0, lambda: booking_btn.configure(state="normal", text="Request Booking"))
            threading.Thread(target=_do_booking, daemon=True).start()

        booking_btn.configure(command=_request_booking)

    # ── PHOTO LIGHTBOX ─────────────────────────────────────────────

    def _show_photo_lightbox(self, photos, start_index):
        """Show a full-area overlay gallery with prev/next navigation inside the dashboard."""
        if not photos:
            return

        overlay = ctk.CTkFrame(self.content_wrapper, fg_color="#000000E0")
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.lift()
        overlay.focus_set()

        current = [start_index]

        img_label = ctk.CTkLabel(overlay, text="", fg_color="transparent")
        img_label.place(relx=0.5, rely=0.5, anchor="center")

        counter = ctk.CTkLabel(overlay, text="",
                                font=self.body_paragraph_font,
                                text_color="white")
        counter.place(relx=0.5, rely=0.92, anchor="center")

        def _load_lightbox_image(idx):
            url = photos[idx].get("photo_url", "")
            if not url:
                return
            try:
                img_data = requests.get(url, timeout=5).content
                pil_img = Image.open(io.BytesIO(img_data))
                cw = self.content_wrapper.winfo_width() or 800
                ch = self.content_wrapper.winfo_height() or 600
                img_w, img_h = pil_img.size
                scale = min(cw * 0.85 / img_w, ch * 0.80 / img_h, 1.0)
                display_w = int(img_w * scale)
                display_h = int(img_h * scale)
                ctk_img = ctk.CTkImage(pil_img, size=(display_w, display_h))
                self.after(0, lambda: img_label.winfo_exists() and img_label.configure(image=ctk_img, text=""))
                self.after(0, lambda: counter.winfo_exists() and counter.configure(
                    text=f"{idx + 1} / {len(photos)}"))
            except Exception:
                self.after(0, lambda: img_label.winfo_exists() and img_label.configure(
                    text="[ Unable to load image ]",
                    text_color="white", font=self.body_paragraph_font))

        def _prev():
            current[0] = (current[0] - 1) % len(photos)
            threading.Thread(target=lambda: _load_lightbox_image(current[0]),
                             daemon=True).start()

        def _next():
            current[0] = (current[0] + 1) % len(photos)
            threading.Thread(target=lambda: _load_lightbox_image(current[0]),
                             daemon=True).start()

        btn_style = dict(font=ctk.CTkFont(size=28),
                         width=50, height=50,
                         fg_color="transparent",
                         text_color="white",
                         hover_color="#FFFFFF40",
                         cursor="hand2")

        prev_btn = ctk.CTkButton(overlay, text="◀", **btn_style,
                                  command=_prev)
        prev_btn.place(relx=0.03, rely=0.5, anchor="center")

        next_btn = ctk.CTkButton(overlay, text="▶", **btn_style,
                                  command=_next)
        next_btn.place(relx=0.97, rely=0.5, anchor="center")

        close_btn = ctk.CTkButton(overlay, text="✕",
                                   font=ctk.CTkFont(size=22),
                                   width=40, height=40,
                                   fg_color="transparent",
                                   text_color="white",
                                   hover_color="#FF000060",
                                   cursor="hand2",
                                   command=overlay.destroy)
        close_btn.place(relx=0.97, rely=0.04, anchor="ne")

        def _on_key(event):
            if event.keysym == "Left":
                _prev()
            elif event.keysym == "Right":
                _next()
            elif event.keysym == "Escape":
                overlay.destroy()
        overlay.bind("<Left>", _on_key)
        overlay.bind("<Right>", _on_key)
        overlay.bind("<Escape>", _on_key)
        overlay.focus_set()

        threading.Thread(target=lambda: _load_lightbox_image(current[0]),
                         daemon=True).start()

    # ── THUMBNAIL LOADER ───────────────────────────────────────────

    def _load_thumbnail(self, label, url, size):
        """Background-load a thumbnail image into a label."""
        def _do():
            try:
                img_data = requests.get(url, timeout=5).content
                pil_img = Image.open(io.BytesIO(img_data))
                ctk_img = ctk.CTkImage(pil_img, size=size)
                self.after(0, lambda: label.winfo_exists() and label.configure(image=ctk_img, text=""))
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load photo. Check your connection.", is_error=True))
        threading.Thread(target=_do, daemon=True).start()

    # ── SUBMIT REVIEW ──────────────────────────────────────────────

    def _submit_review(self, listing_id, rating, textbox, btn=None):
        """Post a new review to the API and refresh the details view."""
        comment = textbox.get("1.0", "end-1c").strip()
        if not comment or comment == "Share your experience...":
            self.show_toast("Please write a review comment", is_error=True)
            return

        textbox.configure(state="disabled")
        if btn:
            btn.configure(state="disabled", text="Submitting...")

        def _do():
            try:
                resp = self.api.post("/social/reviews", json={
                    "listing_id": listing_id,
                    "rating": rating,
                    "comment": comment,
                }, timeout=8)
                if resp.status_code == 201:
                    self.after(0, lambda: self._review_submitted(listing_id))
                else:
                    err = resp.json().get("detail", "Failed to submit review")
                    self.after(0, lambda: self.show_toast(err, is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast(
                    "Cannot connect to server", is_error=True))
            finally:
                self.after(0, lambda: textbox.winfo_exists() and textbox.configure(state="normal"))
                if btn:
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal", text="Submit Review"))

        threading.Thread(target=_do, daemon=True).start()

    def _update_review(self, review_id, listing_id, rating, textbox, btn=None):
        """Update an existing review via PUT and refresh."""
        comment = textbox.get("1.0", "end-1c").strip()
        if not comment or comment == "Share your experience...":
            self.show_toast("Please write a review comment", is_error=True)
            return

        textbox.configure(state="disabled")
        if btn:
            btn.configure(state="disabled", text="Submitting...")

        def _do():
            try:
                resp = self.api.put(f"/social/reviews/{review_id}", json={
                    "rating": rating,
                    "comment": comment,
                }, timeout=8)
                if resp.status_code == 200:
                    self.after(0, lambda lid=listing_id: self._review_updated(lid))
                else:
                    err = resp.json().get("detail", "Failed to update review")
                    self.after(0, lambda: self.show_toast(err, is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast(
                    "Cannot connect to server", is_error=True))
            finally:
                self.after(0, lambda: textbox.winfo_exists() and textbox.configure(state="normal"))
                if btn:
                    self.after(0, lambda: btn.winfo_exists() and btn.configure(state="normal", text="Update Review"))

        threading.Thread(target=_do, daemon=True).start()

    def _review_submitted(self, listing_id):
        """Refresh the details view after a successful review submission."""
        self.show_toast("Review submitted!", is_error=False)
        self._open_property_details(listing_id)

    def _review_updated(self, listing_id):
        """Refresh the details view after a successful review update."""
        self.show_toast("Review updated!", is_error=False)
        self._open_property_details(listing_id)
