import customtkinter as ctk


class AdminDashboardMixin:
    def show_admin_dashboard(self):
        print("[DEBUG] Showing: Admin Dashboard")
        self.clear_container()
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{int(w * 0.85)}x{int(h * 0.85)}")
        self.resizable(True, True)

        container = ctk.CTkFrame(self.container, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="ADMIN DASHBOARD", font=self.alt_title_font,
                     text_color=self.text_color).pack(pady=(0, 20))

        self.admin_tabview = ctk.CTkTabview(container, fg_color="transparent")
        self.admin_tabview.pack(fill="both", expand=True)

        self.users_tab = self.admin_tabview.add("Users")
        self.listings_tab = self.admin_tabview.add("Listings")
        self.reports_tab = self.admin_tabview.add("Reports")
        self.logs_tab = self.admin_tabview.add("Admin Logs")

        self._build_admin_users(self.users_tab)
        self._build_admin_listings(self.listings_tab)
        self._build_admin_reports(self.reports_tab)
        self._build_admin_logs(self.logs_tab)

    def _build_admin_users(self, parent):
        ctk.CTkLabel(parent, text="User Management",
                     font=self.body_bold_font, text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        users = []
        try:
            resp = self.api.get("/users/", timeout=5)
            if resp.status_code == 200:
                users = resp.json()
        except Exception:
            pass

        if not users:
            ctk.CTkLabel(parent, text="No users found or endpoint unavailable.",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(pady=20)
            return

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        headers = ["ID", "Name", "Email", "Role", "Status", "Actions"]
        header_frame = ctk.CTkFrame(scroll, fg_color=self.secondary_color, corner_radius=6)
        header_frame.pack(fill="x", pady=(0, 5))
        for j, h in enumerate(headers):
            ctk.CTkLabel(header_frame, text=h, font=self.body_paragraph_font,
                         text_color=self.text_color).grid(row=0, column=j, padx=15, pady=8, sticky="w")
            header_frame.grid_columnconfigure(j, weight=1)

        for i, user in enumerate(users):
            row_color = self.fg_color if i % 2 == 0 else self.secondary_color
            row = ctk.CTkFrame(scroll, fg_color=row_color, corner_radius=4)
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=str(user.get("user_id", "")), font=self.body_light_font,
                         text_color=self.text_color).grid(row=0, column=0, padx=15, pady=6, sticky="w")
            ctk.CTkLabel(row, text=user.get("name", ""), font=self.body_light_font,
                         text_color=self.text_color).grid(row=0, column=1, padx=15, pady=6, sticky="w")
            ctk.CTkLabel(row, text=user.get("email", ""), font=self.body_light_font,
                         text_color=self.text_color).grid(row=0, column=2, padx=15, pady=6, sticky="w")
            ctk.CTkLabel(row, text=user.get("role", ""), font=self.body_light_font,
                         text_color=self.text_color).grid(row=0, column=3, padx=15, pady=6, sticky="w")
            ctk.CTkLabel(row, text=user.get("status", ""), font=self.body_light_font,
                         text_color=self.text_color).grid(row=0, column=4, padx=15, pady=6, sticky="w")

            uid = user.get("user_id")
            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.grid(row=0, column=5, padx=15, pady=6, sticky="w")
            if user.get("status") != "banned":
                ctk.CTkButton(action_frame, text="Ban", font=self.body_light_font,
                              fg_color=self.error_red, text_color="white",
                              width=50, height=25,
                              command=lambda uid=uid: self._admin_ban_user(uid)).pack(side="left", padx=2)

    def _build_admin_listings(self, parent):
        ctk.CTkLabel(parent, text="Listing Approval Queue",
                     font=self.body_bold_font, text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        listings = []
        try:
            resp = self.api.get("/boarding-houses/feed/dashboard?limit=100", timeout=5)
            if resp.status_code == 200:
                listings = resp.json()
        except Exception:
            pass

        if not listings:
            ctk.CTkLabel(parent, text="No listings found.",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(pady=20)
            return

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for listing in listings:
            card = ctk.CTkFrame(scroll, fg_color=self.secondary_color, corner_radius=6)
            card.pack(fill="x", pady=3)

            ctk.CTkLabel(card, text=listing.get("name", "Unknown"), font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=15, pady=10)

    def _build_admin_reports(self, parent):
        ctk.CTkLabel(parent, text="Report Queue",
                     font=self.body_bold_font, text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        reports = []
        try:
            resp = self.api.get("/reports/", timeout=5)
            if resp.status_code == 200:
                reports = resp.json()
        except Exception:
            pass

        if not reports:
            ctk.CTkLabel(parent, text="No pending reports.",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(pady=20)
            return

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for report in reports:
            card = ctk.CTkFrame(scroll, fg_color=self.secondary_color, corner_radius=6)
            card.pack(fill="x", pady=3)

            info = f"Report #{report.get('report_id')} — {report.get('target_type')} #{report.get('target_id')} — {report.get('status', 'pending')}"
            ctk.CTkLabel(card, text=info, font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=15, pady=10)

    def _build_admin_logs(self, parent):
        ctk.CTkLabel(parent, text="Admin Logs",
                     font=self.body_bold_font, text_color=self.text_color).pack(anchor="w", pady=(0, 10))

        logs = []
        try:
            resp = self.api.get("/admin-logs/", timeout=5)
            if resp.status_code == 200:
                logs = resp.json()
        except Exception:
            pass

        if not logs:
            ctk.CTkLabel(parent, text="No admin logs found.",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(pady=20)
            return

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for log in logs:
            card = ctk.CTkFrame(scroll, fg_color=self.secondary_color, corner_radius=6)
            card.pack(fill="x", pady=2)

            info = f"{log.get('performed_at', '?')} — {log.get('action', '?')} — {log.get('target_type')} #{log.get('target_id')}"
            ctk.CTkLabel(card, text=info, font=self.body_light_font,
                         text_color=self.text_color).pack(side="left", padx=15, pady=8)

    def _admin_ban_user(self, user_id):
        try:
            resp = self.api.patch(f"/users/{user_id}/status?new_status=banned", timeout=10)
            if resp.status_code == 200:
                self.show_toast(f"User {user_id} banned", is_error=False)
                self._build_admin_users(self.users_tab)
            else:
                self.show_toast("Failed to ban user", is_error=True)
        except Exception:
            self.show_toast("Cannot connect to server", is_error=True)
