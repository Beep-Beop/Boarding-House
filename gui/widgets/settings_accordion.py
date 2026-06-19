import customtkinter as ctk


class SettingsSection:
    def __init__(self, parent, title_text, entry_border, text_color,
                 primary_color, title_font=None):
        self.is_expanded = False
        self._content_height = None

        self.frame = ctk.CTkFrame(parent, corner_radius=8, border_width=1,
                                   fg_color="transparent",
                                   border_color=entry_border)

        self._header = ctk.CTkFrame(self.frame, fg_color="transparent",
                                    cursor="hand2")
        self._header.pack(fill="x", padx=15, pady=12)

        self._title_label = ctk.CTkLabel(
            self._header, text=title_text,
            font=title_font or ctk.CTkFont(size=16, weight="bold"),
            text_color=text_color)
        self._title_label.pack(side="left")

        self._arrow_label = ctk.CTkLabel(
            self._header, text="\u25b6",
            font=ctk.CTkFont(size=14),
            text_color=text_color)
        self._arrow_label.pack(side="right")

        self._header.bind("<Button-1>", lambda e: self.toggle())
        self._title_label.bind("<Button-1>", lambda e: self.toggle())
        self._arrow_label.bind("<Button-1>", lambda e: self.toggle())

        self._wrapper = ctk.CTkFrame(self.frame, fg_color="transparent",
                                      height=0)
        self._wrapper.pack(fill="x", padx=15, pady=(0, 12))
        self._wrapper.pack_propagate(False)

        self.content_frame = ctk.CTkFrame(self._wrapper, fg_color="transparent")
        self.content_frame.pack(fill="x")

        self._progress = ctk.CTkProgressBar(self.frame, mode="indeterminate",
                                             fg_color=entry_border,
                                             progress_color=primary_color)

    def expand(self):
        if self.is_expanded:
            return
        self.is_expanded = True
        if self._content_height is None:
            self._content_height = self.content_frame.winfo_reqheight()
        self._wrapper.configure(height=self._content_height)
        self._arrow_label.configure(text="\u25bc")

    def collapse(self):
        if not self.is_expanded:
            return
        self.is_expanded = False
        self._wrapper.configure(height=0)
        self._arrow_label.configure(text="\u25b6")

    def toggle(self):
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def _cache_height(self):
        self.content_frame.update_idletasks()
        self._content_height = self.content_frame.winfo_reqheight()
        if self._content_height is None or self._content_height <= 0:
            self._content_height = 1

    def show_progress(self):
        self._progress.pack(fill="x", pady=(5, 0))
        self._progress.start()

    def hide_progress(self):
        self._progress.stop()
        self._progress.pack_forget()


class SectionHandle:
    def __init__(self, section):
        self.content_frame = section.content_frame
        self._section = section

    def cache_content_height(self):
        self._section._cache_height()


class SettingsAccordion(ctk.CTkScrollableFrame):
    def __init__(self, parent, entry_border=("#E0E0E0", "#555555"),
                 text_color=("#3E362A", "#E0DCD3"),
                 primary_color=("#AC7F5E", "#8B6B4E"),
                 title_font=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._entry_border = entry_border
        self._text_color = text_color
        self._primary_color = primary_color
        self._title_font = title_font
        self._sections = []

        self._body = ctk.CTkFrame(self, fg_color="transparent")
        self._body.pack(fill="both", expand=True)

        self._progress = ctk.CTkProgressBar(self._body, mode="indeterminate",
                                             fg_color=entry_border,
                                             progress_color=primary_color)

    def add_section(self, title):
        section = SettingsSection(self._body, title,
                                  entry_border=self._entry_border,
                                  text_color=self._text_color,
                                  primary_color=self._primary_color,
                                  title_font=self._title_font)
        section.frame.pack(fill="x", pady=(0, 10))
        self._sections.append(section)
        return SectionHandle(section)

    def show_progress(self):
        self._progress.pack(fill="x", pady=(0, 10))
        self._progress.start()

    def hide_progress(self):
        self._progress.stop()
        self._progress.pack_forget()

    def expand_first(self):
        if self._sections:
            self._sections[0].expand()
