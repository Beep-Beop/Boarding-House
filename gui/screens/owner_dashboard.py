import threading
import os
import customtkinter as ctk
from tkinter import filedialog
from urllib.parse import unquote, urlparse, quote
from PIL import Image
import tkinterdnd2


class OwnerDashboardMixin:
    def show_owner_dashboard(self):
        print("[DEBUG] Showing: Owner Dashboard")
        self.clear_container()
        self._enable_debug_right_click()

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{int(w * 0.85)}x{int(h * 0.85)}")
        self.resizable(True, True)

        self.is_sidebar_expanded = True

        # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        self._build_owner_nav()

        self.body_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True)

        self._build_owner_sidebar()

        # Content wrapper for sidebar animation
        self.content_wrapper = ctk.CTkFrame(self.body_frame,
                                            fg_color="transparent"
                                            )
        self.content_wrapper.pack(side="left", fill="both", expand=True, padx=(10, 10), pady=20)

        # --- Dashboard Main Content ---
        self._set_owner_sidebar_btn("dashboard")
        self.build_dashboard_content()

    def build_dashboard_content(self):
        self.main_content = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Quick Actions bar
        quick_actions = ctk.CTkFrame(self.main_content, fg_color="transparent")
        quick_actions.pack(fill="x", pady=(0, 15))

        add_prop_btn = ctk.CTkButton(quick_actions, text="+ Add Property",
                                      font=self.body_light_font,
                                      fg_color=self.primary_color, hover_color=self.hover_color,
                                      text_color="white", height=36,
                                      command=self.show_add_property_form)
        add_prop_btn.pack(side="left", padx=(0, 10))

        view_bookings_btn = ctk.CTkButton(quick_actions, text="View All Bookings",
                                           font=self.body_light_font,
                                           fg_color=self.secondary_color, hover_color=self.hover_color,
                                           text_color=self.text_color, height=36,
                                           border_width=1, border_color=self.entry_border,
                                           command=self.show_owner_bookings)
        view_bookings_btn.pack(side="left")

        owner_id = getattr(self, 'current_user', {}).get('user_id', 0)

        self._owner_dashboard_cards_data = {
            "total_listings": "0",
            "pending_review": "0",
            "total_income": "\u20B10",
            "recent_booking": "0",
            "maint_items": [],
        }

        # Data Cards Frame (4 cards row)
        cards_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="data_card")

        card_info = [
            ("Total Listing", "total_listings"),
            ("Pending Review", "pending_review"),
            ("Total Income", "total_income"),
            ("Recent Booking", "recent_booking"),
        ]

        accent_colors = {
            "total_listings": self.primary_color,
            "pending_review": self.hover_color,
            "total_income": self.primary_color,
            "recent_booking": self.hover_color,
        }
        self._owner_stat_labels = {}
        for i, (title, key) in enumerate(card_info):
            card = ctk.CTkFrame(cards_frame, fg_color=self.secondary_color,
                                corner_radius=6, height=120,
                                border_width=1, border_color=self.entry_border)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            card.pack_propagate(False)
            card.grid_propagate(False)

            accent = ctk.CTkFrame(card, height=4, fg_color=accent_colors.get(key, self.primary_color),
                                  corner_radius=0)
            accent.place(x=0, y=0, relwidth=1)

            val = self._owner_dashboard_cards_data.get(key, "\u20B10")
            ctk.CTkLabel(card, text=title, font=self.body_big_font,
                         text_color=self.primary_color).grid(row=1, column=0, padx=15, pady=(15, 0), sticky="w")
            val_lbl = ctk.CTkLabel(card, text=val, font=self.body_bold_paragraph_font,
                                   text_color=self.text_color)
            val_lbl.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")
            self._owner_stat_labels[key] = val_lbl

            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color=self.hover_color, border_color=self.primary_color))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=self.secondary_color, border_color=self.entry_border))

        # Bottom Cards Frame
        bottom_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(0, 20))
        bottom_frame.grid_columnconfigure((0, 1), weight=1, uniform="bottom_card")

        # Payment History Card
        payment_card = ctk.CTkFrame(bottom_frame, fg_color=self.secondary_color, corner_radius=6,
                                    border_width=1, border_color=self.entry_border)
        payment_card.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="new")
        payment_card.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(payment_card, text="Payment History", font=self.body_big_font,
                     text_color=self.primary_color).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        sep = ctk.CTkFrame(payment_card, height=1, fg_color=self.entry_border)
        sep.grid(row=1, column=0, columnspan=3, sticky="ew", padx=15)

        payment_headers = ["Payment Date", "Amount", "Status"]
        for j, h in enumerate(payment_headers):
            ctk.CTkLabel(payment_card, text=h, font=self.body_paragraph_font,
                         text_color=self.text_color).grid(row=2, column=j, padx=15, pady=5, sticky="w")

        # Container for dynamic payment rows
        self._payment_rows_frame = ctk.CTkFrame(payment_card, fg_color="transparent")
        self._payment_rows_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
        self._payment_rows_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(self._payment_rows_frame, text="Loading...",
                     font=self.body_light_font, text_color=self.text_color).grid(
                     row=0, column=0, padx=15, pady=(7, 12), sticky="w")

        # Maintenance Status Card
        maint_card = ctk.CTkFrame(bottom_frame, fg_color=self.secondary_color, corner_radius=6,
                                  border_width=1, border_color=self.entry_border)
        maint_card.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="new")

        ctk.CTkLabel(maint_card, text="Maintenance Status", font=self.body_big_font,
                     text_color=self.primary_color).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        maint_sep = ctk.CTkFrame(maint_card, height=1, fg_color=self.entry_border)
        maint_sep.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15)

        self._maint_card = maint_card

        def _do():
            try:
                resp = self.api.get(f"/boarding-houses/owner/{owner_id}", timeout=5)
                if resp.status_code == 200:
                    listings = resp.json()
                    self._owner_dashboard_cards_data["total_listings"] = str(len(listings))
                    self._owner_dashboard_cards_data["pending_review"] = str(sum(1 for l in listings if l.get('status') == 'pending'))
            except Exception:
                pass
            try:
                resp2 = self.api.get(f"/bookings/owner/{owner_id}", timeout=5)
                if resp2.status_code == 200:
                    bookings = resp2.json()
                    self._owner_dashboard_cards_data["recent_booking"] = str(len(bookings))
            except Exception:
                pass
            try:
                resp3 = self.api.get(f"/maintenance/owner/{owner_id}", timeout=5)
                if resp3.status_code == 200:
                    self._owner_dashboard_cards_data["maint_items"] = resp3.json()
            except Exception:
                pass
            try:
                resp4 = self.api.get(f"/payments/owner/{owner_id}", timeout=5)
                if resp4.status_code == 200:
                    self._owner_dashboard_cards_data["payments"] = resp4.json()
                    total_income = sum(
                        p.get("amount", 0) for p in resp4.json()
                        if p.get("status") == "completed"
                    )
                    self._owner_dashboard_cards_data["total_income"] = f"\u20B1{total_income:,.0f}"
            except Exception:
                pass
            self.after(0, self._populate_owner_dashboard_cards)

        threading.Thread(target=_do, daemon=True).start()
        self._owner_fetch_notif_count()

    def _populate_owner_dashboard_cards(self):
        data = self._owner_dashboard_cards_data
        for key in ("total_listings", "pending_review", "total_income", "recent_booking"):
            if key in self._owner_stat_labels and self._owner_stat_labels[key].winfo_exists():
                self._owner_stat_labels[key].configure(text=str(data.get(key, "\u20B10")))

        maint_items = data.get("maint_items", [])

        # Guard against race condition: user may have navigated away
        if not hasattr(self, '_maint_card') or not self._maint_card or not self._maint_card.winfo_exists():
            return
        if not maint_items:
            ctk.CTkLabel(self._maint_card, text="No maintenance requests",
                         font=self.body_light_font, text_color=self.text_color).grid(row=2, column=0, padx=15, pady=(7, 12), sticky="w")

        maint_status_colors = {
            "pending": self.hover_color,
            "in_progress": self.hover_color,
            "completed": self.primary_color,
        }

        self.maint_detail_frames = {}
        for r, item in enumerate(maint_items):
            bottom_pady = 12 if r == len(maint_items) - 1 else 7
            req_title = item.get("title", f"Request #{item.get('request_id', '?')}")
            req_status = item.get("status", "unknown")
            req_desc = item.get("description", "")

            req_lbl = ctk.CTkLabel(self._maint_card, text=req_title, font=self.body_paragraph_font,
                                   text_color=self.text_color, cursor="hand2")
            req_lbl.grid(row=2+r*2, column=0, padx=15, pady=(7, bottom_pady), sticky="w")
            req_lbl.bind("<Button-1>", lambda e, t=req_title: self.toggle_maint_detail(t))

            badge_color = maint_status_colors.get(req_status.lower(), self.text_color)
            status_lbl = ctk.CTkLabel(self._maint_card, text=req_status.replace("_", " ").capitalize(),
                                      font=self.body_light_font,
                                      fg_color=badge_color, text_color="#FFFFFF",
                                      corner_radius=4, padx=8, pady=2)
            status_lbl.grid(row=2+r*2, column=1, padx=15, pady=(7, bottom_pady), sticky="w")

            detail_frame = ctk.CTkFrame(self._maint_card, fg_color="transparent")
            detail_frame.grid(row=3+r*2, column=0, columnspan=2, padx=25, pady=(0, 7), sticky="ew")
            detail_frame.grid_remove()

            ctk.CTkLabel(detail_frame, text=req_desc, font=self.body_light_font,
                         text_color=self.text_color, wraplength=600, justify="left").pack(anchor="w")

            self.maint_detail_frames[req_title] = detail_frame

        self._populate_payment_history()

    def _populate_payment_history(self):
        for w in self._payment_rows_frame.winfo_children():
            w.destroy()

        data = self._owner_dashboard_cards_data.get("payments", [])
        if not data:
            ctk.CTkLabel(self._payment_rows_frame, text="No payment records",
                         font=self.body_light_font, text_color=self.text_color).grid(
                         row=0, column=0, padx=15, pady=(7, 12), sticky="w")
            return

        status_colors = {
            "paid": self.primary_color,
            "completed": self.primary_color,
            "pending": self.hover_color,
            "failed": self.error_red,
            "refunded": self.error_red,
        }

        max_rows = min(len(data), 5)
        for r in range(max_rows):
            p = data[r]
            bottom_pady = 12 if r == max_rows - 1 else 7
            paid_at = p.get("paid_at", "")
            if paid_at and len(paid_at) >= 10:
                paid_at = paid_at[:10]
            elif not paid_at:
                paid_at = "—"
            amount = p.get("amount", 0)
            status = p.get("status", "—")

            if r > 0:
                row_sep = ctk.CTkFrame(self._payment_rows_frame, height=1, fg_color=self.entry_border)
                row_sep.grid(row=r*2-1, column=0, columnspan=3, sticky="ew", padx=15)

            row = r * 2
            ctk.CTkLabel(self._payment_rows_frame, text=paid_at, font=self.body_light_font,
                         text_color=self.text_color).grid(row=row, column=0, padx=15, pady=(7, bottom_pady), sticky="w")
            ctk.CTkLabel(self._payment_rows_frame, text=f"\u20B1{amount}", font=self.body_light_font,
                         text_color=self.text_color).grid(row=row, column=1, padx=15, pady=(7, bottom_pady), sticky="w")

            badge_color = status_colors.get(status.lower(), self.text_color)
            status_lbl = ctk.CTkLabel(self._payment_rows_frame, text=status.capitalize(),
                                      font=self.body_light_font,
                                      fg_color=badge_color, text_color="#FFFFFF",
                                      corner_radius=4, padx=8, pady=2)
            status_lbl.grid(row=row, column=2, padx=15, pady=(7, bottom_pady), sticky="w")

    def animate_sidebar(self):
        target = 0 if self.is_sidebar_expanded else 250
        step = -30 if self.is_sidebar_expanded else 30
        current = getattr(self, '_sidebar_width', 250)

        if target > 0 and not self.sidebar_main_frame.winfo_ismapped():
            self.sidebar_main_frame.pack(side="left", fill="y", before=self.content_wrapper)

        def _step():
            nonlocal current
            current += step
            if (step > 0 and current >= target) or (step < 0 and current <= target):
                current = target
                self.sidebar_main_frame.configure(width=current)
                if current == 0:
                    self.sidebar_main_frame.pack_forget()
                self.is_sidebar_expanded = not self.is_sidebar_expanded
                self._sidebar_width = current
                return
            self.sidebar_main_frame.configure(width=current)
            self.after(16, _step)

        self._sidebar_width = current
        _step()

    def toggle_maint_detail(self, request_name):
        frame = self.maint_detail_frames.get(request_name)
        if frame is None:
            return
        if frame.winfo_ismapped():
            frame.grid_remove()
        else:
            frame.grid()

    def _build_owner_nav(self):
        self.owner_nav_bar_frame = ctk.CTkFrame(self.form_container,
                                                fg_color="transparent",
                                                height=60,
                                                border_width=1,
                                                border_color=self.entry_border
                                                )
        self.owner_nav_bar_frame.pack(side="top", fill="x")

        self.owner_bg_hamburg_menu = ctk.CTkButton(self.owner_nav_bar_frame,
                                                   image=self.hamburg_menu_icon,
                                                   text=None,
                                                   fg_color="transparent",
                                                   hover_color=self.hover_color,
                                                   width=25,
                                                   height=15,
                                                   command=self.animate_sidebar
                                                   )
        self.owner_bg_hamburg_menu.pack(side="left", padx=15, pady=(20, 25))

        self.owner_bg_logo = ctk.CTkLabel(self.owner_nav_bar_frame,
                                          text=None,
                                          image=self.logo
                                          )
        self.owner_bg_logo.pack(side="left", pady=(15, 20))

        # Notification Bell
        self.owner_notif_bell_frame = ctk.CTkFrame(self.owner_nav_bar_frame, fg_color="transparent")
        self.owner_notif_bell_frame.pack(side="right", padx=(0, 5))

        self.owner_notif_bell_btn = ctk.CTkLabel(self.owner_notif_bell_frame, text="",
                                                 image=self.notification_icon, cursor="hand2")
        self.owner_notif_bell_btn.pack(side="left", padx=5)
        self.owner_notif_bell_btn.bind("<Button-1>", lambda e: self.show_notifications_page())

        self.owner_notif_badge = ctk.CTkLabel(self.owner_notif_bell_frame, text="",
                                              width=16, height=16, corner_radius=8,
                                              fg_color=self.error_red, text_color="white",
                                              font=ctk.CTkFont(size=9, weight="bold"))
        self.owner_notif_badge.place(x=18, y=-2)

        self.owner_profile_frame = ctk.CTkFrame(self.owner_nav_bar_frame,
                                                fg_color="transparent"
                                                )
        self.owner_profile_frame.pack(side="right", padx=25, pady=10)

        self.owner_nav_pfp = ctk.CTkLabel(self.owner_profile_frame,
                                          text=None,
                                          image=self.pfp_placeholder_sm,
                                          width=32,
                                          height=32
                                          )
        self.owner_nav_pfp.pack(side="left", padx=(0, 12))

        self.owner_profile_text_frame = ctk.CTkFrame(self.owner_profile_frame,
                                                     fg_color="transparent"
                                                     )
        self.owner_profile_text_frame.pack(side="left")

        user_name = getattr(self, 'current_user', {}).get('name', 'Owner')

        self.owner_name_label = ctk.CTkLabel(self.owner_profile_text_frame,
                                             text=user_name,
                                             font=self.body_light_font,
                                             text_color=self.text_color
                                             )
        self.owner_name_label.pack(side="left")

        # Chevron indicator
        self.owner_profile_chevron = ctk.CTkLabel(self.owner_profile_text_frame, text="▾",
                                                  font=self.body_light_font, text_color=self.text_color)
        self.owner_profile_chevron.pack(side="left", padx=(4, 0))

        # Make clickable
        self.owner_profile_frame.bind("<Button-1>", lambda e: self._owner_toggle_user_menu())
        self.owner_profile_frame.configure(cursor="hand2")
        for child in self.owner_profile_frame.winfo_children():
            child.bind("<Button-1>", lambda e: self._owner_toggle_user_menu())

    def _build_owner_sidebar(self):
        self.sidebar_main_frame = ctk.CTkFrame(self.body_frame,
                                               fg_color="transparent",
                                               width=250,
                                               corner_radius=0,
                                               border_color=self.entry_border,
                                               border_width=1
                                               )
        self.sidebar_main_frame.pack(side="left", fill="y")
        self.sidebar_main_frame.pack_propagate(False)

        self.menu_btn_frame = ctk.CTkFrame(self.sidebar_main_frame,
                                           fg_color="transparent"
                                           )
        self.menu_btn_frame.pack(fill="both", expand=True, pady=20)

        self.dashboard_btn = ctk.CTkButton(self.menu_btn_frame,
                                           text="Dashboard",
                                           width=230,
                                           height=40,
                                           hover_color=self.hover_color,
                                           fg_color=self.primary_color,
                                           text_color="white",
                                           font=self.body_big_font,
                                           command=self.show_owner_dashboard
                                           )
        self.dashboard_btn.grid(row=0, column=0, padx=10, pady=(10, 30))

        self.tenant_btn = ctk.CTkButton(self.menu_btn_frame,
                                        text="Tenants",
                                        width=230,
                                        height=40,
                                        hover_color=self.hover_color,
                                        fg_color="transparent",
                                        text_color=self.text_color,
                                        font=self.body_big_font,
                                        command=self.show_owner_tenants
                                        )
        self.tenant_btn.grid(row=1, column=0, padx=10, pady=(0, 30))

        self.property_btn = ctk.CTkButton(self.menu_btn_frame,
                                          text="Property",
                                          width=230,
                                          height=40,
                                          hover_color=self.hover_color,
                                          fg_color="transparent",
                                          text_color=self.text_color,
                                          font=self.body_big_font,
                                          command=self.show_owner_property
                                          )
        self.property_btn.grid(row=2, column=0, padx=10, pady=(0, 30))

        self.bookings_btn = ctk.CTkButton(self.menu_btn_frame,
                                           text="Bookings",
                                           width=230,
                                           height=40,
                                           hover_color=self.hover_color,
                                           fg_color="transparent",
                                           text_color=self.text_color,
                                           font=self.body_big_font,
                                           command=self.show_owner_bookings
                                           )
        self.bookings_btn.grid(row=3, column=0, padx=10, pady=(0, 30))

    def _set_owner_sidebar_btn(self, active):
        buttons = {
            "dashboard": self.dashboard_btn,
            "tenants": self.tenant_btn,
            "property": self.property_btn,
            "bookings": self.bookings_btn,
        }
        for name, btn in buttons.items():
            if name == active:
                btn.configure(fg_color=self.primary_color, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=self.text_color)

    def show_owner_tenants(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_owner_sidebar_btn("tenants")
        self.build_tenants_content()

    def build_tenants_content(self):
        main_content = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Search bar
        search_frame = ctk.CTkFrame(main_content, fg_color=self.secondary_color,
                                    height=50, corner_radius=6)
        search_frame.pack(fill="x", pady=(0, 20))
        search_frame.pack_propagate(False)

        search_icon_lbl = ctk.CTkLabel(search_frame, image=self.search_icon, text=None)
        search_icon_lbl.pack(side="left", padx=(15, 10))

        search_entry = ctk.CTkEntry(search_frame,
                                    placeholder_text="Search tenant by name, unit or contact...",
                                    font=self.body_paragraph_font,
                                    fg_color="transparent", border_width=0)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

        # Table card
        self.owner_table_frame = ctk.CTkFrame(main_content, fg_color=self.secondary_color, corner_radius=6)
        table_frame = self.owner_table_frame
        table_frame.pack(fill="x")

        headers = ["Tenant Name", "Unit", "Contact No.", "Move-in-Date", "Payment Status", "Action"]
        for j, header in enumerate(headers):
            ctk.CTkLabel(table_frame, text=header, font=self.body_paragraph_font,
                         text_color=self.text_color).grid(row=0, column=j, padx=15, pady=(15, 10), sticky="w")
            table_frame.grid_columnconfigure(j, weight=1)

        self._tenants_table_frame = table_frame
        self._loading_tenants_label = ctk.CTkLabel(table_frame, text="Loading tenants...",
                                                   font=self.body_paragraph_font, text_color=self.text_color)
        self._loading_tenants_label.grid(row=1, column=0, columnspan=6, padx=15, pady=20, sticky="w")

        owner_id = getattr(self, 'current_user', {}).get('user_id', 0)

        def _do():
            tenant_data = []
            try:
                resp = self.api.get(f"/bookings/owner/{owner_id}", timeout=5)
                if resp.status_code == 200:
                    bookings = resp.json()
                    for b in bookings:
                        tenant_data.append((
                            f"Tenant #{b.get('user_id', '?')}",
                            f"Room #{b.get('room_id', '?')}",
                            "",
                            b.get('check_in', ''),
                            b.get('status', 'Pending').capitalize(),
                        ))
            except Exception:
                pass
            self.after(0, lambda: self._populate_tenants_table(tenant_data))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_tenants_table(self, tenant_data):
        if not hasattr(self, '_tenants_table_frame'):
            return
        table_frame = self._tenants_table_frame
        if not table_frame.winfo_exists():
            return
        if hasattr(self, '_loading_tenants_label') and self._loading_tenants_label:
            self._loading_tenants_label.destroy()
            self._loading_tenants_label = None

        if not tenant_data:
            tenant_data = [
                ("No tenants yet", "", "", "", ""),
            ]
        self.tenant_action_menus = {}
        self.tenant_action_btns = {}

        for r, (name, unit, contact, move_in, status) in enumerate(tenant_data):
            data_row = 1 + r * 2
            sep_row = data_row + 1
            is_last = r == len(tenant_data) - 1

            name_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            name_frame.grid(row=data_row, column=0, padx=15, pady=(7, 7), sticky="w")

            pfp = ctk.CTkLabel(name_frame, text=None, image=self.pfp_placeholder, width=25, height=25)
            pfp.pack(side="left", padx=(0, 8))

            ctk.CTkLabel(name_frame, text=name, font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left")

            ctk.CTkLabel(table_frame, text=unit, font=self.body_paragraph_font,
                         text_color=self.text_color).grid(row=data_row, column=1, padx=15, pady=(7, 7), sticky="w")

            ctk.CTkLabel(table_frame, text=contact, font=self.body_paragraph_font,
                         text_color=self.text_color).grid(row=data_row, column=2, padx=15, pady=(7, 7), sticky="w")

            ctk.CTkLabel(table_frame, text=move_in, font=self.body_paragraph_font,
                         text_color=self.text_color).grid(row=data_row, column=3, padx=15, pady=(7, 7), sticky="w")

            if status == "Paid":
                status_fg = self.primary_color
                status_fg_text = "white"
            elif status == "Pending":
                status_fg = self.hover_color
                status_fg_text = "white"
            else:
                status_fg = self.error_red
                status_fg_text = "white"

            status_lbl = ctk.CTkLabel(table_frame, text=status, font=self.body_paragraph_font,
                                      fg_color=status_fg, text_color=status_fg_text,
                                      corner_radius=4, padx=10, pady=2)
            status_lbl.grid(row=data_row, column=4, padx=15, pady=(7, 7), sticky="w")

            action_btn = ctk.CTkButton(table_frame, text="\u2022\u2022\u2022",
                                       width=30, height=30,
                                       fg_color="transparent", text_color=self.text_color,
                                       hover_color=self.hover_color,
                                       command=lambda n=name: self.toggle_tenant_action_menu(n))
            action_btn.grid(row=data_row, column=5, padx=15, pady=(7, 7), sticky="w")

            action_frame = ctk.CTkFrame(table_frame, fg_color="white", corner_radius=6,
                                        border_width=1, border_color=self.entry_border)

            for item_text, item_clr in [("View Details", self.text_color), ("Edit", self.text_color), ("Remove", self.error_red)]:
                ctk.CTkButton(action_frame, text=item_text, font=self.body_light_font,
                              fg_color="transparent", text_color=item_clr,
                              hover_color=self.hover_color, corner_radius=4, height=28,
                              cursor="hand2").pack(padx=5, pady=2, fill="x")

            self.tenant_action_menus[name] = action_frame
            self.tenant_action_btns[name] = action_btn

            if not is_last:
                sep = ctk.CTkFrame(table_frame, height=1, fg_color=self.entry_border)
                sep.grid(row=sep_row, column=0, columnspan=6, padx=25, pady=4, sticky="ew")

    def toggle_tenant_action_menu(self, tenant_name):
        frame = self.tenant_action_menus.get(tenant_name)
        btn = self.tenant_action_btns.get(tenant_name)
        if frame is None or btn is None:
            return
        if frame.winfo_ismapped():
            frame.place_forget()
        else:
            for f in self.tenant_action_menus.values():
                f.place_forget()
            parent = getattr(self, "owner_table_frame", frame.master)
            frame.place(x=btn.winfo_rootx() - parent.winfo_rootx() + btn.winfo_width() + 5,
                        y=btn.winfo_rooty() - parent.winfo_rooty())
            frame.lift()

    def show_owner_property(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_owner_sidebar_btn("property")
        self.build_property_content()

    def build_property_content(self):
        self._prop_main_content = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        self._prop_main_content.pack(fill="both", expand=True, padx=20, pady=10)
        self._prop_listings = []

        self._show_loading(self._prop_main_content, text="Loading properties...")

        owner_id = getattr(self, 'current_user', {}).get('user_id', 0)

        def _do():
            try:
                resp = self.api.get(f"/boarding-houses/owner/{owner_id}", timeout=5)
                listings = resp.json() if resp.status_code == 200 else []
            except Exception:
                listings = []
            self.after(0, lambda: self._populate_property_content(listings))

        threading.Thread(target=_do, daemon=True).start()

    def _filter_property_list(self):
        query = self._prop_search_entry.get().strip().lower() if hasattr(self, '_prop_search_entry') and self._prop_search_entry else ""
        for widget in self._property_main.winfo_children():
            widget.destroy()
        filtered = [l for l in self._property_list_data if not query or query in l.get('bh_name', '').lower()]
        self._render_property_cards(filtered)

    def _render_property_cards(self, listings):
        if not listings:
            ctk.CTkLabel(self._property_main, text="No properties found.",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(pady=40)
            return

        for listing in listings:
            listing_id = listing.get('listing_id')
            bh_name = listing.get('bh_name', 'Untitled')
            status = listing.get('status', 'unknown')
            property_type = listing.get('property_type', '')

            card = ctk.CTkFrame(self._property_main, fg_color=self.secondary_color, corner_radius=6)
            card.pack(fill="x", pady=5)

            def _bind_hover(widget):
                widget.bind("<Enter>", lambda e: card.configure(fg_color=self.hover_color))
                widget.bind("<Leave>", lambda e: card.configure(fg_color=self.secondary_color))

            _bind_hover(card)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(10, 2))
            _bind_hover(top_row)

            name_lbl = ctk.CTkLabel(top_row, text=bh_name, font=self.body_big_font,
                                    text_color=self.text_color)
            name_lbl.pack(side="left")
            _bind_hover(name_lbl)

            if status == "active":
                status_fg = self.primary_color
            elif status == "pending":
                status_fg = self.hover_color
            else:
                status_fg = self.error_red
            status_lbl = ctk.CTkLabel(top_row, text=status.capitalize(), font=self.body_description_font,
                                      fg_color=status_fg, text_color="white", corner_radius=4, padx=8, pady=2)
            status_lbl.pack(side="right")
            _bind_hover(status_lbl)

            bottom_row = ctk.CTkFrame(card, fg_color="transparent")
            bottom_row.pack(fill="x", padx=15, pady=(2, 10))
            _bind_hover(bottom_row)

            info_parts = []
            if property_type:
                info_parts.append(property_type)
            price_range = listing.get('price_range', '')
            if price_range:
                info_parts.append(price_range)
            info_lbl = ctk.CTkLabel(bottom_row, text=" | ".join(info_parts) if info_parts else "",
                                    font=self.body_light_font, text_color=self.text_color)
            info_lbl.pack(side="left")
            _bind_hover(info_lbl)

            action_f = ctk.CTkFrame(bottom_row, fg_color="transparent")
            action_f.pack(side="right")
            _bind_hover(action_f)

            view_btn = ctk.CTkButton(action_f, text="View", font=self.body_description_font,
                                     fg_color="transparent", text_color=self.primary_color,
                                     hover_color=self.hover_color, cursor="hand2",
                                     command=lambda lid=listing_id: self.show_property_detail(lid))
            view_btn.pack(side="left", padx=(0, 8))

            del_btn = ctk.CTkButton(action_f, text="Delete", font=self.body_description_font,
                                    fg_color="transparent", text_color=self.error_red,
                                    hover_color=self.hover_color, cursor="hand2",
                                    command=lambda lid=listing_id: self._delete_property(lid))
            del_btn.pack(side="left")

    def _populate_property_content(self, listings):
        self._hide_loading()
        for widget in self._prop_main_content.winfo_children():
            widget.destroy()

        if not listings:
            self._show_property_empty_state()
            return

        header = ctk.CTkFrame(self._prop_main_content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text="My Properties", font=self.title_font,
                     text_color=self.text_color).pack(side="left")
        ctk.CTkButton(header, text="+ Add Property", font=self.body_light_font,
                      fg_color=self.primary_color, hover_color=self.hover_color,
                      text_color="white", corner_radius=4, height=32, cursor="hand2",
                      command=self.show_add_property_form).pack(side="right")

        search_frame = ctk.CTkFrame(self._prop_main_content, fg_color=self.secondary_color,
                                    height=50, corner_radius=6)
        search_frame.pack(fill="x", pady=(0, 20))
        search_frame.pack_propagate(False)

        ctk.CTkLabel(search_frame, image=self.search_icon, text=None).pack(side="left", padx=(15, 10))
        self._prop_search_entry = ctk.CTkEntry(search_frame,
                                               placeholder_text="Search by property name...",
                                               font=self.body_paragraph_font,
                                               fg_color="transparent", border_width=0)
        self._prop_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self._prop_search_entry.bind("<KeyRelease>", lambda e: self._filter_property_list())

        self._property_main = ctk.CTkScrollableFrame(self._prop_main_content, fg_color="transparent")
        self._property_main.pack(fill="both", expand=True)
        self._property_list_data = listings
        self._render_property_cards(listings)

    def _show_property_empty_state(self):
        empty_frame = ctk.CTkFrame(self._prop_main_content, fg_color="transparent")
        empty_frame.place(relx=0.5, rely=0.5, anchor="center")
        add_btn = ctk.CTkButton(empty_frame, text="+", width=80, height=80,
                                font=self.title_font, fg_color=self.primary_color,
                                hover_color=self.hover_color, text_color="white",
                                corner_radius=40, command=self.show_add_property_form)
        add_btn.pack(pady=(0, 15))
        ctk.CTkLabel(empty_frame, text="Add Property",
                     font=self.body_bold_paragraph_font, text_color=self.text_color).pack(pady=(0, 5))
        ctk.CTkLabel(empty_frame, text="List your boarding house to start accepting tenants",
                     font=self.body_paragraph_font, text_color=self.text_color).pack()

    def show_property_detail(self, listing_id):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()

        main_content = ctk.CTkScrollableFrame(self.content_wrapper, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        header_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        back_btn = ctk.CTkLabel(header_frame, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: self.show_owner_property())
        back_btn.bind("<Enter>", lambda e: back_btn.configure(image=self.bk_btn_hvr_icon))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(image=self.bk_btn_icon))
        ctk.CTkLabel(header_frame, text="Property Details", font=self.title_font,
                     text_color=self.text_color).pack(side="left", padx=10)

        self._property_detail_main = main_content
        self._property_detail_id = listing_id

        self._show_loading(text="Loading property details...")

        def _do():
            property_data = None
            rooms_data = []
            try:
                resp = self.api.get(f"/boarding-houses/{listing_id}", timeout=5)
                if resp.status_code == 200:
                    property_data = resp.json()
            except Exception:
                pass
            try:
                resp = self.api.get(f"/rooms/listing/{listing_id}", timeout=5)
                if resp.status_code == 200:
                    rooms_data = resp.json()
            except Exception:
                pass
            self.after(0, lambda: self._populate_property_detail(property_data, rooms_data))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_property_detail(self, property_data, rooms_data):
        self._hide_loading()
        main_content = self._property_detail_main
        if not property_data:
            ctk.CTkLabel(main_content, text="Failed to load property details.",
                         font=self.body_paragraph_font, text_color=self.error_red).pack(pady=20)
            return

        bh_name = property_data.get('bh_name', 'Untitled')
        status = property_data.get('status', 'unknown')
        property_type = property_data.get('property_type', 'N/A')
        description = property_data.get('description', '')
        price_range = property_data.get('price_range', '')
        if not price_range and rooms_data:
            prices = [r.get('price_per_month', 0) for r in rooms_data if r.get('price_per_month')]
            if prices:
                price_range = f"₱{min(prices):,.0f} - ₱{max(prices):,.0f}"
        min_stay = property_data.get('min_stay_months', 1)
        rules = property_data.get('rules', '')
        is_verified = property_data.get('is_verified', False)

        # Hero card
        hero = ctk.CTkFrame(main_content, fg_color=self.secondary_color, corner_radius=6)
        hero.pack(fill="x", pady=(0, 20))
        hero_inner = ctk.CTkFrame(hero, fg_color="transparent")
        hero_inner.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(hero_inner, text=bh_name, font=self.title_font,
                     text_color=self.text_color).pack(side="left")

        if status == "active":
            status_fg = self.primary_color
        elif status == "pending":
            status_fg = self.hover_color
        else:
            status_fg = self.error_red
        ctk.CTkLabel(hero_inner, text=status.capitalize(), font=self.body_paragraph_font,
                     fg_color=status_fg, text_color="white", corner_radius=4, padx=12, pady=4).pack(side="left", padx=(15, 0))

        if is_verified:
            ctk.CTkLabel(hero_inner, text="\u2713 Verified", font=self.body_paragraph_font,
                         text_color=self.primary_color).pack(side="left", padx=(10, 0))

        edit_btn = ctk.CTkButton(hero_inner, text="Edit Property", font=self.body_paragraph_font,
                                 fg_color=self.primary_color, hover_color=self.hover_color,
                                 text_color="white", cursor="hand2",
                                 command=lambda: self.show_edit_property(self._property_detail_id))
        edit_btn.pack(side="right")

        # Two-column info
        body = ctk.CTkFrame(main_content, fg_color="transparent")
        body.pack(fill="x")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        # Left: Details
        detail_card = ctk.CTkFrame(body, fg_color=self.secondary_color, corner_radius=6)
        detail_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 20))
        ctk.CTkLabel(detail_card, text="Property Details", font=self.body_big_font,
                     text_color=self.primary_color).pack(anchor="w", padx=15, pady=(15, 10))
        for label, val in [("Type:", property_type), ("Description:", description or "—"),
                            ("Price Range:", price_range or "—"),
                            ("Min Stay:", f"{min_stay} month(s)"),
                            ("Rules:", rules or "—")]:
            row_f = ctk.CTkFrame(detail_card, fg_color="transparent")
            row_f.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row_f, text=label, font=self.body_light_font,
                         text_color=self.text_color, width=100).pack(side="left")
            val_lbl = ctk.CTkLabel(row_f, text=str(val), font=self.body_paragraph_font,
                                   text_color=self.text_color, wraplength=300, justify="left")
            val_lbl.pack(side="left", padx=(10, 0), fill="x", expand=True)

        # Right: Location & Photos (placeholder for now)
        info_card = ctk.CTkFrame(body, fg_color=self.secondary_color, corner_radius=6)
        info_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 20))
        ctk.CTkLabel(info_card, text="Status & Info", font=self.body_big_font,
                     text_color=self.primary_color).pack(anchor="w", padx=15, pady=(15, 10))
        listing_id_val = property_data.get('listing_id', '—')
        owner_id_val = property_data.get('owner_id', '—')
        created_at = property_data.get('bh_created_at', '')[:10] if property_data.get('bh_created_at') else '—'
        for label, val in [("Listing ID:", f"#{listing_id_val}"), ("Owner ID:", f"#{owner_id_val}"),
                            ("Created:", created_at)]:
            row_f = ctk.CTkFrame(info_card, fg_color="transparent")
            row_f.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row_f, text=label, font=self.body_light_font,
                         text_color=self.text_color, width=90).pack(side="left")
            ctk.CTkLabel(row_f, text=str(val), font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=(10, 0))

        # Rooms section
        rooms_header = ctk.CTkFrame(main_content, fg_color="transparent")
        rooms_header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(rooms_header, text="Rooms", font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(side="left")
        ctk.CTkButton(rooms_header, text="+ Add Room", font=self.body_light_font,
                      fg_color=self.primary_color, hover_color=self.hover_color,
                      text_color="white", corner_radius=4, height=30, cursor="hand2",
                      command=lambda: self.show_add_room_form(self._property_detail_id)).pack(side="right")

        if rooms_data:
            rooms_table = ctk.CTkFrame(main_content, fg_color=self.secondary_color, corner_radius=6)
            rooms_table.pack(fill="x", pady=(0, 20))
            headers = ["#", "Type", "Capacity", "Price/Month", "Status", "Actions"]
            for j, h in enumerate(headers):
                ctk.CTkLabel(rooms_table, text=h, font=self.body_paragraph_font,
                             text_color=self.text_color).grid(row=0, column=j, padx=10, pady=(15, 10), sticky="w")
                rooms_table.grid_columnconfigure(j, weight=1)
            for r, room in enumerate(rooms_data):
                row = 1 + r
                room_id = room.get('room_id', '?')
                room_type = room.get('room_type', '—')
                capacity = room.get('capacity', '—')
                price = room.get('price_per_month', '—')
                room_status = room.get('status', 'available')

                ctk.CTkLabel(rooms_table, text=str(room_id), font=self.body_paragraph_font,
                             text_color=self.text_color).grid(row=row, column=0, padx=10, pady=7, sticky="w")
                ctk.CTkLabel(rooms_table, text=room_type, font=self.body_paragraph_font,
                             text_color=self.text_color).grid(row=row, column=1, padx=10, pady=7, sticky="w")
                ctk.CTkLabel(rooms_table, text=str(capacity), font=self.body_paragraph_font,
                             text_color=self.text_color).grid(row=row, column=2, padx=10, pady=7, sticky="w")
                ctk.CTkLabel(rooms_table, text=f"\u20B1{price}", font=self.body_paragraph_font,
                             text_color=self.text_color).grid(row=row, column=3, padx=10, pady=7, sticky="w")

                if room_status == "available":
                    rs_fg = self.primary_color
                elif room_status == "occupied":
                    rs_fg = self.hover_color
                else:
                    rs_fg = self.error_red
                ctk.CTkLabel(rooms_table, text=room_status.capitalize(), font=self.body_description_font,
                             fg_color=rs_fg, text_color="white", corner_radius=4, padx=8, pady=2).grid(row=row, column=4, padx=10, pady=7, sticky="w")

                del_room_btn = ctk.CTkButton(rooms_table, text="Delete", font=self.body_description_font,
                                             fg_color="transparent", text_color=self.error_red,
                                             hover_color=self.hover_color, cursor="hand2",
                                             command=lambda rid=room_id: self._delete_room(rid, self._property_detail_id))
                del_room_btn.grid(row=row, column=5, padx=10, pady=7, sticky="w")
        else:
            ctk.CTkLabel(main_content, text="No rooms added yet. Add your first room!",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(pady=(0, 20))

    def show_edit_property(self, listing_id):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()

        self._prop_form_widgets = {}
        self._prop_form_files = {"images": [], "permit": None}
        self._prop_edit_mode = True
        self._prop_edit_id = listing_id

        container = ctk.CTkScrollableFrame(self.content_wrapper, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        back_btn = ctk.CTkLabel(header, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: self.show_property_detail(listing_id))
        back_btn.bind("<Enter>", lambda e: back_btn.configure(image=self.bk_btn_hvr_icon))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(image=self.bk_btn_icon))

        ctk.CTkLabel(header, text="Edit Property", font=self.alt_title_font,
                     text_color=self.text_color).pack(side="left", padx=10)

        two_col = ctk.CTkFrame(container, fg_color="transparent")
        two_col.pack(fill="both", expand=True)
        two_col.grid_columnconfigure(0, weight=1, uniform="col")
        two_col.grid_columnconfigure(1, weight=1, uniform="col")

        left = ctk.CTkFrame(two_col, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = ctk.CTkFrame(two_col, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self._edit_left = left
        self._edit_right = right

        self._show_loading(text="Loading property data...")

        def _do():
            try:
                resp = self.api.get(f"/boarding-houses/{listing_id}", timeout=5)
                data = resp.json() if resp.status_code == 200 else None
            except Exception:
                data = None
            self.after(0, lambda: self._populate_edit_form(data))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_edit_form(self, data):
        self._hide_loading()
        if not data:
            self.show_toast("Failed to load property data", is_error=True)
            self.show_owner_property()
            return

        self._build_details_frame(self._edit_left, existing=data)
        self._build_location_frame(self._edit_right, existing=data)

        self._load_provinces()
        self.after(200, self._start_poll_province)

        save_btn_frame = ctk.CTkFrame(self._edit_right, fg_color="transparent")
        save_btn_frame.pack(fill="x", pady=(20, 10))

        self._prop_save_btn = ctk.CTkButton(save_btn_frame, text="Save Changes",
                                             font=self.body_big_font, fg_color=self.primary_color,
                                             hover_color=self.hover_color, text_color="white",
                                             height=45, corner_radius=6, cursor="hand2",
                                             command=self._save_edit_property)
        self._prop_save_btn.pack(fill="x")

    def _save_edit_property(self):
        if getattr(self, '_prop_is_submitting', False):
            return
        self._prop_is_submitting = True
        if hasattr(self, '_prop_save_btn') and self._prop_save_btn:
            self._prop_save_btn.configure(text="SAVING...", state="disabled")

        def _reenable():
            self._prop_is_submitting = False
            if hasattr(self, '_prop_save_btn') and self._prop_save_btn:
                try:
                    self._prop_save_btn.configure(text="Save Changes", state="normal")
                except Exception:
                    pass

        type_w, _ = self._prop_form_widgets.get("property_type", (None, None))
        name_w, _ = self._prop_form_widgets.get("bh_name", (None, None))
        desc_w, _ = self._prop_form_widgets.get("description", (None, None))
        minstay_w, _ = self._prop_form_widgets.get("min_stay", (None, None))
        rules_w, _ = self._prop_form_widgets.get("rules", (None, None))

        property_type = type_w.get().strip() if type_w else ""
        bh_name = name_w.get().strip() if name_w else ""
        description = desc_w.get("1.0", "end-1c").strip() if desc_w else ""
        min_stay_str = minstay_w.get().strip() if minstay_w else "1"
        try:
            min_stay = int(min_stay_str)
        except ValueError:
            min_stay = 1
        rules = rules_w.get("1.0", "end-1c").strip() if hasattr(rules_w, "get") else (rules_w.get().strip() if rules_w else "")

        payload = {}
        if bh_name:
            payload["bh_name"] = bh_name
        if property_type and property_type != "Select...":
            payload["property_type"] = property_type
        if description:
            payload["description"] = description
        payload["min_stay_months"] = min_stay
        if rules:
            payload["rules"] = rules

        def _do():
            try:
                resp = self.api.patch(f"/boarding-houses/{self._prop_edit_id}", json=payload)
                if resp.status_code == 200:
                    self.after(0, lambda: (self.show_toast("Property updated!", is_error=False),
                                           self.show_property_detail(self._prop_edit_id)))
                else:
                    detail = resp.text
                    try:
                        detail = resp.json().get("detail", detail)
                    except Exception:
                        pass
                    self.after(0, lambda: (_reenable(), self.show_toast(f"Update failed: {detail}", is_error=True)))
            except Exception as e:
                self.after(0, lambda: (_reenable(), self.show_toast(f"Error: {str(e)}", is_error=True)))

        threading.Thread(target=_do, daemon=True).start()

    def _delete_property(self, listing_id):
        dialog = ctk.CTkInputDialog(text=f"Type DELETE to confirm removing this property:",
                                    title="Delete Property")
        result = dialog.get_input()
        if result != "DELETE":
            if result is not None:
                self.show_toast("Deletion cancelled", is_error=True)
            return

        def _do():
            try:
                resp = self.api.delete(f"/boarding-houses/{listing_id}")
                if resp.status_code == 204:
                    self.after(0, lambda: (self.show_toast("Property deleted", is_error=False),
                                           self.show_owner_property()))
                else:
                    detail = resp.text
                    try:
                        detail = resp.json().get("detail", detail)
                    except Exception:
                        pass
                    self.after(0, lambda: self.show_toast(f"Delete failed: {detail}", is_error=True))
            except Exception as e:
                self.after(0, lambda: self.show_toast(f"Error: {str(e)}", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def show_add_room_form(self, listing_id):
        dialog_frame = ctk.CTkToplevel(self)
        dialog_frame.title("Add Room")
        dialog_frame.geometry("400x350")
        dialog_frame.resizable(False, False)
        dialog_frame.transient(self)
        dialog_frame.grab_set()

        main = ctk.CTkFrame(dialog_frame, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main, text="Add New Room", font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 15))

        fields_frame = ctk.CTkFrame(main, fg_color="transparent")
        fields_frame.pack(fill="x")

        room_widgets = {}

        for label, key, ftype, opts, default in [
            ("Room Type", "room_type", "combo", ["Single", "Bed Space", "Private", "Shared"], "Select..."),
            ("Capacity", "capacity", "entry", None, ""),
            ("Price per Month", "price", "entry", None, ""),
            ("Status", "status", "combo", ["available", "occupied", "maintenance"], "available"),
        ]:
            f = ctk.CTkFrame(fields_frame, fg_color="transparent")
            f.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(f, text=label, font=self.body_light_font,
                         text_color=self.text_color).pack(anchor="w", pady=(0, 3))
            if ftype == "combo":
                w = ctk.CTkComboBox(f, values=opts, height=35,
                                    font=self.body_light_font, fg_color=self.fg_color,
                                    border_color=self.entry_border, border_width=1,
                                    button_color=self.primary_color,
                                    button_hover_color=self.hover_color,
                                    dropdown_fg_color=self.fg_color,
                                    dropdown_text_color=self.text_color,
                                    dropdown_hover_color=self.hover_color,
                                    dropdown_font=self.body_light_font,
                                    text_color=self.text_color)
                w.pack(fill="x")
                w.set(default)
            else:
                bg = ctk.CTkFrame(f, height=35, fg_color=self.fg_color,
                                  border_color=self.entry_border, border_width=1, corner_radius=6)
                bg.pack(fill="x")
                bg.pack_propagate(False)
                w = ctk.CTkEntry(bg, placeholder_text=f"Enter {label.lower()}",
                                 height=25, font=self.body_light_font,
                                 fg_color="transparent", border_width=0, text_color=self.text_color)
                w.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
            room_widgets[key] = w

        def submit():
            room_type = room_widgets["room_type"].get().strip()
            capacity_str = room_widgets["capacity"].get().strip()
            price_str = room_widgets["price"].get().strip()
            room_status = room_widgets["status"].get().strip()

            if not room_type or room_type == "Select..." or not capacity_str or not price_str:
                self.show_toast("Please fill in all required fields", is_error=True)
                return
            try:
                capacity = int(capacity_str)
                price = float(price_str)
            except ValueError:
                self.show_toast("Capacity must be a number and price must be valid", is_error=True)
                return

            availability = room_status == "available"

            def _do():
                try:
                    resp = self.api.post("/rooms/", json={
                        "listing_id": listing_id,
                        "room_type": room_type,
                        "capacity": capacity,
                        "price_per_month": price,
                        "availability": availability,
                    })
                    if resp.status_code == 201:
                        self.after(0, lambda: (dialog_frame.destroy(),
                                               self.show_toast("Room added!", is_error=False),
                                               self.show_property_detail(listing_id)))
                    else:
                        detail = resp.text
                        try:
                            detail = resp.json().get("detail", detail)
                        except Exception:
                            pass
                        self.after(0, lambda: self.show_toast(f"Failed: {detail}", is_error=True))
                except Exception as e:
                    self.after(0, lambda: self.show_toast(f"Error: {str(e)}", is_error=True))

            threading.Thread(target=_do, daemon=True).start()

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 0))
        ctk.CTkButton(btn_frame, text="Add Room", font=self.body_big_font,
                      fg_color=self.primary_color, hover_color=self.hover_color,
                      text_color="white", height=40, corner_radius=6, cursor="hand2",
                      command=submit).pack(fill="x")

    def _delete_room(self, room_id, listing_id):
        dialog = ctk.CTkInputDialog(text=f"Type DELETE to confirm removing this room:",
                                    title="Delete Room")
        result = dialog.get_input()
        if result != "DELETE":
            return

        def _do():
            try:
                resp = self.api.delete(f"/rooms/{room_id}")
                if resp.status_code == 204:
                    self.after(0, lambda: (self.show_toast("Room deleted", is_error=False),
                                           self.show_property_detail(listing_id)))
                else:
                    detail = resp.text
                    try:
                        detail = resp.json().get("detail", detail)
                    except Exception:
                        pass
                    self.after(0, lambda: self.show_toast(f"Delete failed: {detail}", is_error=True))
            except Exception as e:
                self.after(0, lambda: self.show_toast(f"Error: {str(e)}", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def show_owner_bookings(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_owner_sidebar_btn("bookings")
        self.build_bookings_content()

    def build_bookings_content(self):
        main_content = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main_content, text="Booking Requests",
                     font=self.title_font, text_color=self.text_color).pack(anchor="w", pady=(0, 20))

        self._booking_main = main_content
        self._booking_data = []
        self._booking_is_loading = False
        self._booking_fetch_id = 0

        # Stats bar
        stats_card_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        stats_card_frame.pack(fill="x", pady=(0, 20))
        stats_card_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="booking_stats")

        stats_keys = [
            ("total", "Total Bookings"),
            ("pending", "Pending"),
            ("active", "Active"),
            ("cancelled", "Cancelled"),
        ]
        accent_map = {"total": None, "pending": self.hover_color, "active": self.primary_color, "cancelled": self.error_red}
        self._booking_stats_labels = {}
        for i, (skey, stitle) in enumerate(stats_keys):
            card = ctk.CTkFrame(stats_card_frame, fg_color=self.secondary_color, corner_radius=6, height=100)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            card.grid_propagate(False)
            if accent_map[skey]:
                accent = ctk.CTkFrame(card, width=4, fg_color=accent_map[skey])
                accent.place(x=0, y=0, relheight=1)
            ctk.CTkLabel(card, text=stitle, font=self.body_big_font,
                         text_color=self.text_color).place(x=15, y=15)
            val_lbl = ctk.CTkLabel(card, text="—", font=self.body_bold_paragraph_font,
                                   text_color=self.text_color)
            val_lbl.place(x=15, y=50)
            self._booking_stats_labels[skey] = val_lbl
            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color=self.hover_color))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=self.secondary_color))

        # Filter bar
        filter_frame = ctk.CTkFrame(main_content, fg_color=self.secondary_color, corner_radius=6, height=50)
        filter_frame.pack(fill="x", pady=(0, 20))
        filter_frame.pack_propagate(False)

        search_icon_lbl = ctk.CTkLabel(filter_frame, image=self.search_icon, text=None)
        search_icon_lbl.pack(side="left", padx=(15, 10))

        self._booking_filter_combo = ctk.CTkComboBox(
            filter_frame, values=["All", "Pending", "Active", "Cancelled"],
            width=140, height=32, font=self.body_paragraph_font,
            fg_color=self.fg_color, border_color=self.entry_border, border_width=1,
            button_color=self.primary_color, button_hover_color=self.hover_color,
            dropdown_fg_color=self.fg_color, dropdown_text_color=self.text_color,
            dropdown_hover_color=self.hover_color, dropdown_font=self.body_light_font,
            text_color=self.text_color,
            command=self._on_booking_filter_change
        )
        self._booking_filter_combo.pack(side="left", padx=(0, 10))
        self._booking_filter_combo.set("All")

        self._booking_search_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="Search by tenant or property...",
            font=self.body_paragraph_font, fg_color="transparent", border_width=0
        )
        self._booking_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        search_btn = ctk.CTkButton(filter_frame, text="Search", font=self.body_paragraph_font,
                                   fg_color=self.primary_color, hover_color=self.hover_color,
                                   text_color="white", height=32, width=100, cursor="hand2",
                                   command=self._do_booking_search)
        search_btn.pack(side="right", padx=(0, 15))

        # Table card (headers rendered now, rows come after fetch)
        table_frame = ctk.CTkFrame(main_content, fg_color=self.secondary_color, corner_radius=6)
        table_frame.pack(fill="x")
        self._booking_table_frame = table_frame

        headers = ["#", "Tenant", "Property \u2192 Room", "Check-in", "Check-out", "Status", "Total / Payment", "Actions"]
        for j, header in enumerate(headers):
            ctk.CTkLabel(table_frame, text=header, font=self.body_paragraph_font,
                         text_color=self.text_color).grid(row=0, column=j, padx=10, pady=(15, 10), sticky="w")
            table_frame.grid_columnconfigure(j, weight=1)

        self._booking_loading_label = ctk.CTkLabel(table_frame, text="Loading bookings...",
                                                   font=self.body_paragraph_font, text_color=self.text_color)
        self._booking_loading_label.grid(row=1, column=0, columnspan=8, padx=15, pady=20, sticky="w")

        self._reload_bookings()

    def _reload_bookings(self):
        if self._booking_is_loading:
            return
        self._booking_is_loading = True
        self._booking_fetch_id += 1
        fetch_id = self._booking_fetch_id

        if self._booking_loading_label:
            self._booking_loading_label.grid()
        if hasattr(self, '_booking_table_rows'):
            for row_widgets in self._booking_table_rows:
                for w in row_widgets:
                    try:
                        w.destroy()
                    except Exception:
                        pass
        self._booking_table_rows = []

        owner_id = getattr(self, 'current_user', {}).get('user_id', 0)
        status_filter = self._booking_filter_combo.get().lower() if self._booking_filter_combo else None
        search_query = self._booking_search_entry.get().strip() if self._booking_search_entry else ""

        def _do():
            try:
                stats_resp = self.api.get(f"/bookings/owner/{owner_id}/stats", timeout=5)
                stats = stats_resp.json() if stats_resp.status_code == 200 else None
            except Exception:
                stats = None

            try:
                url = f"/bookings/owner/{owner_id}/enriched"
                params = []
                if status_filter and status_filter != "all":
                    params.append(f"status={status_filter}")
                if search_query:
                    params.append(f"search={search_query}")
                if params:
                    url += "?" + "&".join(params)
                enriched_resp = self.api.get(url, timeout=5)
                enriched = enriched_resp.json() if enriched_resp.status_code == 200 else []
            except Exception:
                enriched = []

            self.after(0, lambda: self._populate_bookings_content(stats, enriched, fetch_id))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_bookings_content(self, stats, enriched, fetch_id):
        if not self.winfo_exists():
            return
        if fetch_id != self._booking_fetch_id:
            self._booking_is_loading = False
            return
        self._booking_is_loading = False

        if hasattr(self, '_booking_loading_label') and self._booking_loading_label and self._booking_loading_label.winfo_exists():
            self._booking_loading_label.grid_remove()

        self._booking_data = enriched

        # Update stats
        if stats and hasattr(self, '_booking_stats_labels'):
            for k in ("total", "pending", "active", "cancelled"):
                if k in self._booking_stats_labels and self._booking_stats_labels[k].winfo_exists():
                    self._booking_stats_labels[k].configure(text=str(stats.get(f"{k}_count" if k != "total" else "total_bookings", 0)))

        table_frame = self._booking_table_frame if hasattr(self, '_booking_table_frame') else None
        if table_frame is None or not table_frame.winfo_exists():
            return
        if hasattr(self, '_booking_table_rows'):
            for row_widgets in self._booking_table_rows:
                for w in row_widgets:
                    try:
                        w.destroy()
                    except Exception:
                        pass
        self._booking_table_rows = []

        if not enriched:
            empty_lbl = ctk.CTkLabel(table_frame, text="No booking requests found.",
                                     font=self.body_paragraph_font, text_color=self.text_color)
            empty_lbl.grid(row=1, column=0, columnspan=8, padx=15, pady=20, sticky="w")
            self._booking_table_rows.append([empty_lbl])
            return

        self._booking_action_btns = {}
        for r, booking in enumerate(enriched):
            data_row = 1 + r * 2
            sep_row = data_row + 1
            is_last = r == len(enriched) - 1
            row_widgets = []

            booking_id = booking.get("booking_id", "?")
            status = booking.get("status", "pending")
            tenant_name = booking.get("tenant_name", f"Tenant #{booking.get('user_id', '?')}")
            property_name = booking.get("property_name", "Property")
            room_number = booking.get("room_number", "?")
            check_in = booking.get("check_in", "")
            check_out = booking.get("check_out", "")
            total_price = booking.get("total_price", 0)
            payment_status = booking.get("payment_status", "—")

            # Col 0: ID
            id_lbl = ctk.CTkLabel(table_frame, text=str(booking_id), font=self.body_paragraph_font,
                                  text_color=self.text_color)
            id_lbl.grid(row=data_row, column=0, padx=10, pady=(7, 7), sticky="w")
            row_widgets.append(id_lbl)

            # Col 1: Tenant
            tenant_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            tenant_frame.grid(row=data_row, column=1, padx=10, pady=(7, 7), sticky="w")
            pfp = ctk.CTkLabel(tenant_frame, text=None, image=self.pfp_placeholder, width=25, height=25)
            pfp.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(tenant_frame, text=tenant_name, font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left")
            row_widgets.append(tenant_frame)

            # Col 2: Property → Room
            prop_lbl = ctk.CTkLabel(table_frame, text=f"{property_name} \u2192 Room #{room_number}",
                                    font=self.body_paragraph_font, text_color=self.text_color)
            prop_lbl.grid(row=data_row, column=2, padx=10, pady=(7, 7), sticky="w")
            row_widgets.append(prop_lbl)

            # Col 3: Check-in
            ci_lbl = ctk.CTkLabel(table_frame, text=check_in, font=self.body_paragraph_font,
                                  text_color=self.text_color)
            ci_lbl.grid(row=data_row, column=3, padx=10, pady=(7, 7), sticky="w")
            row_widgets.append(ci_lbl)

            # Col 4: Check-out
            co_lbl = ctk.CTkLabel(table_frame, text=check_out, font=self.body_paragraph_font,
                                  text_color=self.text_color)
            co_lbl.grid(row=data_row, column=4, padx=10, pady=(7, 7), sticky="w")
            row_widgets.append(co_lbl)

            # Col 5: Status badge
            if status == "active":
                status_fg = self.primary_color
            elif status == "pending":
                status_fg = self.hover_color
            else:
                status_fg = self.error_red
            status_lbl = ctk.CTkLabel(table_frame, text=status.capitalize(), font=self.body_paragraph_font,
                                      fg_color=status_fg, text_color="white", corner_radius=4, padx=10, pady=2)
            status_lbl.grid(row=data_row, column=5, padx=10, pady=(7, 7), sticky="w")
            row_widgets.append(status_lbl)

            # Col 6: Total / Payment
            payment_text = f"\u20B1{total_price} / {payment_status.capitalize() if payment_status else '—'}"
            pay_lbl = ctk.CTkLabel(table_frame, text=payment_text, font=self.body_paragraph_font,
                                   text_color=self.text_color)
            pay_lbl.grid(row=data_row, column=6, padx=10, pady=(7, 7), sticky="w")
            row_widgets.append(pay_lbl)

            # Col 7: Action buttons
            action_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            action_frame.grid(row=data_row, column=7, padx=10, pady=(7, 7), sticky="w")

            view_btn = ctk.CTkButton(action_frame, text="View", font=self.body_description_font,
                                     fg_color="transparent", text_color=self.primary_color,
                                     hover_color=self.hover_color, cursor="hand2",
                                     command=lambda bid=booking_id: self._owner_show_booking_detail(bid))
            view_btn.pack(side="left", padx=(0, 4))
            row_widgets.append(action_frame)

            btn_info = {}
            if status == "pending":
                approve_btn = ctk.CTkButton(action_frame, text="Approve", font=self.body_description_font,
                                            fg_color=self.primary_color, hover_color=self.hover_color,
                                            text_color="white", cursor="hand2",
                                            command=lambda bid=booking_id: self._owner_booking_action(bid, "active"))
                approve_btn.pack(side="left", padx=(0, 4))
                btn_info["approve"] = approve_btn

                cancel_btn = ctk.CTkButton(action_frame, text="Cancel", font=self.body_description_font,
                                           fg_color=self.error_red, hover_color="#b3302e",
                                           text_color="white", cursor="hand2",
                                           command=lambda bid=booking_id: self._owner_booking_action(bid, "cancelled"))
                cancel_btn.pack(side="left")
                btn_info["cancel"] = cancel_btn

            self._booking_action_btns[booking_id] = btn_info
            self._booking_table_rows.append(row_widgets)

            if not is_last:
                sep = ctk.CTkFrame(table_frame, height=1, fg_color=self.entry_border)
                sep.grid(row=sep_row, column=0, columnspan=8, padx=25, pady=4, sticky="ew")
                self._booking_table_rows.append([sep])

    def _on_booking_filter_change(self, choice):
        self._reload_bookings()

    def _do_booking_search(self):
        self._reload_bookings()

    def _owner_show_booking_detail(self, booking_id):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()

        main_content = ctk.CTkScrollableFrame(self.content_wrapper, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Back button + header
        header_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        back_btn = ctk.CTkLabel(header_frame, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: self.show_owner_bookings())
        back_btn.bind("<Enter>", lambda e: back_btn.configure(image=self.bk_btn_hvr_icon))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(image=self.bk_btn_icon))
        ctk.CTkLabel(header_frame, text=f"Booking #{booking_id}", font=self.title_font,
                     text_color=self.text_color).pack(side="left", padx=10)

        self._booking_detail_main = main_content
        self._booking_detail_id = booking_id

        self._show_loading(text="Loading booking details...")

        def _do():
            try:
                resp = self.api.get(f"/bookings/{booking_id}/owner-detail", timeout=5)
                data = resp.json() if resp.status_code == 200 else None
            except Exception:
                data = None
            self.after(0, lambda: self._populate_booking_detail(data))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_booking_detail(self, data):
        self._hide_loading()
        main_content = self._booking_detail_main
        if not data:
            ctk.CTkLabel(main_content, text="Failed to load booking details.",
                         font=self.body_paragraph_font, text_color=self.error_red).pack(pady=20)
            return

        status = data.get("status", "pending")
        check_in = data.get("check_in", "")
        check_out = data.get("check_out", "")
        total_price = data.get("total_price", 0)
        notes = data.get("notes", "")
        tenant_name = data.get("tenant_name", "N/A")
        tenant_email = data.get("tenant_email", "N/A")
        tenant_phone = data.get("tenant_phone", "N/A")
        property_name = data.get("property_name", "N/A")
        property_type = data.get("property_type", "N/A")
        room_number = data.get("room_number", "N/A")
        property_address = data.get("property_address", "N/A")
        owner_name = data.get("owner_name", "N/A")
        payment_status = data.get("payment_status")
        payment_method = data.get("payment_method")
        payment_amount = data.get("payment_amount")
        payments = data.get("payments", [])
        history = data.get("history", [])

        # Hero card
        hero = ctk.CTkFrame(main_content, fg_color=self.secondary_color, corner_radius=6)
        hero.pack(fill="x", pady=(0, 20))
        hero_inner = ctk.CTkFrame(hero, fg_color="transparent")
        hero_inner.pack(fill="x", padx=20, pady=15)

        if status == "active":
            status_fg = self.primary_color
        elif status == "pending":
            status_fg = self.hover_color
        else:
            status_fg = self.error_red
        status_lbl = ctk.CTkLabel(hero_inner, text=status.capitalize(), font=self.body_paragraph_font,
                                  fg_color=status_fg, text_color="white", corner_radius=4, padx=12, pady=4)
        status_lbl.pack(side="left")

        ctk.CTkLabel(hero_inner, text=f"{check_in} \u2192 {check_out}",
                     font=self.body_paragraph_font, text_color=self.text_color).pack(side="left", padx=(15, 0))
        ctk.CTkLabel(hero_inner, text=f"\u20B1{total_price}", font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(side="right")

        # Two-column body
        body = ctk.CTkFrame(main_content, fg_color="transparent")
        body.pack(fill="x")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        # Tenant card
        tenant_card = ctk.CTkFrame(body, fg_color=self.secondary_color, corner_radius=6)
        tenant_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 20))
        ctk.CTkLabel(tenant_card, text="Tenant Information", font=self.body_big_font,
                     text_color=self.primary_color).pack(anchor="w", padx=15, pady=(15, 10))
        for label, val in [("Name:", tenant_name), ("Email:", tenant_email), ("Phone:", tenant_phone)]:
            row_f = ctk.CTkFrame(tenant_card, fg_color="transparent")
            row_f.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row_f, text=label, font=self.body_light_font,
                         text_color=self.text_color, width=60).pack(side="left")
            ctk.CTkLabel(row_f, text=val, font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=(10, 0))

        # Property card
        prop_card = ctk.CTkFrame(body, fg_color=self.secondary_color, corner_radius=6)
        prop_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 20))
        ctk.CTkLabel(prop_card, text="Property / Room", font=self.body_big_font,
                     text_color=self.primary_color).pack(anchor="w", padx=15, pady=(15, 10))
        for label, val in [("Property:", property_name), ("Type:", property_type),
                            ("Room:", f"#{room_number}"), ("Address:", property_address),
                            ("Owner:", owner_name)]:
            row_f = ctk.CTkFrame(prop_card, fg_color="transparent")
            row_f.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row_f, text=label, font=self.body_light_font,
                         text_color=self.text_color, width=80).pack(side="left")
            ctk.CTkLabel(row_f, text=val, font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=(10, 0))

        # Booking details card (left column row 2)
        detail_card = ctk.CTkFrame(body, fg_color=self.secondary_color, corner_radius=6)
        detail_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 20))
        ctk.CTkLabel(detail_card, text="Booking Details", font=self.body_big_font,
                     text_color=self.primary_color).pack(anchor="w", padx=15, pady=(15, 10))
        for label, val in [("Check-in:", check_in), ("Check-out:", check_out),
                            ("Total Price:", f"\u20B1{total_price}"), ("Notes:", notes or "—")]:
            row_f = ctk.CTkFrame(detail_card, fg_color="transparent")
            row_f.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row_f, text=label, font=self.body_light_font,
                         text_color=self.text_color, width=90).pack(side="left")
            ctk.CTkLabel(row_f, text=str(val), font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=(10, 0))

        # Payment card (right column row 2)
        payment_card = ctk.CTkFrame(body, fg_color=self.secondary_color, corner_radius=6)
        payment_card.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(0, 20))
        ctk.CTkLabel(payment_card, text="Payment", font=self.body_big_font,
                     text_color=self.primary_color).pack(anchor="w", padx=15, pady=(15, 10))
        if payments:
            p = payments[0]
            for label, val in [("Method:", p.get("method", "—")), ("Status:", p.get("status", "—")),
                                ("Amount:", f"\u20B1{p.get('amount', 0)}"),
                                ("Reference:", p.get("reference_no", "—"))]:
                row_f = ctk.CTkFrame(payment_card, fg_color="transparent")
                row_f.pack(fill="x", padx=15, pady=3)
                ctk.CTkLabel(row_f, text=label, font=self.body_light_font,
                             text_color=self.text_color, width=90).pack(side="left")
                ctk.CTkLabel(row_f, text=str(val), font=self.body_paragraph_font,
                             text_color=self.text_color).pack(side="left", padx=(10, 0))
        else:
            ctk.CTkLabel(payment_card, text="No payment records",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(padx=15, pady=(0, 15))

        # Status history
        history_card = ctk.CTkFrame(main_content, fg_color=self.secondary_color, corner_radius=6)
        history_card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(history_card, text="Status History", font=self.body_big_font,
                     text_color=self.primary_color).pack(anchor="w", padx=15, pady=(15, 10))

        if history:
            for h in history:
                h_row = ctk.CTkFrame(history_card, fg_color="transparent")
                h_row.pack(fill="x", padx=25, pady=3)
                dot = ctk.CTkFrame(h_row, width=8, height=8, corner_radius=4, fg_color=self.primary_color)
                dot.pack(side="left", padx=(0, 10))
                old = h.get("old_status", "—") or "—"
                new = h.get("new_status", "—")
                changed_at = h.get("changed_at", "")[:16] if h.get("changed_at") else ""
                ctk.CTkLabel(h_row, text=f"{old} \u2192 {new}",
                             font=self.body_paragraph_font, text_color=self.text_color).pack(side="left")
                ctk.CTkLabel(h_row, text=changed_at, font=self.body_description_font,
                             text_color=self.text_color).pack(side="right")
        else:
            ctk.CTkLabel(history_card, text="No status changes recorded",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(padx=15, pady=(0, 15))

        # Action buttons
        if status == "pending":
            action_bar = ctk.CTkFrame(main_content, fg_color="transparent")
            action_bar.pack(fill="x", pady=(0, 20))
            approve_btn = ctk.CTkButton(action_bar, text="Approve Booking",
                                        font=self.body_big_font, fg_color=self.primary_color,
                                        hover_color=self.hover_color, text_color="white",
                                        height=45, corner_radius=6, cursor="hand2",
                                        command=lambda: self._owner_booking_action(self._booking_detail_id, "active"))
            approve_btn.pack(side="left", padx=(0, 15))
            cancel_btn = ctk.CTkButton(action_bar, text="Cancel Booking",
                                       font=self.body_big_font, fg_color=self.error_red,
                                       hover_color="#b3302e", text_color="white",
                                       height=45, corner_radius=6, cursor="hand2",
                                       command=lambda: self._owner_booking_action(self._booking_detail_id, "cancelled"))
            cancel_btn.pack(side="left")

    def _owner_booking_action(self, booking_id, new_status):
        action_label = "Approving" if new_status == "active" else "Cancelling"
        btns = self._booking_action_btns.get(booking_id, {})
        for btn in btns.values():
            btn.configure(state="disabled")

        user_id = getattr(self, 'current_user', {}).get('user_id', 0)
        def _do():
            try:
                resp = self.api.patch(f"/bookings/{booking_id}/status",
                                      json={"status": new_status, "changed_by_user_id": user_id})
                if resp.status_code == 200:
                    msg = "Booking approved!" if new_status == "active" else "Booking cancelled."
                    self.after(0, lambda: self.show_toast(msg, is_error=False))
                else:
                    detail = resp.text
                    try:
                        detail = resp.json().get("detail", detail)
                    except Exception:
                        pass
                    self.after(0, lambda: self.show_toast(f"Failed: {detail}", is_error=True))
            except Exception as e:
                self.after(0, lambda: self.show_toast(f"Error: {str(e)}", is_error=True))

            def reenable():
                for btn in btns.values():
                    try:
                        btn.configure(state="normal")
                    except Exception:
                        pass
                self.after(100, self.show_owner_bookings)

            self.after(0, reenable)

        threading.Thread(target=_do, daemon=True).start()

    def _show_loading(self, parent=None, text="Please wait..."):
        self._hide_loading()
        target = parent or self.content_wrapper
        overlay = ctk.CTkFrame(target, fg_color=("white", "#1a1a1a"), corner_radius=0)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.lift()
        inner = ctk.CTkFrame(overlay, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")
        loading_lbl = ctk.CTkLabel(inner, text=text, font=self.body_paragraph_font,
                                   text_color=self.text_color)
        loading_lbl.pack()
        self._loading_overlay = overlay

    def _hide_loading(self):
        if hasattr(self, '_loading_overlay') and self._loading_overlay:
            try:
                self._loading_overlay.destroy()
            except Exception:
                pass
            self._loading_overlay = None

    def show_add_property_form(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()

        self._prop_form_widgets = {}
        self._prop_form_files = {"images": [], "permit": None}

        container = ctk.CTkScrollableFrame(self.content_wrapper, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        back_btn = ctk.CTkLabel(header, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: (self._cleanup_uploads(), self.show_owner_property()))
        back_btn.bind("<Enter>", lambda e: back_btn.configure(image=self.bk_btn_hvr_icon))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(image=self.bk_btn_icon))

        ctk.CTkLabel(header, text="Add Property", font=self.alt_title_font,
                     text_color=self.text_color).pack(side="left", padx=10)

        two_col = ctk.CTkFrame(container, fg_color="transparent")
        two_col.pack(fill="both", expand=True)
        two_col.grid_columnconfigure(0, weight=1, uniform="col")
        two_col.grid_columnconfigure(1, weight=1, uniform="col")

        left = ctk.CTkFrame(two_col, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        right = ctk.CTkFrame(two_col, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self._build_details_frame(left)
        self._build_location_frame(right)

        self._load_provinces()
        self.after(200, self._start_poll_province)

    def _enable_debug_right_click(self):
        _last_time = [None]
        def _show_debug(event):
            if _last_time[0] == event.time:
                return
            _last_time[0] = event.time
            w = event.widget
            info = []
            info.append(f"Class: {w.winfo_class()}")
            try:
                info.append(f"Geo: {w.winfo_geometry()}")
            except Exception:
                pass
            try:
                info.append(f"Req: {w.winfo_reqwidth()}x{w.winfo_reqheight()}")
            except Exception:
                pass
            # walk up and find a _debug_tag + full chain
            tag = getattr(w, '_debug_tag', '')
            chain = [f"{w.winfo_class()}({w.winfo_name()})"]
            if not tag:
                try:
                    p = w.winfo_parent()
                    while p:
                        pw = w._nametowidget(p)
                        cls = pw.winfo_class()
                        nm = pw.winfo_name()
                        chain.append(f"{cls}({nm})")
                        tag = getattr(pw, '_debug_tag', '')
                        if tag:
                            break
                        p = pw.winfo_parent()
                except Exception:
                    pass
            if tag:
                info.append(f"Tag: {tag}")
            info.append(f"Chain: {' ← '.join(chain)}")
            msg = " | ".join(info)
            print(f"[DEBUG] {msg}")

        self.bind_all("<Button-3>", _show_debug, add="+")

    def _build_details_frame(self, parent, existing=None):
        ctk.CTkLabel(parent, text="Property Details", font=self.body_bold_paragraph_font,
                     text_color=self.primary_color).pack(anchor="w", pady=(0, 15))

        fields = [
            ("property_type", "Type of Property", "combo",
             ["Boarding House", "Dormitory", "Apartment", "Bed Space", "Condo Unit"]),
            ("bh_name", "Name of Property", "entry", None),
        ]
        for key, label, ftype, opts in fields:
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(f, text=label, font=self.body_light_font,
                         text_color=self.text_color).pack(anchor="w", pady=(0, 3))
            if ftype == "combo":
                w = ctk.CTkComboBox(f, values=opts, height=40,
                                    font=self.body_light_font, fg_color=self.fg_color,
                                    border_color=self.entry_border, border_width=1,
                                    button_color=self.primary_color,
                                    button_hover_color=self.hover_color,
                                    dropdown_fg_color=self.fg_color,
                                    dropdown_text_color=self.text_color,
                                    dropdown_hover_color=self.hover_color,
                                    dropdown_font=self.body_light_font,
                                    text_color=self.text_color)
                w.pack(fill="x")
                w.set("Select...")
            else:
                bg = ctk.CTkFrame(f, height=40, fg_color=self.fg_color,
                                  border_color=self.entry_border, border_width=1, corner_radius=6)
                bg.pack(fill="x")
                bg.pack_propagate(False)
                w = ctk.CTkEntry(bg, placeholder_text=f"Enter {label.lower()}",
                                 height=30, font=self.body_light_font,
                                 fg_color="transparent", border_width=0, text_color=self.text_color)
                w.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
            err = ctk.CTkLabel(f, text="", height=14, font=self.inline_error_font,
                               text_color=self.error_red)
            err.pack(anchor="w", padx=5)
            self._prop_form_widgets[key] = (w, err)

        # ── Amenities (rewritten — clean grid layout) ──
        amenities_frame = ctk.CTkFrame(parent, fg_color="transparent", border_color="#000000")
        amenities_frame._debug_tag = "amenities_section"
        amenities_frame.pack(fill="x")
        amenities_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(amenities_frame, text="Amenities", font=self.body_light_font,
                     text_color=self.text_color).grid(row=0, column=0, sticky="w", pady=(0, 0))

        self._amenity_chips_frame = ctk.CTkFrame(amenities_frame, fg_color="transparent")
        self._amenity_chips_frame.grid(row=1, column=0, sticky="ew", pady=(0, 0))
        self._amenity_chips_frame.grid_columnconfigure(0, weight=1)

        self._selected_amenities = []
        self._amenity_chip_btns = dict()

        # "Selected:" label + value — DIRECTLY below chips (row 2), zero gap
        amenities_selected_frame = ctk.CTkFrame(amenities_frame, fg_color="transparent")
        amenities_selected_frame.grid(row=2, column=0, sticky="ew", pady=(0, 0))
        amenities_selected_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(amenities_selected_frame, text="Selected:",
                     font=self.body_description_font,
                     text_color=self.text_color).grid(row=0, column=0, sticky="w")
        self._amenity_entry = ctk.CTkLabel(amenities_selected_frame, text=" ",
                                           font=self.body_light_font,
                                           text_color=self.text_color,
                                           anchor="w", justify="left")
        self._amenity_entry.grid(row=0, column=1, sticky="ew", padx=5)

        # Error label — at the VERY BOTTOM (row 3)
        amenities_err = ctk.CTkLabel(amenities_frame, text="", height=14,
                                     font=self.inline_error_font,
                                     text_color=self.error_red)
        amenities_err.grid(row=3, column=0, sticky="w", padx=5, pady=(0, 0))
        self._prop_form_widgets["amenities"] = (self._amenity_entry, amenities_err)
        self._load_amenity_options()

        if not existing:
            self._build_initial_rooms_section(parent)

        desc_frame = ctk.CTkFrame(parent, fg_color="transparent")
        desc_frame._debug_tag = "description_section"
        desc_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(desc_frame, text="Description", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        desc_bg = ctk.CTkFrame(desc_frame, height=120, fg_color=self.fg_color,
                               border_color=self.entry_border, border_width=1, corner_radius=6)
        desc_bg.pack(fill="x")
        desc_bg.pack_propagate(False)
        desc_txt = ctk.CTkTextbox(desc_bg, height=100, font=self.body_light_font,
                                  fg_color="transparent", border_width=0, text_color=self.text_color)
        desc_txt.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.85, anchor="center")
        desc_err = ctk.CTkLabel(desc_frame, text="", height=14, font=self.inline_error_font,
                                text_color=self.error_red)
        desc_err.pack(anchor="w", padx=5)
        self._prop_form_widgets["description"] = (desc_txt, desc_err)

        # Minimum Stay
        minstay_frame = ctk.CTkFrame(parent, fg_color="transparent")
        minstay_frame._debug_tag = "minstay_section"
        minstay_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(minstay_frame, text="Minimum Stay (months)", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        minstay_combo = ctk.CTkComboBox(minstay_frame, height=40,
                                        values=["1", "3", "6", "12"],
                                        font=self.body_light_font, fg_color=self.fg_color,
                                        border_color=self.entry_border, border_width=1,
                                        button_color=self.primary_color,
                                        button_hover_color=self.hover_color,
                                        dropdown_fg_color=self.fg_color,
                                        dropdown_text_color=self.text_color,
                                        dropdown_hover_color=self.hover_color,
                                        dropdown_font=self.body_light_font,
                                        text_color=self.text_color)
        minstay_combo.pack(fill="x")
        minstay_combo.set("Select...")
        minstay_err = ctk.CTkLabel(minstay_frame, text="", height=14, font=self.inline_error_font,
                                   text_color=self.error_red)
        minstay_err.pack(anchor="w", padx=5)
        self._prop_form_widgets["min_stay"] = (minstay_combo, minstay_err)

        # House Rules
        rules_frame = ctk.CTkFrame(parent, fg_color="transparent")
        rules_frame._debug_tag = "rules_section"
        rules_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(rules_frame, text="House Rules", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        rules_bg = ctk.CTkFrame(rules_frame, height=80, fg_color=self.fg_color,
                                border_color=self.entry_border, border_width=1, corner_radius=6)
        rules_bg.pack(fill="x")
        rules_bg.pack_propagate(False)
        rules_txt = ctk.CTkTextbox(rules_bg, height=60, font=self.body_light_font,
                                   fg_color="transparent", border_width=0, text_color=self.text_color)
        rules_txt.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.85, anchor="center")
        rules_err = ctk.CTkLabel(rules_frame, text="", height=14, font=self.inline_error_font,
                                 text_color=self.error_red)
        rules_err.pack(anchor="w", padx=5)
        self._prop_form_widgets["rules"] = (rules_txt, rules_err)

        self._build_upload_zone(parent, "Upload Images", max_files=10)
        self._build_upload_zone(parent, "Upload Permit Images", is_permit=True)

        # Pre-fill values in edit mode
        if existing:
            if "property_type" in self._prop_form_widgets:
                w, _ = self._prop_form_widgets["property_type"]
                if existing.get("property_type"):
                    w.set(existing["property_type"])
            if "bh_name" in self._prop_form_widgets:
                w, _ = self._prop_form_widgets["bh_name"]
                if existing.get("bh_name"):
                    w.delete(0, "end")
                    w.insert(0, existing["bh_name"])
            if "description" in self._prop_form_widgets:
                w, _ = self._prop_form_widgets["description"]
                if existing.get("description"):
                    w.delete("1.0", "end")
                    w.insert("1.0", existing["description"])
            if "min_stay" in self._prop_form_widgets:
                w, _ = self._prop_form_widgets["min_stay"]
                if existing.get("min_stay_months"):
                    w.set(str(existing["min_stay_months"]))
            if "rules" in self._prop_form_widgets:
                w, _ = self._prop_form_widgets["rules"]
                if existing.get("rules"):
                    w.delete("1.0", "end")
                    w.insert("1.0", existing["rules"])

    def _build_initial_rooms_section(self, parent):
        rooms_frame = ctk.CTkFrame(parent, fg_color="transparent")
        rooms_frame._debug_tag = "initial_rooms_section"
        rooms_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(rooms_frame, text="Initial Rooms (optional)", font=self.body_bold_paragraph_font,
                     text_color=self.primary_color).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(rooms_frame, text="Add room pricing now, or skip and add later",
                     font=self.body_description_font, text_color=self.text_color).pack(anchor="w", pady=(0, 8))

        room_headers = ctk.CTkFrame(rooms_frame, fg_color="transparent")
        room_headers.pack(fill="x", pady=(0, 3))
        room_headers.grid_columnconfigure((0, 1, 2), weight=1)
        for j, h in enumerate(["Room Type", "Capacity", "Price/Month"]):
            ctk.CTkLabel(room_headers, text=h, font=self.body_description_font,
                         text_color=self.text_color).grid(row=0, column=j, padx=2)

        room_types = ["Single", "Bed Space", "Private", "Shared", "Double Deck"]
        self._initial_room_rows = []
        for row_idx in range(3):
            row_f = ctk.CTkFrame(rooms_frame, fg_color="transparent")
            row_f.pack(fill="x", pady=3)
            row_f.grid_columnconfigure((0, 1, 2), weight=1)

            type_w = ctk.CTkComboBox(row_f, values=room_types, height=35,
                                      font=self.body_light_font, fg_color=self.fg_color,
                                      border_color=self.entry_border, border_width=1,
                                      button_color=self.primary_color,
                                      button_hover_color=self.hover_color,
                                      dropdown_fg_color=self.fg_color,
                                      dropdown_text_color=self.text_color,
                                      dropdown_hover_color=self.hover_color,
                                      dropdown_font=self.body_light_font,
                                      text_color=self.text_color)
            type_w.grid(row=0, column=0, padx=2)
            type_w.set("")

            cap_w = ctk.CTkEntry(row_f, placeholder_text="e.g. 2", height=35,
                                  font=self.body_light_font, fg_color=self.fg_color,
                                  border_color=self.entry_border, border_width=1,
                                  text_color=self.text_color)
            cap_w.grid(row=0, column=1, padx=2)

            price_w = ctk.CTkEntry(row_f, placeholder_text="e.g. 5000", height=35,
                                    font=self.body_light_font, fg_color=self.fg_color,
                                    border_color=self.entry_border, border_width=1,
                                    text_color=self.text_color)
            price_w.grid(row=0, column=2, padx=2)

            self._initial_room_rows.append({
                "type": type_w, "capacity": cap_w, "price": price_w
            })

    def _load_amenity_options(self):
        self._amenity_loading_lbl = ctk.CTkLabel(
            self._amenity_chips_frame, text="Loading amenities...",
            font=self.body_light_font, text_color=self.text_color)
        self._amenity_loading_lbl.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        def fetch():
            try:
                resp = self.api.get("/amenities/", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    names = [a.get("amenity_name", "") for a in data if a.get("amenity_name")]
                    if names:
                        self.after(0, lambda: self._build_amenity_chips(names))
                        return
            except Exception:
                pass
            self.after(0, lambda: self._show_amenity_error())

        threading.Thread(target=fetch, daemon=True).start()

    def _show_amenity_error(self):
        if hasattr(self, '_amenity_chips_frame') and self._amenity_chips_frame.winfo_exists():
            for w in self._amenity_chips_frame.winfo_children():
                w.destroy()
            ctk.CTkLabel(self._amenity_chips_frame, text="Failed to load amenities",
                         font=self.body_light_font, text_color=self.error_red).grid(row=0, column=0, padx=5, pady=5)

    def _build_amenity_chips(self, amenities):
        # Guard: user may have navigated away during async fetch
        if not hasattr(self, '_amenity_chips_frame') or not self._amenity_chips_frame.winfo_exists():
            return
        # Destroy loading label
        for w in self._amenity_chips_frame.winfo_children():
            w.destroy()
        # Build chip rows: 3 chips per row using grid
        for idx, name in enumerate(amenities):
            row = idx // 3
            col = idx % 3
            if col == 0:
                # First chip in row: configure grid columns for this row
                self._amenity_chips_frame.grid_rowconfigure(row, weight=0)
            chip = ctk.CTkButton(self._amenity_chips_frame, text=name,
                                 font=self.body_description_font,
                                 fg_color="transparent", text_color=self.text_color,
                                 border_width=1, border_color=self.entry_border,
                                 hover_color=self.hover_color, corner_radius=12,
                                 height=26,
                                 command=lambda n=name: self._toggle_amenity_chip(n, None))
            chip.grid(row=row, column=col, padx=(0, 4), pady=2, sticky="w")
            self._amenity_chip_btns[name] = {"btn": chip, "id": None, "selected": False}
        # Configure remaining grid columns for each row
        for r in range((len(amenities) + 2) // 3):
            self._amenity_chips_frame.grid_columnconfigure((0, 1, 2), weight=0)

    def _toggle_amenity_chip(self, name, aid):
        info = self._amenity_chip_btns.get(name)
        if not info:
            return
        info["selected"] = not info["selected"]
        btn = info["btn"]
        if info["selected"]:
            btn.configure(fg_color=self.primary_color, text_color="white", border_width=0)
            if name not in self._selected_amenities:
                self._selected_amenities.append(name)
        else:
            btn.configure(fg_color="transparent", text_color=self.text_color, border_width=1,
                          border_color=self.entry_border)
            if name in self._selected_amenities:
                self._selected_amenities.remove(name)
        if self._amenity_entry:
            text = ", ".join(self._selected_amenities) if self._selected_amenities else " "
            self._amenity_entry.configure(text=text)

    def _build_upload_zone(self, parent, label_text, is_permit=False, max_files=1):
        key = "permit" if is_permit else "images"
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text=label_text, font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))

        drop_zone = ctk.CTkFrame(frame, fg_color=self.secondary_color,
                                 height=200, border_width=2, border_color=self.entry_border)
        drop_zone.pack(fill="x")
        drop_zone.pack_propagate(False)

        drop_zone.drop_target_register(tkinterdnd2.DND_FILES)
        drop_zone.dnd_bind('<<Drop>>', lambda e: self._handle_file_drop(
            e, key, is_permit, max_files, drop_zone, placeholder, choose_btn, frame
        ))
        drop_zone.dnd_bind('<<DropEnter>>',
            lambda e: (
                drop_zone.configure(fg_color=self.hover_color, border_color=self.primary_color),
                "copy"
            )[1])
        drop_zone.dnd_bind('<<DropPosition>>', lambda e: "copy")
        drop_zone.dnd_bind('<<DropLeave>>',
            lambda e: drop_zone.configure(fg_color=self.secondary_color, border_color=self.entry_border))

        placeholder = ctk.CTkFrame(drop_zone, fg_color="transparent")
        placeholder.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(placeholder, text=None, image=self.upload_image_icon).pack(pady=(0, 5))
        ctk.CTkLabel(placeholder, text="Drop your files here", font=self.body_paragraph_font,
                     text_color=self.text_color).pack(pady=(0, 5))

        choose_btn = ctk.CTkButton(placeholder, text="Choose File", font=self.body_light_font,
                                   fg_color=self.primary_color, hover_color=self.hover_color,
                                   text_color="white", corner_radius=4, width=110, height=32,
                                   command=lambda: self._upload_choose_files(key, is_permit, max_files, drop_zone, placeholder, choose_btn, frame))
        choose_btn.pack(pady=(5, 0))

        self._prop_form_widgets[f"upload_{key}"] = (drop_zone, placeholder)

    def _upload_to_server(self, file_path):
        try:
            with open(file_path, "rb") as f:
                resp = self.api.post("/photos/upload", files={"file": f})
            if resp.status_code == 200:
                data = resp.json()
                return data.get("url"), data.get("filename")
        except Exception:
            pass
        return None, None

    def _upload_file_entry(self, entry, key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame):
        def upload():
            url, filename = self._upload_to_server(entry["path"])
            def update():
                entry["url"] = url
                entry["filename"] = filename
                entry["status"] = "done" if url else "failed"
                self._rebuild_thumbnails(key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame)
            self.after(0, update)
        threading.Thread(target=upload, daemon=True).start()

    def _add_uploaded_files(self, file_paths, key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame, skip_upload=False):
        existing = self._prop_form_files.get(key, [])
        if is_permit:
            new_entries = [{"path": p, "url": None, "status": "done" if skip_upload else "uploading", "filename": None} for p in file_paths[:1]]
            existing = new_entries
        else:
            new_entries = [{"path": p, "url": None, "status": "done" if skip_upload else "uploading", "filename": None} for p in file_paths]
            existing = (existing + new_entries)[:max_files]
        self._prop_form_files[key] = existing
        self._rebuild_thumbnails(key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame)
        if not skip_upload:
            for entry in new_entries[:max_files]:
                self._upload_file_entry(entry, key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame)

    def _rebuild_thumbnails(self, key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame):
        files = self._prop_form_files.get(key, [])
        if not files:
            for w in drop_zone.winfo_children():
                if w is not placeholder:
                    w.destroy()
            drop_zone.configure(height=200, border_width=2, border_color=self.entry_border)
            placeholder.place(relx=0.5, rely=0.5, anchor="center")
            return

        placeholder.place_forget()
        for w in drop_zone.winfo_children():
            if w is not placeholder:
                w.destroy()

        drop_zone.configure(height=250, border_width=0)

        inner = ctk.CTkFrame(drop_zone, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=(5, 3))

        ctk.CTkButton(inner, text="Choose File", font=self.body_light_font,
                       fg_color=self.primary_color, hover_color=self.hover_color,
                       text_color="white", corner_radius=4, width=110, height=32,
                       command=lambda: self._upload_choose_files(key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame)
                       ).pack(side="bottom", pady=(0, 6))

        thumb_frame = ctk.CTkScrollableFrame(inner, orientation="horizontal",
                                             fg_color="transparent",
                                             scrollbar_button_color=self.entry_border,
                                             scrollbar_button_hover_color=self.hover_color)
        thumb_frame.pack(fill="both", expand=True)

        for entry in files:
            item = ctk.CTkFrame(thumb_frame, fg_color="transparent")
            item.pack(side="left", padx=4)

            fpath = entry.get("path", "")
            status = entry.get("status", "done")
            upload_url = entry.get("url")

            if status == "uploading":
                status_lbl = ctk.CTkLabel(item, text="Uploading...", font=self.body_description_font,
                                          text_color=self.primary_color)
                status_lbl.pack()
                ctk_img = self.upload_image_icon
            elif status == "failed":
                status_lbl = ctk.CTkLabel(item, text="Failed", font=self.body_description_font,
                                          text_color=self.error_red)
                status_lbl.pack()
                retry_btn = ctk.CTkButton(item, text="Retry", font=self.body_description_font,
                                          fg_color=self.primary_color, hover_color=self.hover_color,
                                          text_color="white", width=50, height=22, corner_radius=3,
                                          command=lambda e=entry: self._upload_file_entry(e, key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame))
                retry_btn.pack(pady=(2, 0))
                ctk_img = self.upload_image_icon
            else:
                try:
                    img = Image.open(fpath).convert("RGBA")
                    img.thumbnail((180, 180))
                    ctk_img = ctk.CTkImage(img, size=(img.width, img.height))
                except Exception:
                    ctk_img = self.upload_image_icon

            ctk.CTkLabel(item, text=None, image=ctk_img).pack()

            def make_remove(e, k=key, per=is_permit, mx=max_files, dz=drop_zone, ph=placeholder, cb=choose_btn, pf=parent_frame):
                def rm():
                    if e.get("url") and e.get("filename"):
                        try:
                            self.api.delete(f"/photos/upload/{e['filename']}")
                        except Exception:
                            pass
                    lst = self._prop_form_files.get(k, [])
                    if e in lst:
                        lst.remove(e)
                    self._prop_form_files[k] = lst
                    self._rebuild_thumbnails(k, per, mx, dz, ph, cb, pf)
                return rm

            if status != "uploading":
                rm_btn = ctk.CTkButton(item, text="x", width=22, height=22,
                                       fg_color=self.error_red, hover_color="#b3302e",
                                       text_color="white", corner_radius=11,
                                       font=self.body_description_font,
                                       command=make_remove(entry))
                rm_btn.place(relx=1.0, y=0, anchor="ne", x=2)

    def _upload_choose_files(self, key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame):
        raw_files = filedialog.askopenfilenames(
            title=f"Select {'Permit' if is_permit else 'Property'} Images",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp")]
        )
        if not raw_files:
            return

        max_size = 5 * 1024 * 1024
        valid = []
        skipped = 0
        for f in raw_files:
            if os.path.getsize(f) <= max_size:
                valid.append(f)
            else:
                skipped += 1
        if skipped:
            self.show_toast(f"{skipped} file(s) skipped (over 5MB)", is_error=True)
        if not valid:
            return

        self._add_uploaded_files(valid, key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame)

    def _handle_file_drop(self, event, key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame):
        drop_zone.configure(fg_color=self.secondary_color, border_color=self.entry_border)
        raw = event.data
        items = self.tk.splitlist(raw)
        valid_exts = (".png", ".jpg", ".jpeg", ".webp")
        max_size = 5 * 1024 * 1024
        dropped = []
        for item in items:
            path = unquote(urlparse(item).path) if item.startswith("file:") else item
            if path.lower().endswith(valid_exts) and os.path.isfile(path) and os.path.getsize(path) <= max_size:
                dropped.append(path)

        if not dropped:
            return "copy"

        self._add_uploaded_files(dropped, key, is_permit, max_files, drop_zone, placeholder, choose_btn, parent_frame)
        return "copy"

    def _build_location_frame(self, parent, existing=None):
        ctk.CTkLabel(parent, text="Location", font=self.body_bold_paragraph_font,
                     text_color=self.primary_color).pack(anchor="w", pady=(0, 15))

        prov_frame = ctk.CTkFrame(parent, fg_color="transparent")
        prov_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(prov_frame, text="Province", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        self.province_menu = ctk.CTkComboBox(prov_frame, values=[], height=40,
                                             font=self.body_light_font, fg_color=self.fg_color,
                                             border_color=self.entry_border, border_width=1,
                                             button_color=self.primary_color,
                                             button_hover_color=self.hover_color,
                                             dropdown_fg_color=self.fg_color,
                                             dropdown_text_color=self.text_color,
                                             dropdown_hover_color=self.hover_color,
                                             dropdown_font=self.body_light_font,
                                             text_color=self.text_color,
                                             command=self.on_province_selected)
        self.province_menu.pack(fill="x")
        self.province_menu.configure(state="normal")
        self.province_menu.set("Select Province...")
        self.province_menu._entry.bind("<FocusIn>", lambda e: self.province_menu.set("")
                                      if self.province_menu.get() == "Select Province..." else None)
        self.province_menu.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.province_menu, "Select Province..."))
        self.province_dropdown = self._make_dropdown(self.province_menu, values=["Select Province..."],
                                                      autocomplete=True, command=self.on_province_selected)
        self.province_err = ctk.CTkLabel(prov_frame, text="", height=14, font=self.inline_error_font,
                                         text_color=self.error_red)
        self.province_err.pack(anchor="w", padx=5)
        self._prop_form_widgets["province"] = (self.province_menu, self.province_err)

        def _province_blur(e=None):
            def check():
                val = self.province_menu.get().strip()
                opts = getattr(self, "province_options", [])
                if opts and val and val not in opts and not val.startswith("Select"):
                    self.province_menu.set("Select Province...")
            self.after(300, check)
        self.province_menu._entry.bind("<FocusOut>", _province_blur, add="+")

        city_frame = ctk.CTkFrame(parent, fg_color="transparent")
        city_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(city_frame, text="City", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        self.city_menu = ctk.CTkComboBox(city_frame, values=[], height=40,
                                         font=self.body_light_font, fg_color=self.fg_color,
                                         border_color=self.entry_border, border_width=1,
                                         button_color=self.primary_color,
                                         button_hover_color=self.hover_color,
                                         dropdown_fg_color=self.fg_color,
                                         dropdown_text_color=self.text_color,
                                         dropdown_hover_color=self.hover_color,
                                         dropdown_font=self.body_light_font,
                                         text_color=self.text_color,
                                         command=self.on_city_selected)
        self.city_menu.pack(fill="x")
        self.city_menu.set("Select City...")
        self.city_menu._entry.bind("<FocusIn>", lambda e: self.city_menu.set("")
                                   if self.city_menu.get() == "Select City..." else None)
        self.city_menu.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.city_menu, "Select City..."))
        self.city_dropdown = self._make_dropdown(self.city_menu, values=["Select City..."],
                                                  autocomplete=True, command=self.on_city_selected)
        self.city_err = ctk.CTkLabel(city_frame, text="", height=14, font=self.inline_error_font,
                                     text_color=self.error_red)
        self.city_err.pack(anchor="w", padx=5)
        self._prop_form_widgets["city"] = (self.city_menu, self.city_err)

        brgy_frame = ctk.CTkFrame(parent, fg_color="transparent")
        brgy_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(brgy_frame, text="Barangay", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        self.barangay_menu = ctk.CTkComboBox(brgy_frame, values=[], height=40,
                                             font=self.body_light_font, fg_color=self.fg_color,
                                             border_color=self.entry_border, border_width=1,
                                             button_color=self.primary_color,
                                             button_hover_color=self.hover_color,
                                             dropdown_fg_color=self.fg_color,
                                             dropdown_text_color=self.text_color,
                                             dropdown_hover_color=self.hover_color,
                                             dropdown_font=self.body_light_font,
                                             text_color=self.text_color,
                                             command=lambda c: self.barangay_menu.set(c))
        self.barangay_menu.pack(fill="x")
        self.barangay_menu.set("Select Barangay...")
        self.barangay_menu._entry.bind("<FocusIn>", lambda e: self.barangay_menu.set("")
                                       if self.barangay_menu.get() == "Select Barangay..." else None)
        self.barangay_menu.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.barangay_menu, "Select Barangay..."))
        self.barangay_dropdown = self._make_dropdown(self.barangay_menu, values=["Select Barangay..."],
                                                     autocomplete=True,
                                                     command=lambda c: self.barangay_menu.set(c))
        self.barangay_err = ctk.CTkLabel(brgy_frame, text="", height=14, font=self.inline_error_font,
                                         text_color=self.error_red)
        self.barangay_err.pack(anchor="w", padx=5)
        self._prop_form_widgets["barangay"] = (self.barangay_menu, self.barangay_err)

        zip_frame = ctk.CTkFrame(parent, fg_color="transparent")
        zip_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(zip_frame, text="Zip Code", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        zip_bg = ctk.CTkFrame(zip_frame, height=40, fg_color=self.fg_color,
                              border_color=self.entry_border, border_width=1, corner_radius=6)
        zip_bg.pack(fill="x")
        zip_bg.pack_propagate(False)
        zip_entry = ctk.CTkEntry(zip_bg, placeholder_text="Enter zip code",
                                 height=30, font=self.body_light_font,
                                 fg_color="transparent", border_width=0, text_color=self.text_color)
        zip_entry.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        zip_err = ctk.CTkLabel(zip_frame, text="", height=14, font=self.inline_error_font,
                               text_color=self.error_red)
        zip_err.pack(anchor="w", padx=5)
        self._prop_form_widgets["zip_code"] = (zip_entry, zip_err)

        street_frame = ctk.CTkFrame(parent, fg_color="transparent")
        street_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(street_frame, text="Address", font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w", pady=(0, 3))
        street_bg = ctk.CTkFrame(street_frame, height=80, fg_color=self.fg_color,
                                 border_color=self.entry_border, border_width=1, corner_radius=6)
        street_bg.pack(fill="x")
        street_bg.pack_propagate(False)
        street_txt = ctk.CTkTextbox(street_bg, height=60, font=self.body_light_font,
                                    fg_color="transparent", border_width=0, text_color=self.text_color)
        street_txt.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.85, anchor="center")
        street_err = ctk.CTkLabel(street_frame, text="", height=14, font=self.inline_error_font,
                                  text_color=self.error_red)
        street_err.pack(anchor="w", padx=5)
        self._prop_form_widgets["street"] = (street_txt, street_err)

        self._prop_create_btn = ctk.CTkButton(parent, text="Create Property",
                                               font=self.body_big_font, fg_color=self.primary_color,
                                               hover_color=self.hover_color, text_color="white",
                                               height=45, corner_radius=6, cursor="hand2",
                                               command=self._submit_property)
        self._prop_create_btn.pack(pady=(20, 10))

    def _load_provinces(self):
        cached = getattr(self, "_cached_provinces", None)
        if cached is not None:
            self.province_options = cached
            if cached and hasattr(self, "province_dropdown") and self.province_menu.winfo_exists():
                self.province_dropdown.configure(values=cached)
            self._cached_provinces = None
            return

        def fetch():
            try:
                resp = self.api.get("/locations/provinces", timeout=5)
                if resp.status_code == 200:
                    options = resp.json().get("options", [])
                    self.province_options = options
                    if options and hasattr(self, "province_dropdown") and self.province_menu.winfo_exists():
                        def update():
                            if self.province_menu.winfo_exists():
                                self.province_dropdown.configure(values=options)
                        self.after(0, update)
            except Exception:
                pass

        threading.Thread(target=fetch, daemon=True).start()

    def _set_location_opts(self, key, options):
        if key == "city":
            self.city_dropdown.configure(values=options)
        elif key == "barangay":
            self.barangay_dropdown.configure(values=options)

    def _start_poll_province(self):
        def poll():
            if not self.province_menu.winfo_exists():
                return
            val = self.province_menu.get().strip()
            opts = getattr(self, "province_options", [])
            if val and val in opts and not val.startswith("Select") and val != getattr(self, "_last_province_val", ""):
                self._last_province_val = val
                self._handle_province_selected(val)
            self.after(500, poll)
        poll()

    def on_province_selected(self, choice):
        self._handle_province_selected(choice)

    def _handle_province_selected(self, choice):
        if not choice or not choice.strip() or choice.startswith("Select"):
            return

        self.province_menu.set(choice)
        self._last_province_val = choice

        self.barangay_menu.set("Select Barangay...")
        self.barangay_dropdown.configure(values=["Select Barangay..."])

        self.city_menu.set("Loading cities...")
        self.city_dropdown.configure(values=["Loading..."])

        self._start_poll_city()

        def fetch():
            try:
                resp = self.api.get(f"/locations/cities?province={quote(choice)}", timeout=5)
                if resp.status_code == 200:
                    options = resp.json().get("options", [])
                    self._city_options = options

                    def update():
                        if self.city_menu.winfo_exists():
                            self.city_dropdown.configure(values=options)
                            if options:
                                self.city_menu.set("")
                            else:
                                self.city_menu.set("No Cities Found")
                    self.after(0, update)
                else:
                    self._city_options = []
                    self.after(0, lambda: self.city_menu.set("No Cities Found") if self.city_menu.winfo_exists() else None)
            except Exception:
                self._city_options = []
                self.after(0, lambda: self.show_toast("Failed to load cities", is_error=True))

        threading.Thread(target=fetch, daemon=True).start()

    def _start_poll_city(self):
        def poll():
            if not self.city_menu.winfo_exists():
                return
            val = self.city_menu.get().strip()
            opts = getattr(self, "_city_options", [])
            if val and val in opts and not val.startswith("Select") and not val.startswith("Loading") and val != getattr(self, "_last_city_val", ""):
                self._last_city_val = val
                self._handle_city_selected(val)
            self.after(500, poll)
        poll()

    def on_city_selected(self, choice):
        self._handle_city_selected(choice)

    def _handle_city_selected(self, choice):
        if not choice or not choice.strip() or choice.startswith("Select") or choice.startswith("Loading"):
            return

        self.city_menu.set(choice)
        self._last_city_val = choice

        self.barangay_menu.set("Loading Barangays...")
        self.barangay_dropdown.configure(values=["Loading..."])

        def fetch():
            try:
                resp = self.api.get(f"/locations/barangays?city={quote(choice)}", timeout=5)
                if resp.status_code == 200:
                    options = resp.json().get("options", [])

                    def update():
                        if self.barangay_menu.winfo_exists():
                            self.barangay_dropdown.configure(values=options)
                            if options:
                                self.barangay_menu.set("")
                            else:
                                self.barangay_menu.set("No Barangay Found")
                    self.after(0, update)
                else:
                    self.after(0, lambda: self.barangay_menu.set("No Barangay Found") if self.barangay_menu.winfo_exists() else None)
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to load barangays", is_error=True))

        threading.Thread(target=fetch, daemon=True).start()

    def _validate_property_form(self):
        valid = True
        for key, (widget, err_lbl) in self._prop_form_widgets.items():
            if key.startswith("upload_"):
                continue
            if key == "amenities":
                if not getattr(self, '_selected_amenities', []):
                    err_lbl.configure(text="Select at least one amenity")
                    valid = False
                else:
                    err_lbl.configure(text="")
                continue
            if key == "rules":
                err_lbl.configure(text="")
                continue
            if isinstance(widget, ctk.CTkComboBox):
                val = widget.get().strip()
                if not val or val in ("Select...", "No options available", "Select Province...", "Select City...", "Select Barangay..."):
                    err_lbl.configure(text="This field is required")
                    valid = False
                    continue
            elif isinstance(widget, ctk.CTkTextbox):
                val = widget.get("1.0", "end-1c").strip()
                if not val:
                    err_lbl.configure(text="This field is required")
                    valid = False
                    continue
            elif isinstance(widget, ctk.CTkEntry):
                val = widget.get().strip()
                if not val:
                    err_lbl.configure(text="This field is required")
                    valid = False
                    continue
            err_lbl.configure(text="")
        return valid

    def _cleanup_uploads(self):
        for key in ("permit", "images"):
            entries = self._prop_form_files.get(key) or []
            for entry in entries:
                if entry.get("url") and entry.get("filename"):
                    try:
                        self.api.delete(f"/photos/upload/{entry['filename']}")
                    except Exception:
                        pass
        self._prop_form_files = {"images": [], "permit": None}

    def _submit_property(self):
        if getattr(self, '_prop_is_submitting', False):
            return
        if not self._validate_property_form():
            self.show_toast("Please fill in all required fields", is_error=True)
            return

        for entry in self._prop_form_files.get("permit", []):
            if entry.get("status") != "done":
                self.show_toast("Please wait for permit upload to complete", is_error=True)
                return

        pending = [e for e in self._prop_form_files.get("images", []) if e.get("status") != "done"]
        if pending:
            self.show_toast("Please wait for image uploads to complete", is_error=True)
            return

        if not any(e.get("status") == "done" for e in self._prop_form_files.get("permit", [])):
            self.show_toast("Please upload a permit image", is_error=True)
            return

        if not any(e.get("status") == "done" for e in self._prop_form_files.get("images", [])):
            self.show_toast("Please upload at least one property image", is_error=True)
            return

        self._prop_is_submitting = True
        if hasattr(self, '_prop_create_btn') and self._prop_create_btn:
            self._prop_create_btn.configure(text="CREATING...", state="disabled")

        self._show_loading(text="Creating property...")

        def _reenable():
            self._prop_is_submitting = False
            if hasattr(self, '_prop_create_btn') and self._prop_create_btn:
                try:
                    self._prop_create_btn.configure(text="Create Property", state="normal")
                except Exception:
                    pass

        owner_id = getattr(self, 'current_user', {}).get('user_id', 0)

        def _do():
            try:
                permit_entries = [e for e in self._prop_form_files.get("permit", []) if e.get("status") == "done"]
                permit_url = permit_entries[0]["url"] if permit_entries else ""

                image_entries = [e for e in self._prop_form_files.get("images", []) if e.get("status") == "done"]
                image_urls = [e["url"] for e in image_entries]

                type_w, _ = self._prop_form_widgets.get("property_type", (None, None))
                name_w, _ = self._prop_form_widgets.get("bh_name", (None, None))
                desc_w, _ = self._prop_form_widgets.get("description", (None, None))
                minstay_w, _ = self._prop_form_widgets.get("min_stay", (None, None))
                rules_w, _ = self._prop_form_widgets.get("rules", (None, None))
                prov_w, _ = self._prop_form_widgets.get("province", (None, None))
                city_w, _ = self._prop_form_widgets.get("city", (None, None))
                brgy_w, _ = self._prop_form_widgets.get("barangay", (None, None))
                zip_w, _ = self._prop_form_widgets.get("zip_code", (None, None))
                street_w, _ = self._prop_form_widgets.get("street", (None, None))

                property_type = type_w.get().strip() if type_w else ""
                bh_name = name_w.get().strip() if name_w else ""
                description = desc_w.get("1.0", "end-1c").strip() if desc_w else ""
                min_stay_str = minstay_w.get().strip() if minstay_w else "1"
                try:
                    min_stay = int(min_stay_str)
                except ValueError:
                    min_stay = 1
                rules = rules_w.get("1.0", "end-1c").strip() if hasattr(rules_w, "get") else (rules_w.get().strip() if rules_w else "")

                province = prov_w.get().strip() if prov_w else ""
                city = city_w.get().strip() if city_w else ""
                barangay = brgy_w.get().strip() if brgy_w else ""
                zip_code = zip_w.get().strip() if zip_w else ""

                if hasattr(street_w, "get"):
                    street = street_w.get("1.0", "end-1c").strip()
                else:
                    street = street_w.get().strip() if street_w else ""

                location_payload = {
                    "province": province,
                    "city": city,
                    "barangay": barangay,
                    "street": street,
                    "zip_code": zip_code,
                }
                loc_resp = self.api.post("/locations/", json=location_payload)
                if loc_resp.status_code != 201:
                    detail = loc_resp.text
                    try:
                        detail = loc_resp.json().get("detail", detail)
                    except Exception:
                        pass
                    self._cleanup_uploads()
                    self.after(0, lambda: (self._hide_loading(), _reenable(), self.show_toast(f"Failed to create location: {detail}", is_error=True)))
                    return
                location_id = loc_resp.json().get("location_id")

                bh_payload = {
                    "bh_name": bh_name,
                    "property_type": property_type if property_type != "Select..." else "",
                    "description": description,
                    "permit_url": permit_url,
                    "min_stay_months": min_stay,
                    "rules": rules,
                    "location_id": location_id,
                }
                bh_resp = self.api.post("/boarding-houses/", json=bh_payload)
                if bh_resp.status_code != 201:
                    detail = bh_resp.text
                    try:
                        detail = bh_resp.json().get("detail", detail)
                    except Exception:
                        pass
                    self._cleanup_uploads()
                    self.after(0, lambda: (self._hide_loading(), _reenable(), self.show_toast(f"Failed to create property: {detail}", is_error=True)))
                    return
                listing_id = bh_resp.json().get("listing_id")

                for amenity_name in getattr(self, '_selected_amenities', []):
                    self.api.post("/amenities/link-to-listing", json={
                        "listing_id": listing_id,
                        "amenity_name": amenity_name,
                    })

                for i, img_url in enumerate(image_urls):
                    self.api.post("/photos/from_url", json={
                        "entity_type": "listing",
                        "entity_id": listing_id,
                        "photo_url": img_url,
                        "is_primary": i == 0,
                        "sort_order": i,
                    })

                room_rows = getattr(self, '_initial_room_rows', [])
                for row in room_rows:
                    room_type = row["type"].get().strip()
                    cap_str = row["capacity"].get().strip()
                    price_str = row["price"].get().strip()
                    if room_type and cap_str and price_str:
                        try:
                            self.api.post("/rooms/", json={
                                "listing_id": listing_id,
                                "room_type": room_type,
                                "capacity": int(cap_str),
                                "price_per_month": float(price_str),
                                "availability": True,
                            })
                        except Exception:
                            pass

                self.after(0, lambda: (self._hide_loading(), self.show_toast("Property created successfully!", is_error=False)))
                self.after(500, self.show_owner_property)

            except Exception as e:
                self._cleanup_uploads()
                self.after(0, lambda: (self._hide_loading(), _reenable(), self.show_toast(f"Error: {str(e)}", is_error=True)))

        threading.Thread(target=_do, daemon=True).start()


    def _owner_fetch_notif_count(self):
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
            self.after(0, lambda: self._owner_update_notif_badge(unread))

        threading.Thread(target=_do, daemon=True).start()

    def _owner_update_notif_badge(self, count):
        if hasattr(self, 'owner_notif_badge') and self.owner_notif_badge:
            if count > 0:
                self.owner_notif_badge.configure(text=str(count) if count <= 99 else "99+")
            else:
                self.owner_notif_badge.configure(text="")

    def _owner_toggle_user_menu(self):
        if hasattr(self, '_user_menu') and self._user_menu and self._user_menu.winfo_ismapped():
            self._hide_user_menu()
        else:
            self._show_user_menu(
                parent=self.form_container,
                anchor=self.owner_profile_frame,
                form_container=self.form_container,
                items=[
                    ("Account Settings", self.menu_profile_icon,  self.show_account_settings),
                    None,
                    ("My Bookings",    self.menu_bookings_icon, self.show_owner_bookings),
                    ("Notifications",  self.notification_icon,  self.show_notifications_page),
                    None,
                    ("Logout",         self.menu_logout_icon,   self._handle_logout),
                ],
            )
            if hasattr(self, 'owner_profile_chevron'):
                self.owner_profile_chevron.configure(text="▴")
