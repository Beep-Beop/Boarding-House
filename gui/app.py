import customtkinter as ctk
from tkinterdnd2.TkinterDnD import require as require_dnd
from PIL import Image
import os
import base64
import json
import sys
from datetime import datetime, timezone
from dataclasses import dataclass

if sys.platform.startswith("linux"):
    from customtkinter.windows.widgets.ctk_scrollable_frame import CTkScrollableFrame

    def _linux_scroll_handler(self, event):
        if self.check_if_master_is_canvas(event.widget):
            if self._parent_canvas.yview() != (0.0, 1.0):
                if event.num == 4:
                    self._parent_canvas.yview("scroll", -1, "units")
                elif event.num == 5:
                    self._parent_canvas.yview("scroll", 1, "units")

    CTkScrollableFrame._linux_scroll_handler = _linux_scroll_handler
    _orig_init = CTkScrollableFrame.__init__
    def _patched_init(self, *args, **kwargs):
        _orig_init(self, *args, **kwargs)
        self.bind_all("<Button-4>", lambda e: self._linux_scroll_handler(e), add="+")
        self.bind_all("<Button-5>", lambda e: self._linux_scroll_handler(e), add="+")
    CTkScrollableFrame.__init__ = _patched_init

from gui.api_client import APIClient
from src.logger import logger
from gui.screens.login import LoginMixin
from gui.screens.account_type import AccountTypeMixin
from gui.screens.register import RegisterMixin
from gui.screens.email_verify import EmailVerifyMixin
from gui.screens.dashboard import DashboardMixin
from gui.screens.owner_dashboard import OwnerDashboardMixin
from gui.screens.register_skeleton import RegisterSkeletonMixin
from gui.screens.forgot_password import ForgotPasswordMixin
from gui.screens.account_settings import AccountSettingsMixin
from gui.screens.admin_dashboard import AdminDashboardMixin
from gui.screens.notifications import NotificationsMixin


@dataclass
class Theme:
    primary_color: tuple = ("#AC7F5E", "#8B6B4E")
    secondary_color: tuple = ("#F6F1E8", "#2D2D2D")
    entry_border: tuple = ("#E0E0E0", "#555555")
    hover_color: tuple = ("#D6B588", "#A89060")
    hover_color_text: tuple = ("#E2E2E2", "#444444")
    text_color: tuple = ("#3E362A", "#E0DCD3")
    error_red: tuple = ("#D9534F", "#D9534F")
    fg_color: tuple = ("#F8F8F8", "#333333")


class BoardingHouseApp(ctk.CTk, LoginMixin, AccountTypeMixin, RegisterMixin,
                       RegisterSkeletonMixin,
                       EmailVerifyMixin, DashboardMixin, OwnerDashboardMixin,
                       ForgotPasswordMixin, AccountSettingsMixin,
                       NotificationsMixin, AdminDashboardMixin):
    def __init__(self):
        super().__init__()
        require_dnd(self)

        ctk.set_default_color_theme("green")
        self.title("Boarding House Finder")
        self.geometry("630x700")
        self.resizable(False, False)

        # --- User State (before api client — setter reads these) ---
        self.current_user = None
        self.access_token = None
        self._screen_active = True
        self._menu_showing = False
        self.bind("<Button-1>", self._on_global_menu_click)

        # --- API Client ---
        self.api = APIClient()

        # --- Toast / Screen state ---
        self.current_toast = None
        self.toast_timer = None
        self.after_ids = []

        # --- Font Setup ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        font_files = [
            os.path.join(parent_dir, "assets", "Novecentosanswide-Light.otf"),
            os.path.join(parent_dir, "assets", "Novecentosanswide-Normal.otf"),
            os.path.join(parent_dir, "assets", "Poppins-Regular.ttf"),
            os.path.join(parent_dir, "assets", "Poppins-Light.ttf")
        ]

        for file_path in font_files:
            if os.path.exists(file_path):
                try:
                    ctk.FontManager.load_font(file_path)
                except Exception as e:
                    logger.warning("Could not load %s. Error: %s", file_path, e)

        self.design = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "design.png")), size=(180, 160))
        self.tenant_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "icons.png")), size=(25, 25))
        self.landlord_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "Frame.png")), size=(25, 25))
        self.hamburg_menu_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "menu.png")), size=(25, 15))
        self.pfp_placeholder = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "pfp_placeholder.png")), size=(40, 40))
        self.pfp_placeholder_sm = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "pfp_placeholder.png")), size=(32, 32))
        self.search_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "search.png")), size=(30, 30))
        self.bookmark_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "bookmark.png")), size=(25, 25))
        self.upload_image_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "upload_image.png")), size=(60, 60))

        self.notification_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "notification.png")), size=(22, 22))
        self.menu_profile_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "pfp_placeholder.png")), size=(18, 18))
        self.menu_lock_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "close_eye_pass_icon.png")), size=(18, 18))
        self.menu_bookings_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "bookmark.png")), size=(18, 18))
        self.menu_logout_icon = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "bk_btn.png")), size=(18, 18))

        self.logo = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "logo.png")), size=(140, 32))
        raw_google = Image.open(os.path.join(parent_dir, "assets", "google.png"))
        orig_w, orig_h = raw_google.size
        padded_google = Image.new("RGBA", (orig_w + 40, orig_h + 40), (255, 255, 255, 0))
        padded_google.paste(raw_google, (20, 20))
        pad_w, pad_h = padded_google.size
        target_width = 110
        target_height = int((pad_h / pad_w) * target_width)
        self.google_icon = ctk.CTkImage(padded_google, size=(target_width, target_height))

        self.bk_btn = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "bk_btn.png")), size=(80, 60))
        raw_bk_btn = Image.open(os.path.join(parent_dir, "assets", "bk_btn.png"))
        bk_orig_w, bk_orig_h = raw_bk_btn.size
        padded_bk_btn = Image.new("RGBA", (bk_orig_w + 40, bk_orig_h + 40), (255, 255, 255, 0))
        padded_bk_btn.paste(raw_bk_btn, (20, 20))
        bk_btn_pad_w, bk_btn_pad_h = padded_bk_btn.size
        target_width_btn = 70
        target_height_btn = int((bk_btn_pad_h / bk_btn_pad_w) * target_width_btn)
        self.bk_btn_icon = ctk.CTkImage(padded_bk_btn, size=(target_width_btn, target_height_btn))

        self.bk_btn_hvr = ctk.CTkImage(Image.open(os.path.join(parent_dir, "assets", "bk_btn_hvr.png")), size=(80, 60))
        raw_bk_btn_hvr = Image.open(os.path.join(parent_dir, "assets", "bk_btn_hvr.png"))
        bk_hvr_orig_w, bk_hvr_orig_h = raw_bk_btn_hvr.size
        padded_bk_btn_hvr = Image.new("RGBA", (bk_hvr_orig_w + 40, bk_hvr_orig_h + 40), (255, 255, 255, 0))
        padded_bk_btn_hvr.paste(raw_bk_btn_hvr, (20, 20))
        bk_btn_hvr_pad_w, bk_btn_hvr_pad_h = padded_bk_btn_hvr.size
        target_width_hvr = 70
        target_height_hvr = int((bk_btn_hvr_pad_h / bk_btn_hvr_pad_w) * target_width_hvr)
        self.bk_btn_hvr_icon = ctk.CTkImage(padded_bk_btn_hvr, size=(target_width_hvr, target_height_hvr))

        # Pre-generate eye icon animation frames (no extra PNGs needed)
        raw_closed = Image.open(os.path.join(parent_dir, "assets", "close_eye_pass_icon.png")).convert("RGBA")
        raw_open = Image.open(os.path.join(parent_dir, "assets", "open_eye_pass_icon.png")).convert("RGBA")
        self._eye_frames_open = []
        self._eye_frames_closed = []
        size = (22, 22)
        for i in range(1, 8):
            alpha = i / 7
            blended = Image.blend(raw_closed, raw_open, alpha)
            self._eye_frames_open.append(ctk.CTkImage(blended, size=size))
        for i in range(6, -1, -1):
            alpha = i / 7
            blended = Image.blend(raw_closed, raw_open, alpha)
            self._eye_frames_closed.append(ctk.CTkImage(blended, size=size))

        self.closed_eye_icon = ctk.CTkImage(raw_closed, size=(22, 22))
        self.open_eye_icon = ctk.CTkImage(raw_open, size=(22, 22))

        self.title_font = ctk.CTkFont(family="Novecento sans wide Normal", size=32, weight="bold")
        self.alt_title_font = ctk.CTkFont(family="Novecento sans wide Normal", size=24, weight="bold")
        self.body_bold_font = ctk.CTkFont(family="Novecento sans wide Normal", size=20, weight="bold")


        self.body_paragraph_big_font = ctk.CTkFont(family="Poppins", size=24, weight="normal")
        self.body_bold_paragraph_font = ctk.CTkFont(family="Poppins", size=24, weight="bold")
        self.body_paragraph_font = ctk.CTkFont(family="Poppins", size=16, weight="normal")
        self.body_big_font = ctk.CTkFont(family="Poppins", size=20, weight="normal")
        self.body_light_font = ctk.CTkFont(family="Poppins Light", size=16, weight="normal")
        self.body_description_font = ctk.CTkFont(family="Poppins", size=12, weight="normal")

        self.inline_error_font = ctk.CTkFont(family="Poppins", size=12, weight="normal")

        theme = Theme()
        self.primary_color = theme.primary_color
        self.secondary_color = theme.secondary_color
        self.entry_border = theme.entry_border
        self.hover_color = theme.hover_color
        self.hover_color_text = theme.hover_color_text
        self.text_color = theme.text_color
        self.error_red = theme.error_red
        self.fg_color = theme.fg_color

        self.configure(fg_color="#FFFFFF")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)

        # --- Try loading saved session ---
        saved = self._load_session()
        if saved and saved.get("access_token"):
            token = saved["access_token"]
            if not self._is_token_valid(token):
                print("[DEBUG] Saved token expired — clearing session")
                self._clear_session()
                self.access_token = None
                self.api.access_token = None
                saved = None
        if saved and saved.get("access_token"):
            print(f"[DEBUG] Session restored — role={saved.get('role')}, routing to dashboard")
            self.access_token = saved["access_token"]
            self.api.access_token = self.access_token
            self.current_user = saved
            role = saved.get("role")
            if role == "admin":
                self.show_admin_dashboard()
            elif role == "owner":
                self.show_owner_dashboard()
            else:
                self.show_tenant_dashboard()
            return
        else:
            print("[DEBUG] No saved session — showing login page")

        #Debugg
        self.show_login_page()
        #self.show_owner_dashboard()
        #self.show_tenant_dashboard()

    def _is_token_valid(self, token):
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return False
            payload_b64 = parts[1]
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            exp = payload.get("exp", 0)
            return exp > datetime.now(timezone.utc).timestamp()
        except Exception:
            return False

    def clear_container(self):
        self._hide_user_menu()
        if not getattr(self, "_building_under_skeleton", False):
            if hasattr(self, "_stop_skeleton"):
                self._stop_skeleton()
        self._screen_active = False
        for after_id in self.after_ids:
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self.after_ids = []

        if self.toast_timer is not None:
            try:
                self.after_cancel(self.toast_timer)
            except Exception:
                pass
            self.toast_timer = None

        if self.current_toast is not None:
            try:
                self.current_toast.destroy()
            except Exception:
                pass
            self.current_toast = None

        for widget in self.winfo_children():
            if "!ctkscrollabledropdown" in str(widget).lower():
                try:
                    widget.destroy()
                except Exception:
                    pass

        if hasattr(self, 'container'):
            for widget in self.container.winfo_children():
                try:
                    widget.destroy()
                except Exception:
                    pass

        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def show_toast(self, message, is_error=True):

        if self.toast_timer is not None:
            self.after_cancel(self.toast_timer)
            self.toast_timer = None

        if self.current_toast is not None:
            try:
                self.current_toast.destroy()
            except:
                pass

        bg_color = self.error_red if is_error else self.primary_color

        self.current_toast = ctk.CTkFrame(self,
                                          fg_color=bg_color,
                                          corner_radius=6,
                                          width=350,
                                          height=40)
        self.current_toast.place(relx=0.5, rely=-0.1, anchor="center")
        self.current_toast.pack_propagate(False)

        msg_label = ctk.CTkLabel(self.current_toast,
                                 text=message,
                                 text_color="#FFFFFF",
                                 font=self.body_paragraph_font)
        msg_label.place(relx=0.5, rely=0.5, anchor="center")

        def animate_in(current_rely=1.05):
            if self.current_toast is None or not self.current_toast.winfo_exists(): return

            if current_rely > 0.9:
                self.current_toast.place(relx=0.5, rely=current_rely, anchor="center")
                aid = self.after(10, lambda: animate_in(current_rely - 0.01))
                self.after_ids.append(aid)
            else:
                self.toast_timer = self.after(2500, animate_out)

        def animate_out(current_rely=0.9):
            if self.current_toast is None or not self.current_toast.winfo_exists(): return

            if current_rely < 1.05:
                self.current_toast.place(relx=0.5, rely=current_rely, anchor="center")
                aid = self.after(10, lambda: animate_out(current_rely + 0.01))
                self.after_ids.append(aid)
            else:
                self.current_toast.destroy()
                self.current_toast = None

        animate_in()

    def _animate_eye(self, label, frames, idx=0):
        if idx == 0:
            timer = getattr(label, "_anim_timer", None)
            if timer:
                try:
                    self.after_cancel(timer)
                except Exception:
                    pass
        if idx >= len(frames):
            label._anim_timer = None
            return
        try:
            label.configure(image=frames[idx])
            label._anim_timer = self.after(40, lambda: self._animate_eye(label, frames, idx + 1))
        except Exception:
            label._anim_timer = None

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, client):
        self._api = client
        if self.access_token:
            client.access_token = self.access_token

    def api_request(self, method, endpoint, **kwargs):
        return getattr(self._api, method.lower())(endpoint, **kwargs)

    def _handle_logout(self):
        self.api.logout()
        self.access_token = None
        self.current_user = None
        self._clear_session()
        self.show_login_page()

    def show_location(self):
        self.clear_container()

        self.geometry("1200x700")

    # Main Container
        self.form_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.form_container.pack(pady=(0, 0), fill="both", expand=True)

        bk_btn_frame = ctk.CTkFrame(self.form_container,
                                  fg_color="transparent"
                                  )
        bk_btn_frame.pack(fill="x", pady=(15, 0))

        self.back_btn = ctk.CTkLabel(bk_btn_frame,
                                     text="",
                                     image=self.bk_btn_icon,
                                     cursor="hand2"
                                     )
        self.back_btn.pack(side="left", padx=(15, 0))
        self.back_btn.bind("<Button-1>", lambda event: self.show_login_page())
        self.back_btn.bind("<Enter>", lambda event: self.back_btn.configure(image=self.bk_btn_hvr_icon))

    def clear_placeholder(self, event, combobox, placeholder_text):
        if combobox.get() == placeholder_text:
            combobox.set("")

    def _make_dropdown(self, attach, **kwargs):
        from CTkScrollableDropdown import CTkScrollableDropdown
        defaults = dict(
            fg_color=self.fg_color,
            button_color=self.secondary_color,
            text_color=self.text_color,
            hover_color=self.hover_color,
            button_height=36,
            font=self.body_light_font,
            frame_corner_radius=10,
            frame_border_width=1,
            frame_border_color=self.entry_border,
            scrollbar_button_color=self.primary_color,
            scrollbar_button_hover_color=self.hover_color,
        )
        defaults.update(kwargs)
        return CTkScrollableDropdown(attach, **defaults)

    def restore_placeholder(self, event, combobox, placeholder_text):
        if not combobox.get().strip():
            combobox.set(placeholder_text)

    # ── Shared User Menu ────────────────────────────────────────────

    def _show_user_menu(self, parent, anchor, form_container, items):
        """Single implementation used by all three dashboards."""
        self._hide_user_menu()

        menu = ctk.CTkFrame(parent, fg_color=self.secondary_color,
                            corner_radius=8, border_width=2,
                            border_color=self.entry_border, width=240)
        self._user_menu = menu

        ax = anchor.winfo_rootx() - form_container.winfo_rootx()
        ay = anchor.winfo_rooty() - form_container.winfo_rooty()
        ah = anchor.winfo_height()
        menu.place(x=ax + anchor.winfo_width() - 240, y=ay + ah + 6)
        menu.lift()

        user = getattr(self, 'current_user', {})
        email = user.get('email', '')
        role = user.get('role', 'tenant').capitalize()

        header = ctk.CTkFrame(menu, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(14, 8))

        if email:
            ctk.CTkLabel(header, text=email, font=ctk.CTkFont(size=12),
                         text_color=self.text_color).pack(anchor="w")
        ctk.CTkLabel(header, text=role, font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="white", fg_color=self.primary_color,
                     corner_radius=4, padx=6).pack(anchor="w", pady=(3, 0))

        ctk.CTkFrame(menu, height=1, fg_color=self.entry_border).pack(fill="x", padx=10, pady=6)

        for item in items:
            if item is None:
                ctk.CTkFrame(menu, height=1, fg_color=self.entry_border).pack(fill="x", padx=10, pady=2)
                continue
            text, icon, cmd = item
            btn = ctk.CTkButton(menu, text=text, image=icon,
                                font=self.body_paragraph_font,
                                fg_color="transparent", text_color=self.text_color,
                                hover_color=self.hover_color, anchor="w",
                                height=36)
            btn.pack(fill="x", padx=5, pady=2)
            btn.configure(command=lambda cb=cmd: self._execute_menu_action(cb))
            btn.bind("<Button-3>", lambda e, t=text, cb=cmd: self._debug_menu_item(t, cb))

        menu.focus_set()
        menu.bind("<Escape>", lambda e: self._hide_user_menu())
        self._menu_anchor = anchor
        self._menu_showing = True

    def _debug_menu_item(self, text, callback):
        print(f"\n[DEBUG] ===== Right-click on menu item: '{text}' =====")
        import inspect
        cb_name = getattr(callback, '__name__', str(callback))
        cb_module = getattr(callback, '__self__', '')
        print(f"[DEBUG]   callback: {cb_name}, self: {cb_module}")
        print(f"[DEBUG]   inspect: {inspect.getsource(callback)[:200] if callable(callback) else 'N/A'}")
        print(f"[DEBUG]   current container children: {len(self.container.winfo_children())}")
        print(f"[DEBUG] ======================================\n")
        self.show_toast(f"Right-click: {text}", is_error=False)

    def _execute_menu_action(self, callback):
        """Hide menu then invoke the callback."""
        cb_name = getattr(callback, '__name__', str(callback))
        print(f"\n[DEBUG] _execute_menu_action: callback={cb_name}")
        print(f"[DEBUG]   container children before hide: {len(self.container.winfo_children())}")
        self._hide_user_menu()
        print(f"[DEBUG]   container children after hide: {len(self.container.winfo_children())}")
        try:
            callback()
            print(f"[DEBUG]   callback completed OK")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[DEBUG]   callback FAILED: {e}")
            self.after(0, lambda: self.show_toast(f"Navigation error: {e}", is_error=True))

    def _hide_user_menu(self):
        """Destroy menu and overlay. Shared by all dashboards."""
        self._menu_showing = False
        if hasattr(self, '_user_menu') and self._user_menu:
            try:
                self._user_menu.destroy()
            except Exception:
                pass
            self._user_menu = None
        self._reset_chevrons()

    def _on_global_menu_click(self, event):
        if not self._menu_showing:
            return
        menu = getattr(self, '_user_menu', None)
        anchor = getattr(self, '_menu_anchor', None)
        w = event.widget
        while w:
            if w is menu or (anchor and w is anchor):
                return
            w = w.master if w.master else None
        self._hide_user_menu()

    def _reset_chevrons(self):
        """Set all known chevron labels back to ▾."""
        for attr in ('profile_chevron', 'owner_profile_chevron'):
            if hasattr(self, attr):
                try:
                    getattr(self, attr).configure(text="▾")
                except Exception:
                    pass
