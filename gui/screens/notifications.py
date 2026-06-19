import threading
import customtkinter as ctk


class NotificationsMixin:
    def show_notifications_page(self):
        self.clear_container()
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{int(w * 0.85)}x{int(h * 0.85)}")
        self.resizable(True, True)

        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True)

        # Top bar
        top_bar = ctk.CTkFrame(self.form_container, fg_color="transparent", height=60,
                               border_width=1, border_color=self.entry_border)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        back_btn = ctk.CTkLabel(top_bar, text="", image=self.bk_btn_icon, cursor="hand2")
        back_btn.pack(side="left", padx=10)
        back_btn.bind("<Button-1>", lambda e: self._back_to_dashboard())
        back_btn.bind("<Enter>", lambda e: back_btn.configure(image=self.bk_btn_hvr_icon))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(image=self.bk_btn_icon))

        ctk.CTkLabel(top_bar, text="Notifications", font=self.alt_title_font,
                     text_color=self.text_color).pack(side="left", padx=10)

        self.mark_all_btn = ctk.CTkButton(top_bar, text="Mark All Read",
                                          font=self.body_light_font,
                                          fg_color=self.primary_color,
                                          hover_color=self.hover_color,
                                          text_color="white",
                                          height=32, command=self._mark_all_read)
        self.mark_all_btn.pack(side="right", padx=15)

        # Scrollable content
        self._notif_scroll = ctk.CTkScrollableFrame(self.form_container, fg_color="transparent")
        self._notif_scroll.pack(fill="both", expand=True, padx=30, pady=20)

        self._notif_loading = ctk.CTkProgressBar(self._notif_scroll, mode="indeterminate",
                                                  fg_color=self.entry_border,
                                                  progress_color=self.primary_color)
        self._notif_loading.pack(fill="x", padx=40, pady=40)
        self._notif_loading.start()

        self._notif_data = []
        self._notif_widgets = {}

        self._fetch_notifications()

    def _fetch_notifications(self):
        user_id = getattr(self, 'current_user', {}).get('user_id')
        if not user_id:
            self._notif_loading.stop()
            self._notif_loading.pack_forget()
            return

        def _do():
            try:
                resp = self.api.get(f"/notifications/user/{user_id}", timeout=5)
                data = resp.json() if resp.status_code == 200 else []
            except Exception:
                data = None
            self.after(0, lambda: self._populate_notifications(data))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_notifications(self, data):
        self._notif_loading.stop()
        self._notif_loading.pack_forget()

        if data is None:
            ctk.CTkLabel(self._notif_scroll, text="Cannot connect to server.",
                         font=self.body_paragraph_font, text_color=self.error_red).pack(pady=40)
            return

        if not data:
            ctk.CTkLabel(self._notif_scroll, text="No notifications yet.",
                         font=self.body_paragraph_font, text_color=self.text_color).pack(pady=40)
            return

        self._notif_data = data
        for notif in data:
            notif_id = notif.get("notif_id")
            is_read = notif.get("is_read", False)
            content = notif.get("content", "")
            notif_type = notif.get("type", "system")
            created_at = str(notif.get("created_at", ""))[:16] if notif.get("created_at") else ""

            card = ctk.CTkFrame(self._notif_scroll, fg_color=self.secondary_color,
                                corner_radius=6, border_width=1, border_color=self.entry_border)
            card.pack(fill="x", pady=4)
            card.pack_propagate(False)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=12)

            # Unread dot
            dot = ctk.CTkLabel(inner, text="", width=8, height=8,
                               fg_color=self.primary_color if not is_read else "transparent",
                               corner_radius=4)
            dot.pack(side="left", padx=(0, 10))

            type_lbl = ctk.CTkLabel(inner, text=notif_type.capitalize(),
                                    font=self.body_description_font,
                                    text_color=self.primary_color, width=60)
            type_lbl.pack(side="left")

            ctk.CTkLabel(inner, text=content, font=self.body_paragraph_font,
                         text_color=self.text_color).pack(side="left", padx=(10, 0), fill="x", expand=True)

            ctk.CTkLabel(inner, text=created_at, font=self.body_description_font,
                         text_color=self.text_color).pack(side="right", padx=(10, 0))

            if not is_read:
                card.bind("<Button-1>", lambda e, nid=notif_id: self._mark_one_read(nid))
                card.configure(cursor="hand2")

            self._notif_widgets[notif_id] = (card, dot)

    def _mark_one_read(self, notif_id):
        def _do():
            try:
                self.api.patch(f"/notifications/{notif_id}/read", timeout=5)
            except Exception:
                self.after(0, lambda: self.show_toast("Failed to mark notification as read. Check your connection.", is_error=True))
            self.after(0, lambda: self._update_notif_read_ui(notif_id))

        threading.Thread(target=_do, daemon=True).start()

    def _update_notif_read_ui(self, notif_id):
        widgets = self._notif_widgets.get(notif_id)
        if not widgets:
            return
        card, dot = widgets
        dot.configure(fg_color="transparent")
        card.configure(cursor="")
        card.unbind("<Button-1>")

    def _mark_all_read(self):
        self.mark_all_btn.configure(state="disabled", text="Marking...")

        def _do():
            for notif_id in self._notif_widgets:
                try:
                    self.api.patch(f"/notifications/{notif_id}/read", timeout=5)
                except Exception:
                    self.after(0, lambda: self.show_toast("Failed to mark notifications as read. Check your connection.", is_error=True))
            self.after(0, self._update_all_read_ui)

        threading.Thread(target=_do, daemon=True).start()

    def _update_all_read_ui(self):
        self.mark_all_btn.configure(state="normal", text="Mark All Read")
        for notif_id in self._notif_widgets:
            card, dot = self._notif_widgets[notif_id]
            dot.configure(fg_color="transparent")
            card.configure(cursor="")
            card.unbind("<Button-1>")

    def _back_to_dashboard(self):
        role = getattr(self, 'current_user', {}).get('role')
        if role == 'owner':
            self.show_owner_dashboard()
        else:
            self.show_tenant_dashboard()
