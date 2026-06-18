import customtkinter as ctk
import threading
from PIL import Image
import io
import re
from tkinter import filedialog, messagebox


class AccountSettingsMixin:

    def show_account_settings(self):
        """Build the unified Account Settings overlay with CTkTabview."""
        # Determine which container to use (same pattern as existing overlays)
        container = getattr(self, 'form_container', None) or \
                    getattr(self, '_admin_form_container', None) or \
                    self.container

        # Destroy any existing overlay
        self._close_account_overlay()

        # Outer overlay
        overlay = ctk.CTkFrame(container, fg_color=self.fg_color)
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.lift()
        self._account_overlay = overlay

        # Card
        card = ctk.CTkFrame(overlay, fg_color=self.secondary_color,
                            corner_radius=12, border_width=1,
                            border_color=self.entry_border, width=580)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Close button
        close_btn = ctk.CTkButton(card, text="✕", width=32, height=32,
                                  fg_color="transparent",
                                  text_color=self.text_color,
                                  hover_color=self.hover_color,
                                  command=self._close_account_overlay)
        close_btn.place(x=12, y=12)

        # Title
        title = ctk.CTkLabel(card, text="ACCOUNT SETTINGS",
                             font=self.alt_title_font,
                             text_color=self.text_color)
        title.pack(pady=(20, 10))

        # Determine tabs based on role
        role = getattr(self.current_user, 'role', None) or \
               (self.current_user or {}).get('role', 'student')

        if role == "admin":
            tab_names = ["Profile", "Security"]
        elif role == "owner":
            tab_names = ["Profile", "Security", "Documents"]
        else:
            tab_names = ["Profile", "Security", "Verification"]

        # Tabview
        tabview = ctk.CTkTabview(card, width=540, height=460,
                                 fg_color="transparent",
                                 segmented_button_fg_color=self.fg_color,
                                 segmented_button_selected_color=self.primary_color,
                                 segmented_button_unselected_color=self.hover_color_text,
                                 text_color=self.text_color)
        tabview.pack(padx=20, pady=(0, 20))

        # Create tabs
        self._account_tabs = {}
        for name in tab_names:
            tab = tabview.add(name)
            tab_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
            tab_scroll.pack(fill="both", expand=True)
            self._account_tabs[name] = tab_scroll

        # Build tab contents
        self._build_profile_tab(self._account_tabs["Profile"])
        self._build_security_tab(self._account_tabs["Security"])
        if "Verification" in self._account_tabs:
            self._build_verification_tab(self._account_tabs["Verification"])
        if "Documents" in self._account_tabs:
            self._build_documents_tab(self._account_tabs["Documents"])

    def _close_account_overlay(self):
        """Destroy the account settings overlay."""
        if hasattr(self, '_account_overlay') and self._account_overlay:
            try:
                self._account_overlay.destroy()
            except Exception:
                pass
            self._account_overlay = None
