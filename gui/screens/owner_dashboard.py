import threading
import customtkinter as ctk


class OwnerDashboardMixin:
    def show_owner_dashboard(self):
        print("[DEBUG] Showing: Owner Dashboard")
        self.clear_container()

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{int(w * 0.85)}x{int(h * 0.85)}")
        self.resizable(True, True)

        self.is_sidebar_expanded = True

        # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        self._build_owner_nav()
        self._build_owner_sidebar()

        # Content wrapper for sidebar animation
        self.content_wrapper = ctk.CTkFrame(self.form_container,
                                            fg_color="transparent"
                                            )
        self.content_wrapper.pack(fill="both", expand=True, padx=(260, 10), pady=20)

        # --- Dashboard Main Content ---
        self._set_active_sidebar_btn("dashboard")
        self.build_dashboard_content()

    def build_dashboard_content(self):
        self.main_content = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=20, pady=10)

        owner_id = getattr(self, 'current_user', {}).get('user_id', 0)

        self._owner_dashboard_cards_data = {
            "total_listings": "0",
            "pending_review": "0",
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
            ("Total Income", "\u20B10"),
            ("Recent Booking", "recent_booking"),
        ]

        self._owner_stat_labels = {}
        for i, (title, key) in enumerate(card_info):
            card = ctk.CTkFrame(cards_frame, fg_color=self.secondary_color,
                                corner_radius=6, height=120)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            card.pack_propagate(False)
            card.grid_propagate(False)

            val = self._owner_dashboard_cards_data.get(key, "\u20B10") if key != "\u20B10" else "\u20B10"
            ctk.CTkLabel(card, text=title, font=self.body_big_font,
                         text_color=self.text_color).grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")
            val_lbl = ctk.CTkLabel(card, text=val, font=self.body_bold_paragraph_font,
                                   text_color=self.text_color)
            val_lbl.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
            self._owner_stat_labels[key] = val_lbl

            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color=self.hover_color))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=self.secondary_color))

        # Bottom Cards Frame
        bottom_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(0, 20))
        bottom_frame.grid_columnconfigure((0, 1), weight=1, uniform="bottom_card")

        # Payment History Card
        payment_card = ctk.CTkFrame(bottom_frame, fg_color=self.secondary_color, corner_radius=6)
        payment_card.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="new")
        payment_card.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(payment_card, text="Payment History", font=self.body_big_font,
                     text_color=self.text_color).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        payment_headers = ["Payment Date", "Amount", "Status"]
        for j, h in enumerate(payment_headers):
            ctk.CTkLabel(payment_card, text=h, font=self.body_paragraph_font,
                         text_color=self.text_color).grid(row=1, column=j, padx=15, pady=5, sticky="w")

        payment_rows = [
            ("2024-01-15", "\u20B13,500", "Paid"),
            ("2024-02-15", "\u20B13,500", "Pending"),
            ("2024-03-15", "\u20B13,500", "Paid"),
        ]
        for r, (date, amount, status) in enumerate(payment_rows):
            bottom_pady = 12 if r == len(payment_rows) - 1 else 7
            ctk.CTkLabel(payment_card, text=date, font=self.body_light_font,
                         text_color=self.text_color).grid(row=2+r, column=0, padx=15, pady=(7, bottom_pady), sticky="w")
            ctk.CTkLabel(payment_card, text=amount, font=self.body_light_font,
                         text_color=self.text_color).grid(row=2+r, column=1, padx=15, pady=(7, bottom_pady), sticky="w")
            ctk.CTkLabel(payment_card, text=status, font=self.body_light_font,
                         text_color=self.text_color).grid(row=2+r, column=2, padx=15, pady=(7, bottom_pady), sticky="w")

        payment_btn_row = 2 + len(payment_rows)
        payment_card.grid_rowconfigure(payment_btn_row, weight=1)
        payment_btn_frame = ctk.CTkFrame(payment_card, fg_color="transparent")
        payment_btn_frame.grid(row=payment_btn_row, column=0, columnspan=3, padx=15, pady=(0, 12), sticky="sew")

        view_all_btn = ctk.CTkButton(payment_btn_frame, text="See Invoice",
                                     font=self.body_paragraph_font,
                                     fg_color="transparent",
                                     text_color=self.primary_color,
                                     border_width=1,
                                     border_color=self.entry_border,
                                     hover_color=self.hover_color,
                                     width=100, height=30)
        view_all_btn.pack(side="right")

        # Maintenance Status Card
        maint_card = ctk.CTkFrame(bottom_frame, fg_color=self.secondary_color, corner_radius=6)
        maint_card.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="new")

        ctk.CTkLabel(maint_card, text="Maintenance Status", font=self.body_big_font,
                     text_color=self.text_color).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

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
            self.after(0, self._populate_owner_dashboard_cards)

        threading.Thread(target=_do, daemon=True).start()

    def _populate_owner_dashboard_cards(self):
        data = self._owner_dashboard_cards_data
        if "total_listings" in self._owner_stat_labels:
            self._owner_stat_labels["total_listings"].configure(text=data["total_listings"])
        if "pending_review" in self._owner_stat_labels:
            self._owner_stat_labels["pending_review"].configure(text=data["pending_review"])
        if "recent_booking" in self._owner_stat_labels:
            self._owner_stat_labels["recent_booking"].configure(text=data["recent_booking"])

        maint_items = data.get("maint_items", [])
        if not maint_items:
            ctk.CTkLabel(self._maint_card, text="No maintenance requests",
                         font=self.body_light_font, text_color=self.text_color).grid(row=1, column=0, padx=15, pady=(7, 12), sticky="w")

        self.maint_detail_frames = {}
        for r, item in enumerate(maint_items):
            bottom_pady = 12 if r == len(maint_items) - 1 else 7
            req_title = item.get("title", f"Request #{item.get('request_id', '?')}")
            req_status = item.get("status", "unknown")
            req_desc = item.get("description", "")

            req_lbl = ctk.CTkLabel(self._maint_card, text=req_title, font=self.body_paragraph_font,
                                   text_color=self.text_color, cursor="hand2")
            req_lbl.grid(row=1+r*2, column=0, padx=15, pady=(7, bottom_pady), sticky="w")
            req_lbl.bind("<Button-1>", lambda e, t=req_title: self.toggle_maint_detail(t))

            ctk.CTkLabel(self._maint_card, text=req_status, font=self.body_light_font,
                         text_color=self.text_color).grid(row=1+r*2, column=1, padx=15, pady=(7, bottom_pady), sticky="w")

            detail_frame = ctk.CTkFrame(self._maint_card, fg_color="transparent")
            detail_frame.grid(row=2+r*2, column=0, columnspan=2, padx=25, pady=(0, 7), sticky="ew")
            detail_frame.grid_remove()

            ctk.CTkLabel(detail_frame, text=req_desc, font=self.body_light_font,
                         text_color=self.text_color, wraplength=600, justify="left").pack(anchor="w")

            self.maint_detail_frames[req_title] = detail_frame



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
                                                fg_color=self.secondary_color,
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

        self.owner_profile_frame = ctk.CTkFrame(self.owner_nav_bar_frame,
                                                fg_color="transparent"
                                                )
        self.owner_profile_frame.pack(side="right", padx=25, pady=10)

        self.owner_nav_pfp = ctk.CTkLabel(self.owner_profile_frame,
                                          text=None,
                                          image=self.pfp_placeholder,
                                          width=25,
                                          height=25
                                          )
        self.owner_nav_pfp.pack(side="left", padx=(0, 12))

        self.owner_profile_text_frame = ctk.CTkFrame(self.owner_profile_frame,
                                                     fg_color="transparent"
                                                     )
        self.owner_profile_text_frame.pack(side="left")

        user_name = getattr(self, 'current_user', {}).get('name', 'Owner')
        user_id = getattr(self, 'current_user', {}).get('user_id', '?')

        self.owner_name_label = ctk.CTkLabel(self.owner_profile_text_frame,
                                             text=user_name,
                                             font=self.body_light_font,
                                             text_color=self.text_color
                                             )
        self.owner_name_label.grid(row=0, column=0, sticky="w")

        self.owner_uid_label = ctk.CTkLabel(self.owner_profile_text_frame,
                                            text=f"UID: {user_id}",
                                            font=self.body_light_font,
                                            text_color=self.text_color
                                            )
        self.owner_uid_label.grid(row=1, column=0, sticky="w")

    def _build_owner_sidebar(self):
        self.sidebar_main_frame = ctk.CTkFrame(self.form_container,
                                               fg_color=self.secondary_color,
                                               width=250,
                                               corner_radius=0,
                                               border_color=self.entry_border,
                                               border_width=1
                                               )
        self.sidebar_main_frame.place(x=0, y=0, relheight=1.0)
        self.sidebar_main_frame.pack_propagate(False)

        self.sidebar_logo_frame = ctk.CTkFrame(self.sidebar_main_frame,
                                               fg_color="transparent"
                                               )
        self.sidebar_logo_frame.pack(fill="x", pady=(20, 0))

        self.sidebar_hamburger_btn = ctk.CTkButton(self.sidebar_logo_frame,
                                                   image=self.hamburg_menu_icon,
                                                   text=None,
                                                   fg_color="transparent",
                                                   hover_color=self.hover_color,
                                                   width=25,
                                                   height=15,
                                                   command=self.animate_sidebar
                                                   )
        self.sidebar_hamburger_btn.pack(side="left", padx=15)

        self.logo_image = ctk.CTkLabel(self.sidebar_logo_frame,
                                       text=None,
                                       image=self.logo
                                       )
        self.logo_image.pack(side="left")

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

        self.logout_btn = ctk.CTkButton(self.menu_btn_frame,
                                        text="Logout",
                                        width=230,
                                        height=40,
                                        hover_color=self.hover_color,
                                        fg_color="transparent",
                                        text_color=self.text_color,
                                        font=self.body_big_font,
                                        command=self._handle_logout
                                        )
        self.logout_btn.grid(row=4, column=0, padx=10, pady=(30, 0))

    def _set_active_sidebar_btn(self, active):
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
        self._set_active_sidebar_btn("tenants")
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
        if hasattr(self, '_loading_tenants_label') and self._loading_tenants_label:
            self._loading_tenants_label.destroy()
            self._loading_tenants_label = None

        if not tenant_data:
            tenant_data = [
                ("No tenants yet", "", "", "", ""),
            ]

        table_frame = self._tenants_table_frame
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
        self._set_active_sidebar_btn("property")
        self.build_property_content()

    def build_property_content(self):
        main_content = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main_content, text="My Properties",
                     font=self.title_font, text_color=self.text_color).pack(anchor="w", pady=(0, 20))

        self._property_main = main_content
        self._loading_prop = ctk.CTkLabel(main_content, text="Loading properties...",
                                          font=self.body_paragraph_font, text_color=self.text_color)
        self._loading_prop.pack(pady=20)

        owner_id = getattr(self, 'current_user', {}).get('user_id', 0)

        def _do():
            try:
                resp = self.api.get(f"/boarding-houses/owner/{owner_id}", timeout=5)
                listings = resp.json() if resp.status_code == 200 else []
            except Exception:
                listings = []
            self.after(0, lambda: self._populate_property_content(listings))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_property_content(self, listings):
        if hasattr(self, '_loading_prop') and self._loading_prop:
            self._loading_prop.destroy()
            self._loading_prop = None

        main_content = self._property_main
        for listing in listings:
            card = ctk.CTkFrame(main_content, fg_color=self.secondary_color, corner_radius=6)
            card.pack(fill="x", pady=5)

            ctk.CTkLabel(card, text=listing.get('bh_name', 'Untitled'),
                         font=self.body_big_font, text_color=self.text_color).pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(card, text=listing.get('status', 'unknown'),
                         font=self.body_paragraph_font, text_color=self.text_color).pack(side="right", padx=15, pady=10)

        if not listings:
            ctk.CTkLabel(main_content, text="No properties yet. Create one from the dashboard.",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(pady=20)

    def show_owner_bookings(self):
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self._set_active_sidebar_btn("bookings")
        self.build_bookings_content()

    def build_bookings_content(self):
        main_content = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main_content, text="Booking Requests",
                     font=self.title_font, text_color=self.text_color).pack(anchor="w", pady=(0, 20))

        self._booking_main = main_content
        self._loading_bookings = ctk.CTkLabel(main_content, text="Loading bookings...",
                                              font=self.body_paragraph_font, text_color=self.text_color)
        self._loading_bookings.pack(pady=20)

        owner_id = getattr(self, 'current_user', {}).get('user_id', 0)

        def _do():
            try:
                resp = self.api.get(f"/bookings/owner/{owner_id}", timeout=5)
                bookings = resp.json() if resp.status_code == 200 else []
            except Exception:
                bookings = []
            self.after(0, lambda: self._populate_bookings_content(bookings))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_bookings_content(self, bookings):
        if hasattr(self, '_loading_bookings') and self._loading_bookings:
            self._loading_bookings.destroy()
            self._loading_bookings = None

        main_content = self._booking_main

        if not bookings:
            ctk.CTkLabel(main_content, text="No booking requests yet.",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(pady=20)
            return

        for booking in bookings:
            card = ctk.CTkFrame(main_content, fg_color=self.secondary_color, corner_radius=6)
            card.pack(fill="x", pady=5)

            info = f"Booking #{booking.get('booking_id')} — Status: {booking.get('status')}"
            ctk.CTkLabel(card, text=info, font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=15, pady=10)
