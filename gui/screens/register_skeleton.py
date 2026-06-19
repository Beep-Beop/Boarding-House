import time
import threading

import customtkinter as ctk


_MIN_SKELETON_MS = 2000


class RegisterSkeletonMixin:
    def show_register_skeleton(self):
        print("[DEBUG] Showing: Register Skeleton")
        self._stop_skeleton()
        self.clear_container()
        self.geometry("630x700")
        self.resizable(False, False)

        self._sk_blocks = []
        self._fade_step = 0
        self._fade_dir = 1
        self._pulse_timer = None
        self._skeleton_start = time.monotonic()
        self._form_ready = False
        self._reveal_timer = None

        # Overlay on main window (not container) so clear_container() won't destroy it
        self.overlay = ctk.CTkFrame(self, fg_color="#F0F0F0", corner_radius=0)
        self.overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self.overlay.lift()
        self.overlay.bind("<Button>", lambda e: None)

        self._build_skeleton_ui()
        self._start_pulse_animation()

        # Prefetch provinces while skeleton is visible
        self._prefetch_provinces()

        # Build form underneath while skeleton animation plays; reveal after min display time
        self.after_idle(self._prepare_register_form)

    def _prefetch_provinces(self):
        def fetch():
            try:
                response = self.api.get("/locations/provinces")
                if response.status_code == 200:
                    self._cached_provinces = response.json().get("options", [])
            except Exception:
                self._cached_provinces = None
        threading.Thread(target=fetch, daemon=True).start()

    def _stop_skeleton(self):
        self._stop_pulse_animation()
        if getattr(self, "_reveal_timer", None):
            try:
                self.after_cancel(self._reveal_timer)
            except Exception:
                pass
            self._reveal_timer = None
        # Don't destroy overlay if form is building underneath it
        if getattr(self, "_building_under_skeleton", False):
            return
        if hasattr(self, "overlay") and self.overlay:
            try:
                self.overlay.destroy()
            except Exception:
                pass
            self.overlay = None

    def _sk_block(self, parent, **kwargs):
        f = ctk.CTkFrame(parent, **kwargs)
        self._sk_blocks.append(f)
        return f

    def _build_skeleton_ui(self):
        sk = "#E0E0E0"
        L = 15
        W = 430

        # ---- Navbar (bk_btn_frame) ----
        nav = ctk.CTkFrame(self.overlay, fg_color="transparent")
        nav.pack(fill="x", pady=(15, 0))
        self._sk_block(nav, width=50, height=30, fg_color=sk, corner_radius=6).pack(side="left", padx=(L, 0))
        self._sk_block(nav, width=160, height=20, fg_color=sk, corner_radius=4).pack(side="left", padx=5, pady=(15, 10))

        # "Sign up to get started with BHFinder" (notes_label)
        self._sk_block(self.overlay, width=213, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=90)

        # ---- Personal Details (section_1_label) ----
        self._sk_block(self.overlay, width=150, height=20, fg_color=sk, corner_radius=4).pack(anchor="w", padx=90, pady=(10, 10))

        # First Name
        fn_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        fn_frame.pack(pady=(0, 5))
        self._sk_block(fn_frame, width=100, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(L, 0), pady=(0, 5))
        self._sk_block(fn_frame, width=W, height=40, fg_color=sk, corner_radius=6).pack()
        ctk.CTkFrame(fn_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(L, 0))

        # Last Name
        ln_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        ln_frame.pack(pady=(0, 15))
        self._sk_block(ln_frame, width=100, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(L, 0), pady=(0, 5))
        self._sk_block(ln_frame, width=W, height=40, fg_color=sk, corner_radius=6).pack()
        ctk.CTkFrame(ln_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(L, 0))

        # Date of Birth
        dob_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        dob_frame.pack(anchor="w", fill="x", pady=(0, 15))
        self._sk_block(dob_frame, width=120, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(100, 0), pady=(0, 5))
        inner = self._sk_block(dob_frame, fg_color=sk, width=W, height=40, corner_radius=6)
        inner.pack()
        inner.pack_propagate(False)
        ctk.CTkFrame(dob_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(100, 0))

        # Email
        em_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        em_frame.pack(pady=(0, 15))
        self._sk_block(em_frame, width=80, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(L, 0), pady=(0, 5))
        self._sk_block(em_frame, width=W, height=40, fg_color=sk, corner_radius=6).pack()
        ctk.CTkFrame(em_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(L, 0))

        # Phone
        ph_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        ph_frame.pack(pady=(0, 15))
        self._sk_block(ph_frame, width=120, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(L, 0), pady=(0, 5))
        self._sk_block(ph_frame, width=W, height=40, fg_color=sk, corner_radius=6).pack()
        ctk.CTkFrame(ph_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(L, 0))

        # ---- Location Details (section_2_label) ----
        self._sk_block(self.overlay, width=150, height=20, fg_color=sk, corner_radius=4).pack(anchor="w", padx=90, pady=(15, 10))

        # Province
        pv_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        pv_frame.pack(pady=(0, 5))
        self._sk_block(pv_frame, width=80, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(L, 0), pady=(0, 2))
        self._sk_block(pv_frame, width=W, height=40, fg_color=sk, corner_radius=6).pack(pady=(0, 10))
        ctk.CTkFrame(pv_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(L, 0))

        # City
        ct_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        ct_frame.pack(pady=(0, 5))
        self._sk_block(ct_frame, width=60, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(L, 0), pady=(5, 2))
        self._sk_block(ct_frame, width=W, height=40, fg_color=sk, corner_radius=6).pack(pady=(0, 10))
        ctk.CTkFrame(ct_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(L, 0))

        # Barangay
        br_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        br_frame.pack(pady=(0, 5))
        self._sk_block(br_frame, width=80, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(L, 0), pady=(5, 2))
        self._sk_block(br_frame, width=W, height=40, fg_color=sk, corner_radius=6).pack(pady=(0, 10))
        ctk.CTkFrame(br_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(L, 0))

        # Street
        st_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        st_frame.pack(pady=(0, 15))
        self._sk_block(st_frame, width=70, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(L, 0), pady=(0, 5))
        self._sk_block(st_frame, width=W, height=40, fg_color=sk, corner_radius=6).pack()
        ctk.CTkFrame(st_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(L, 0))

        # ---- Account Security (section_3_label) ----
        self._sk_block(self.overlay, width=180, height=20, fg_color=sk, corner_radius=4).pack(anchor="w", padx=90, pady=(15, 10))

        # Password
        pw_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        pw_frame.pack(pady=(0, 15))
        self._sk_block(pw_frame, width=90, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(L, 0), pady=(0, 5))
        self._sk_block(pw_frame, width=W, height=40, fg_color=sk, corner_radius=6).pack()
        ctk.CTkFrame(pw_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(L, 0))

        # Requirements (2x2 grid)
        req_outer = ctk.CTkFrame(self.overlay, fg_color="transparent")
        req_outer.pack(anchor="w", padx=L, pady=(2, 4))
        for r in range(2):
            row = ctk.CTkFrame(req_outer, fg_color="transparent")
            row.pack(anchor="w")
            self._sk_block(row, width=130, height=12, fg_color=sk, corner_radius=3).pack(side="left", padx=(0, 20), pady=1)
            self._sk_block(row, width=130, height=12, fg_color=sk, corner_radius=3).pack(side="left", pady=1)

        # Confirm Password
        cp_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        cp_frame.pack(pady=(0, 15))
        self._sk_block(cp_frame, width=150, height=14, fg_color=sk, corner_radius=4).pack(anchor="w", padx=(L, 0), pady=(0, 5))
        self._sk_block(cp_frame, width=W, height=40, fg_color=sk, corner_radius=6).pack()
        ctk.CTkFrame(cp_frame, height=14, fg_color="transparent").pack(anchor="w", fill="x", padx=(L, 0))

        # ToS (checkbox + link rows)
        tos_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        tos_frame.pack(anchor="center", pady=(5, 0), padx=100)
        self._sk_block(tos_frame, width=240, height=18, fg_color=sk, corner_radius=4).pack(side="left")

        tos2 = ctk.CTkFrame(self.overlay, fg_color="transparent")
        tos2.pack(anchor="center")
        self._sk_block(tos2, width=200, height=18, fg_color=sk, corner_radius=4).pack()

        # Register button
        self._sk_block(self.overlay, width=W, height=45, fg_color=sk, corner_radius=6).pack(pady=(10, 40))

    # ---- Form build & reveal ----

    def _prepare_register_form(self):
        if not getattr(self, "overlay", None):
            return
        self._building_under_skeleton = True
        try:
            self.show_register_page()
        finally:
            self._building_under_skeleton = False
        self._form_ready = True
        # Restart pulse if form finished before min display time
        if getattr(self, "overlay", None) and not getattr(self, "_pulse_timer", None):
            self._start_pulse_animation()
        self._try_reveal()

    def _try_reveal(self):
        if not self._form_ready or not getattr(self, "overlay", None):
            return
        elapsed_ms = (time.monotonic() - self._skeleton_start) * 1000
        if elapsed_ms >= _MIN_SKELETON_MS:
            self._stop_skeleton()
            return
        self._reveal_timer = self.after(
            int(_MIN_SKELETON_MS - elapsed_ms),
            self._try_reveal,
        )

    # ---- Fade animation ----

    _FADE_MIN = "#E0E0E0"
    _FADE_MAX = "#F0F0F0"
    _FADE_STEPS = 5
    _FADE_MS = 60

    def _start_pulse_animation(self):
        self._fade_step = 0
        self._fade_dir = 1
        self._pulse_tick()

    def _lerp_color(self, c1, c2, t):
        r1 = int(c1[1:3], 16)
        g1 = int(c1[3:5], 16)
        b1 = int(c1[5:7], 16)
        r2 = int(c2[1:3], 16)
        g2 = int(c2[3:5], 16)
        b2 = int(c2[5:7], 16)
        r = r1 + (r2 - r1) * t
        g = g1 + (g2 - g1) * t
        b = b1 + (b2 - b1) * t
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    def _pulse_tick(self):
        if not getattr(self, "overlay", None):
            return
        t = self._fade_step / self._FADE_STEPS
        color = self._lerp_color(self._FADE_MIN, self._FADE_MAX, t)
        for block in getattr(self, "_sk_blocks", []):
            try:
                block.configure(fg_color=color)
            except Exception:
                pass
        self._fade_step += self._fade_dir
        if self._fade_step >= self._FADE_STEPS:
            self._fade_step = self._FADE_STEPS
            self._fade_dir = -1
        elif self._fade_step <= 0:
            self._fade_step = 0
            self._fade_dir = 1
        self._pulse_timer = self.after(self._FADE_MS, self._pulse_tick)

    def _stop_pulse_animation(self):
        timer = getattr(self, "_pulse_timer", None)
        if timer:
            try:
                self.after_cancel(timer)
            except Exception:
                pass
        self._pulse_timer = None
