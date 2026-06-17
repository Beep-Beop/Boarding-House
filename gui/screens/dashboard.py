import customtkinter as ctk
import requests
import threading
from PIL import Image
import io
from src.logger import logger
from datetime import datetime


class DashboardMixin:
    def show_tenant_dashboard(self):
        print("[DEBUG] Showing: Tenant Dashboard")
        self.clear_container()

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{int(w * 0.85)}x{int(h * 0.85)}")
        self.resizable(True, True)

        self.is_sidebar_expanded = True
        self.is_search_expanded = False

        # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        # Main Dashboard

        # Nav Bar
        self.nav_bar_frame = ctk.CTkFrame(self.form_container,
                                          fg_color="transparent",
                                          height=60,
                                          border_width=1,
                                          border_color=self.entry_border
                                          )
        self.nav_bar_frame.pack(side="top", fill="x")

        self.bg_hamburg_menu = ctk.CTkButton(self.nav_bar_frame,
                                             image=self.hamburg_menu_icon,
                                             text=None,
                                             fg_color="transparent",
                                             hover_color=self.hover_color,
                                             width=25,
                                             height=15,
                                             command=self.animate_sidebar
                                             )
        self.bg_hamburg_menu.pack(side="left", padx=15, pady=(20, 25))

        self.bg_logo = ctk.CTkLabel(self.nav_bar_frame,
                                    text=None,
                                    image=self.logo
                                    )
        self.bg_logo.pack(side="left", pady=(15, 20))

        self.search_bg_frame = ctk.CTkFrame(self.nav_bar_frame,
                                            height=40,
                                            width=40,
                                            fg_color="transparent",
                                            )
        self.search_bg_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.search_bg_frame.pack_propagate(False)

        self.search_btn = ctk.CTkButton(self.search_bg_frame,
                                        text=None,
                                        image=self.search_icon,
                                        width=40,
                                        height=40,
                                        fg_color="transparent",
                                        hover_color=self.hover_color,
                                        command=self.animate_search_bar
                                        )
        self.search_btn.pack(side="left")

        self.search_entry = ctk.CTkEntry(self.search_bg_frame,
                                         placeholder_text="Search for boarding houses, cities",
                                         font=self.body_light_font,
                                         height=40,
                                         border_width=0,
                                         fg_color="transparent"
                                         )
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        # Notification Bell
        self.notif_bell_frame = ctk.CTkFrame(self.nav_bar_frame, fg_color="transparent")
        self.notif_bell_frame.pack(side="right", padx=(0, 5))

        self.notif_bell_btn = ctk.CTkLabel(self.notif_bell_frame, text="",
                                           image=self.notification_icon, cursor="hand2")
        self.notif_bell_btn.pack(side="left", padx=5)
        self.notif_bell_btn.bind("<Button-1>", lambda e: self.show_notifications_page())

        # Badge
        self.notif_badge = ctk.CTkLabel(self.notif_bell_frame, text="",
                                        width=16, height=16, corner_radius=8,
                                        fg_color=self.error_red, text_color="white",
                                        font=ctk.CTkFont(size=9, weight="bold"))
        self.notif_badge.place(x=18, y=-2)

        self.profile_frame = ctk.CTkFrame(self.nav_bar_frame,
                                          fg_color="transparent"
                                          )
        self.profile_frame.pack(side="right", padx=25, pady=10)

        self.nav_pfp = ctk.CTkLabel(self.profile_frame,
                                          text=None,
                                          image=self.pfp_placeholder,
                                          width=25,
                                          height=25
                                          )
        self.nav_pfp.pack(side="left", padx=(0, 12))

        self.profile_text_frame = ctk.CTkFrame(self.profile_frame,
                                               fg_color="transparent"
                                               )
        self.profile_text_frame.pack(side="left")

        user_name = getattr(self, 'current_user', {}).get('name', 'User')
        user_id = getattr(self, 'current_user', {}).get('user_id', '?')

        self.name_label = ctk.CTkLabel(self.profile_text_frame,
                                       text=user_name,
                                       font=self.body_light_font,
                                       text_color=self.text_color
                                       )
        self.name_label.grid(row=0, column=0, sticky="w")

        self.uid_label = ctk.CTkLabel(self.profile_text_frame,
                                      text=f"UID: {user_id}",
                                      font=self.body_light_font,
                                      text_color=self.text_color
                                      )
        self.uid_label.grid(row=1, column=0, sticky="w")

        # Chevron indicator for clickability
        self.profile_chevron = ctk.CTkLabel(self.profile_text_frame, text="▾",
                                            font=self.body_light_font, text_color=self.text_color)
        self.profile_chevron.grid(row=0, column=1, padx=(4, 0), sticky="w")

        # Make entire profile frame clickable
        self.profile_frame.bind("<Button-1>", lambda e: self._toggle_user_menu())
        self.profile_frame.configure(cursor="hand2")
        for child in self.profile_frame.winfo_children():
            child.bind("<Button-1>", lambda e: self._toggle_user_menu())

        # Main Content

        self.content_wrapper = ctk.CTkFrame(self.form_container,
                                            fg_color="transparent"
                                            )
        self.content_wrapper.pack(fill="both", expand=True, padx=(260, 10), pady=20)

        # Welcome Banner
        self.welcome_frame = ctk.CTkFrame(self.content_wrapper, fg_color=self.secondary_color,
                                          corner_radius=8, height=80,
                                          border_width=1, border_color=self.entry_border)
        self.welcome_frame.pack(fill="x", pady=(0, 15))
        self.welcome_frame.pack_propagate(False)

        inner_welcome = ctk.CTkFrame(self.welcome_frame, fg_color="transparent")
        inner_welcome.pack(fill="both", padx=20, pady=15)

        accent = ctk.CTkFrame(inner_welcome, width=4, fg_color=self.primary_color, corner_radius=2)
        accent.pack(side="left", fill="y", padx=(0, 12))

        welcome_text = f"Welcome back, {user_name}!"
        today_str = datetime.now().strftime("%A, %B %d, %Y")
        ctk.CTkLabel(inner_welcome, text=welcome_text, font=self.body_bold_paragraph_font,
                     text_color=self.text_color).pack(anchor="w")
        ctk.CTkLabel(inner_welcome, text=today_str, font=self.body_light_font,
                     text_color=self.text_color).pack(anchor="w")

        # Quick Stats Row
        self.stats_row_frame = ctk.CTkFrame(self.content_wrapper, fg_color="transparent")
        self.stats_row_frame.pack(fill="x", pady=(0, 15))
        self.stats_row_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="stats")

        stats_cards = [
            ("Active Bookings", "0", self.primary_color),
            ("Saved Favorites", "0", self.hover_color),
            ("Total Reviews", "0", self.text_color),
        ]
        self._stat_labels = {}
        for i, (title, val, accent_color) in enumerate(stats_cards):
            card = ctk.CTkFrame(self.stats_row_frame, fg_color=self.secondary_color,
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

        self.filter_scroll_frame = ctk.CTkScrollableFrame(self.content_wrapper,
                                                          orientation="horizontal",
                                                          height=50,
                                                          fg_color="transparent"
                                                          )
        self.filter_scroll_frame.pack(fill="x")

        filters = ["All", "Wi-Fi Included", "With Meals", "Furnished", "Near University", "Pet Friendly", "Aircon"]

        self.filter_buttons = {}

        for f in filters:
            btn = ctk.CTkButton(self.filter_scroll_frame,
                                text=f,
                                height=32,
                                corner_radius=16,
                                fg_color=self.secondary_color,
                                text_color=self.text_color,
                                hover_color=self.hover_color,
                                command=lambda f_name=f: self.toggle_filter(f_name)
                                )
            btn.pack(side="left", padx=(0, 10))
            self.filter_buttons[f] = btn

        self.filter_buttons["All"].configure(fg_color=self.primary_color, text_color="white")

        self.main_content_frame = ctk.CTkScrollableFrame(self.content_wrapper,
                                               fg_color="transparent"
                                               )
        self.main_content_frame.pack(fill="both", expand=True)

        self.main_content_frame.bind_all("<Button-4>", lambda e: self.main_content_frame._parent_canvas.yview("scroll", -1, "units") if hasattr(self.main_content_frame, "_parent_canvas") else None)
        self.main_content_frame.bind_all("<Button-5>", lambda e: self.main_content_frame._parent_canvas.yview("scroll", 1, "units") if hasattr(self.main_content_frame, "_parent_canvas") else None)

        self.cards_grid_frame = ctk.CTkFrame(self.main_content_frame,
                                             fg_color="transparent"
                                             )
        self.cards_grid_frame.pack(anchor="n")
        self.cards_grid_frame.bind(
            "<Configure>",
            lambda e: self._update_scroll_region()
        )

        self._dashboard_offset = 0
        self._dashboard_limit = 20
        self.cards_list = []

        self.load_more_btn = ctk.CTkButton(self.main_content_frame, text="Load More",
                                           font=self.body_paragraph_font,
                                           fg_color=self.primary_color, hover_color=self.hover_color,
                                           text_color="white", width=200, height=40,
                                           command=self._load_more)
        self.load_more_btn.pack(pady=20)

        self.main_content_frame.bind("<Configure>", self.reflow_cards)
        self.after(100, self.reflow_cards)

        self._load_initial_dashboard()
        self._fetch_notif_count()
        self._fetch_dashboard_stats()

        # Menu Frame
        self.sidebar_main_frame = ctk.CTkFrame(self.form_container,
                                     fg_color="transparent",
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
        self.menu_btn_frame.grid_columnconfigure(0, weight=1)

        self.explore_btn = ctk.CTkButton(self.menu_btn_frame,
                                            text="Explore",
                                            width=230,
                                            height=40,
                                            hover_color=self.hover_color,
                                            fg_color="transparent",
                                            text_color=self.text_color,
                                            font=self.body_big_font
                                            )
        self.explore_btn.grid(row=0, column=0, padx=10, pady=(0, 30))

        self.viewing = ctk.CTkButton(self.menu_btn_frame,
                                         text="Viewing",
                                         width=230,
                                         height=40,
                                         hover_color=self.hover_color,
                                         fg_color="transparent",
                                         text_color=self.text_color,
                                         font=self.body_big_font
                                         )
        self.viewing.grid(row=1, column=0, padx=10, pady=(0, 30))

        self.message_btn = ctk.CTkButton(self.menu_btn_frame,
                                          text="Message",
                                          width=230,
                                          height=40,
                                          hover_color=self.hover_color,
                                          fg_color="transparent",
                                          text_color=self.text_color,
                                          font=self.body_big_font
                                          )
        self.message_btn.grid(row=2, column=0, padx=10, pady=(0, 30))

        self.favorite_btn = ctk.CTkButton(self.menu_btn_frame,
                                            text="Favorite",
                                            width=230,
                                            height=40,
                                            hover_color=self.hover_color,
                                            fg_color="transparent",
                                            text_color=self.text_color,
                                            font=self.body_big_font
                                            )
        self.favorite_btn.grid(row=3, column=0, padx=10, pady=(0, 30))

        self.bookings_btn = ctk.CTkButton(self.menu_btn_frame,
                                          text="My Bookings",
                                          width=230,
                                          height=40,
                                          hover_color=self.hover_color,
                                          fg_color="transparent",
                                          text_color=self.text_color,
                                          font=self.body_big_font,
                                          command=self.show_student_bookings
                                          )
        self.bookings_btn.grid(row=4, column=0, padx=10, pady=(0, 30))

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
        self.logout_btn.grid(row=5, column=0, padx=10, pady=(30, 0))

    # Tenant Dashboard Helper

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

    def create_listing_card(self, parent_frame, house_data):
        card = ctk.CTkFrame(parent_frame,
                            width=400,
                            height=450,
                            fg_color=self.secondary_color,
                            corner_radius=12,
                            border_width=1,
                            border_color=self.entry_border
                            )
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
                                    fg_color=self.fg_color, text_color=self.text_color, corner_radius=6)
        card_img.pack(pady=(10, 0), padx=5)

        card_name = ctk.CTkLabel(card,
                                 text=house_data["name"],
                                 font=self.body_bold_paragraph_font,
                                 text_color=self.text_color)
        card_name.pack(anchor="w", padx=15, pady=(10, 0))

        card_location = ctk.CTkLabel(card,
                                     text=house_data["location"],
                                     font=self.body_paragraph_font,
                                     text_color=self.text_color)
        card_location.pack(anchor="w", padx=15)

        card_amenities = ctk.CTkLabel(card,
                                      text=house_data["amenities"],
                                      font=self.body_paragraph_font,
                                      text_color=self.text_color)
        card_amenities.pack(anchor="w", padx=15)

        card_title = ctk.CTkLabel(card,
                                  text="Description",
                                  font=self.body_description_font,
                                  text_color=self.text_color)
        card_title.pack(anchor="w", padx=15, pady=(0, 5))

        card_bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
        card_bottom_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        listing_id = house_data.get("id")
        bookmark_btn = ctk.CTkButton(card_bottom_frame,
                                     text=None,
                                     image=self.bookmark_icon,
                                     width=25, height=25,
                                     fg_color="transparent",
                                     hover_color=self.hover_color,
                                     command=lambda lid=listing_id: self.toggle_bookmark(lid))
        bookmark_btn.pack(side="right")

        return card

    def reflow_cards(self, event=None):
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
        self._loading_label = ctk.CTkLabel(self.cards_grid_frame, text="Loading...",
                                           font=self.body_paragraph_font, text_color=self.text_color)
        self._loading_label.pack()

        def _do():
            try:
                response = self.api.get(f"/boarding-houses/feed/dashboard?offset=0&limit={self._dashboard_limit}")
                if response.status_code == 200:
                    houses = response.json()
                    logger.info("Successfully loaded %d houses from the database!", len(houses))
                    self.after(0, lambda: self._populate_initial_cards(houses))
                else:
                    logger.warning("Backend error %s: %s", response.status_code, response.text)
                    self.after(0, self._show_dashboard_offline)
            except (requests.ConnectionError, requests.Timeout):
                logger.warning("Backend is offline! Falling back to dummy data.")
                self.after(0, self._show_dashboard_offline)

        threading.Thread(target=_do, daemon=True).start()

    def _populate_initial_cards(self, houses):
        if hasattr(self, '_loading_label') and self._loading_label:
            self._loading_label.destroy()
            self._loading_label = None
        if not houses:
            return
        for house_data in houses:
            card_widget = self.create_listing_card(self.cards_grid_frame, house_data)
            self.cards_list.append(card_widget)
        self.reflow_cards()

    def _show_dashboard_offline(self):
        if hasattr(self, '_loading_label') and self._loading_label:
            self._loading_label.destroy()
            self._loading_label = None
        dummy = {"name": "Server Offline", "location": "N/A", "amenities": "N/A", "desc": "Please start Uvicorn!"}
        card = self.create_listing_card(self.cards_grid_frame, dummy)
        self.cards_list.append(card)
        self.reflow_cards()

    def _load_more(self):
        self._dashboard_offset += self._dashboard_limit
        self.load_more_btn.configure(state="disabled", text="Loading...")

        def _do():
            try:
                resp = self.api.get(f"/boarding-houses/feed/dashboard?offset={self._dashboard_offset}&limit={self._dashboard_limit}", timeout=10)
                if resp.status_code == 200:
                    houses = resp.json()
                    if not houses:
                        self._dashboard_offset -= self._dashboard_limit
                        self.after(0, lambda: self._load_more_done("No more listings"))
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

    def _load_more_done(self, msg):
        self.load_more_btn.configure(state="normal", text="Load More")
        self.show_toast(msg, is_error=True)

    def _do_search(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        self.search_btn.configure(state="disabled", text="Searching...")

        def _do():
            try:
                resp = self.api.get(f"/search/?q={query}", timeout=10)
                if resp.status_code == 200:
                    results = resp.json()
                    self.after(0, lambda: self._rebuild_cards(results))
                else:
                    self.after(0, lambda: self.show_toast("Search failed", is_error=True))
            except Exception:
                self.after(0, lambda: self.show_toast("Cannot connect to server", is_error=True))
            finally:
                self.after(0, lambda: self.search_btn.configure(state="normal", text=None, image=self.search_icon))

        threading.Thread(target=_do, daemon=True).start()

    def toggle_filter(self, selected_filter):
        for name, btn in self.filter_buttons.items():
            btn.configure(fg_color=self.secondary_color, text_color=self.text_color)

        self.filter_buttons[selected_filter].configure(fg_color=self.primary_color, text_color="white")

        if selected_filter == "All":
            return

        def _do():
            if not hasattr(self, "_amenity_map"):
                try:
                    resp = self.api.get("/amenities")
                    if resp.status_code == 200:
                        self._amenity_map = {a["amenity_name"]: a["amenity_id"] for a in resp.json()}
                except Exception:
                    self._amenity_map = {}

            amenity_id = self._amenity_map.get(selected_filter)
            if not amenity_id:
                return

            try:
                resp = self.api.get(f"/search/?amenity_ids={amenity_id}")
                if resp.status_code == 200:
                    results = resp.json()
                    self.after(0, lambda: self._rebuild_cards(results))
            except Exception:
                pass

        threading.Thread(target=_do, daemon=True).start()

    def toggle_bookmark(self, listing_id):
        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            self.show_toast("Please log in to bookmark listings", is_error=True)
            return

        def _do():
            try:
                resp = self.api.post("/favorites/toggle", json={"user_id": user_id, "listing_id": listing_id})
                if resp.status_code == 200:
                    action = resp.json().get("action", "")
                    self.after(0, lambda: self.show_toast(f"Bookmark {action}!", is_error=False))
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to toggle bookmark", is_error=True))

        threading.Thread(target=_do, daemon=True).start()

    def _rebuild_cards(self, houses):
        for card in self.cards_list:
            card.destroy()
        self.cards_list = []
        for house_data in houses:
            card_widget = self.create_listing_card(self.cards_grid_frame, house_data)
            self.cards_list.append(card_widget)
        self.reflow_cards()

    def show_student_bookings(self):
        self.clear_container()
        self.geometry("900x700")

        container = ctk.CTkFrame(self.container, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        back_btn = ctk.CTkLabel(container, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(anchor="w")
        back_btn.bind("<Button-1>", lambda e: self.show_tenant_dashboard())

        ctk.CTkLabel(container, text="MY BOOKINGS", font=self.alt_title_font,
                     text_color=self.text_color).pack(pady=(20, 20))

        self._bookings_container = container
        self._loading_bookings_label = ctk.CTkLabel(container, text="Loading...",
                                                    font=self.body_paragraph_font, text_color=self.text_color)
        self._loading_bookings_label.pack(pady=40)

        user_id = getattr(self, 'current_user', {}).get('user_id')

        def _do():
            bookings = []
            try:
                resp = self.api.get(f"/bookings/user/{user_id}", timeout=5)
                if resp.status_code == 200:
                    bookings = resp.json()
            except Exception:
                pass
            self.after(0, lambda: self._populate_bookings(container, bookings))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_bookings(self, container, bookings):
        if hasattr(self, '_loading_bookings_label') and self._loading_bookings_label:
            self._loading_bookings_label.destroy()
            self._loading_bookings_label = None

        if not bookings:
            ctk.CTkLabel(container, text="You have no bookings yet.",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for b in bookings:
            card = ctk.CTkFrame(scroll, fg_color=self.secondary_color, corner_radius=8,
                                border_width=1, border_color=self.entry_border)
            card.pack(fill="x", pady=5, padx=10)

            info = f"Booking #{b.get('booking_id')} — Room #{b.get('room_id')} — {b.get('status', 'unknown')}"
            ctk.CTkLabel(card, text=info, font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=15, pady=12)

            if b.get("status") == "pending":
                cancel_btn = ctk.CTkButton(card, text="Cancel Booking",
                                           fg_color=self.error_red, hover_color="#c9302c",
                                           text_color="white", font=self.body_paragraph_font,
                                           width=120, height=32,
                                           command=lambda bid=b.get("booking_id"): self._cancel_booking(bid))
                cancel_btn.pack(side="right", padx=15, pady=8)

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
        self.show_student_bookings()


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

    def _toggle_user_menu(self):
        if hasattr(self, '_user_menu') and self._user_menu and self._user_menu.winfo_ismapped():
            self._hide_user_menu()
        else:
            self._show_user_menu()

    def _show_user_menu(self):
        self._hide_user_menu()

        menu = ctk.CTkFrame(self.form_container, fg_color=self.secondary_color,
                            corner_radius=6, border_width=1, border_color=self.entry_border,
                            width=200)
        self._user_menu = menu

        profile_x = self.profile_frame.winfo_rootx() - self.form_container.winfo_rootx()
        profile_y = self.profile_frame.winfo_rooty() - self.form_container.winfo_rooty()
        profile_h = self.profile_frame.winfo_height()
        menu_x = profile_x + self.profile_frame.winfo_width() - 200
        menu_y = profile_y + profile_h + 5

        menu.place(x=menu_x, y=menu_y)
        menu.lift()

        items = [
            ("View Profile", self.menu_profile_icon, lambda: self._menu_action(self.show_profile)),
            ("Change Password", self.menu_lock_icon, lambda: self._menu_action(self.show_change_password)),
            ("Notifications", self.notification_icon, lambda: self._menu_action(self.show_notifications_page)),
            ("My Bookings", self.menu_bookings_icon, lambda: self._menu_action(self.show_student_bookings)),
            None,
            ("Logout", self.menu_logout_icon, lambda: self._menu_action(self._handle_logout)),
        ]

        for item in items:
            if item is None:
                sep = ctk.CTkFrame(menu, height=1, fg_color=self.entry_border)
                sep.pack(fill="x", padx=10, pady=5)
                continue
            text, icon, cmd = item
            btn = ctk.CTkButton(menu, text=text, image=icon,
                                font=self.body_paragraph_font,
                                fg_color="transparent", text_color=self.text_color,
                                hover_color=self.hover_color, anchor="w",
                                height=36, command=cmd)
            btn.pack(fill="x", padx=5, pady=2)

        self.bind_all("<Button-1>", self._dismiss_user_menu, add="+")

    def _hide_user_menu(self):
        if hasattr(self, '_user_menu') and self._user_menu:
            try:
                self._user_menu.destroy()
            except Exception:
                pass
            self._user_menu = None
        try:
            self.unbind_all("<Button-1>")
        except Exception:
            pass

    def _dismiss_user_menu(self, event):
        if not hasattr(self, '_user_menu') or not self._user_menu:
            return
        x = event.x_root
        y = event.y_root
        widget = self.winfo_containing(x, y)
        if widget and (self._user_menu == widget or self._user_menu in self._get_all_children(widget)):
            return
        self._hide_user_menu()

    def _get_all_children(self, widget):
        children = []
        try:
            for child in widget.winfo_children():
                children.append(child)
                children.extend(self._get_all_children(child))
        except Exception:
            pass
        return children

    def _menu_action(self, callback):
        self._hide_user_menu()
        callback()

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
