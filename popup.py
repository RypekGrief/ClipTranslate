import ctypes
import queue
import threading
import tkinter as tk
import tkinter.font as tkfont
from ctypes import wintypes

import pyperclip

_MONITOR_DEFAULTTONEAREST = 2
_GWL_EXSTYLE = -20
_WS_EX_NOACTIVATE = 0x08000000

_BG = "#1C1F26"
_PILL_BG = "#282D37"
_BUTTON_BG = "#282D37"
_BUTTON_HOVER = "#353B48"
_TEXT_FG = "#F3F4F6"
_BADGE_FG = "#E5E7EB"
_SELECT_BG = "#3B4252"
_SCROLL_THUMB = "#4B5563"
_SCROLL_THUMB_HOVER = "#6B7280"
_COPY_OK = "#4ADE80"
_DWMWA_WINDOW_CORNER_PREFERENCE = 33
_DWMWA_BORDER_COLOR = 34
_DWMWCP_ROUND = 2
_DWMWA_BORDER_SLATE = 0x00463E36


class _RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class _MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", _RECT),
        ("rcWork", _RECT),
        ("dwFlags", wintypes.DWORD),
    ]


_user32 = ctypes.WinDLL("user32", use_last_error=True)
_user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
_user32.GetCursorPos.restype = wintypes.BOOL
_user32.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
_user32.MonitorFromPoint.restype = wintypes.HANDLE
_user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_MONITORINFO)]
_user32.GetMonitorInfoW.restype = wintypes.BOOL
_user32.GetParent.argtypes = [wintypes.HWND]
_user32.GetParent.restype = wintypes.HWND

if hasattr(_user32, "GetWindowLongPtrW"):
    _get_window_long = _user32.GetWindowLongPtrW
    _set_window_long = _user32.SetWindowLongPtrW
else:
    _get_window_long = _user32.GetWindowLongW
    _set_window_long = _user32.SetWindowLongW

_get_window_long.argtypes = [wintypes.HWND, ctypes.c_int]
_get_window_long.restype = ctypes.c_ssize_t
_set_window_long.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
_set_window_long.restype = ctypes.c_ssize_t

try:
    _dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)
    _dwmapi.DwmSetWindowAttribute.argtypes = [
        wintypes.HWND,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    _dwmapi.DwmSetWindowAttribute.restype = ctypes.HRESULT
except Exception:
    _dwmapi = None


class TranslationPopup:
    WIDTH_MIN = 220
    WIDTH_MAX = 420
    HEIGHT_MIN = 70
    HEIGHT_MAX = 320
    HEADER_HEIGHT = 34
    FOOTER_HEIGHT = 32
    PADDING = 10
    TEXT_PAD = 6
    GAP = 12
    SCROLLBAR_WIDTH = 7
    BTN_SIZE = 22
    BADGE_HEIGHT = 20
    SPACING_1 = 2
    SPACING_2 = 3

    def __init__(self):
        self._queue = queue.Queue()
        self._thread = None
        self._start_lock = threading.Lock()
        self._ready = threading.Event()
        self._root = None
        self._text_widget = None
        self._scrollbar = None
        self._badge_canvas = None
        self._close_canvas = None
        self._copy_canvas = None
        self._badge_label = None
        self._copy_feedback_id = None
        self._font = None
        self._badge_font = None
        self._line_height = 16
        self._dpi_scale = 1.0
        self._width_min = self.WIDTH_MIN
        self._width_max = self.WIDTH_MAX
        self._height_min = self.HEIGHT_MIN
        self._height_max = self.HEIGHT_MAX
        self._header_height = self.HEADER_HEIGHT
        self._footer_height = self.FOOTER_HEIGHT
        self._padding = self.PADDING
        self._text_pad = self.TEXT_PAD
        self._gap = self.GAP
        self._sb_width = self.SCROLLBAR_WIDTH
        self._btn_size = self.BTN_SIZE
        self._badge_h = self.BADGE_HEIGHT
        self._pill_pad = 8
        self._spacing_1 = self.SPACING_1
        self._spacing_2 = self.SPACING_2
        self._scrollbar_visible = False
        self._scroll_first = 0.0
        self._scroll_last = 1.0
        self._scroll_hover = False
        self._scroll_drag = False
        self._scroll_drag_offset = 0
        self._close_hover = False
        self._copy_hover = False
        self._current_text = None
        self._is_pinned = False
        self._pinned_x = None
        self._pinned_y = None
        self._visible = False
        self._drag_offset_x = 0
        self._drag_offset_y = 0
        self._start()

    def _start(self):
        with self._start_lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._ready.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
        self._ready.wait(3.0)

    def _run(self):
        try:
            self._build()
        except Exception:
            self._ready.set()
            return
        self._ready.set()
        self._root.after(40, self._drain)
        self._root.mainloop()

    def _build(self):
        self._root = tk.Tk()
        dpi_scale = max(1.0, self._root.winfo_fpixels("1i") / 96.0)
        self._dpi_scale = dpi_scale
        self._width_min = int(round(self.WIDTH_MIN * dpi_scale))
        self._width_max = int(round(self.WIDTH_MAX * dpi_scale))
        self._height_min = int(round(self.HEIGHT_MIN * dpi_scale))
        self._height_max = int(round(self.HEIGHT_MAX * dpi_scale))
        self._header_height = int(round(self.HEADER_HEIGHT * dpi_scale))
        self._footer_height = int(round(self.FOOTER_HEIGHT * dpi_scale))
        self._padding = int(round(self.PADDING * dpi_scale))
        self._text_pad = int(round(self.TEXT_PAD * dpi_scale))
        self._gap = int(round(self.GAP * dpi_scale))
        self._sb_width = max(4, int(round(self.SCROLLBAR_WIDTH * dpi_scale)))
        self._btn_size = int(round(self.BTN_SIZE * dpi_scale))
        self._badge_h = int(round(self.BADGE_HEIGHT * dpi_scale))
        self._pill_pad = int(round(8 * dpi_scale))
        self._spacing_1 = int(round(self.SPACING_1 * dpi_scale))
        self._spacing_2 = int(round(self.SPACING_2 * dpi_scale))
        self._root.withdraw()
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", 0.96)
        self._root.configure(bg=_BG)
        self._root.resizable(False, False)

        self._font = tkfont.Font(family="Segoe UI", size=11)
        self._badge_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self._line_height = self._font.metrics("linespace") + self._spacing_2

        header = tk.Frame(self._root, bg=_BG, height=self._header_height)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        self._badge_canvas = tk.Canvas(
            header,
            bg=_BG,
            width=1,
            height=self._badge_h,
            highlightthickness=0,
            bd=0,
        )
        self._badge_canvas.pack(
            side="left",
            padx=(self._padding, 0),
            pady=(self._header_height - self._badge_h) // 2,
        )

        btn_pady = (self._header_height - self._btn_size) // 2
        self._close_canvas = tk.Canvas(
            header,
            bg=_BG,
            width=self._btn_size,
            height=self._btn_size,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._close_canvas.pack(side="right", padx=(0, self._padding), pady=btn_pady)
        self._close_canvas.bind("<Enter>", self._on_close_enter)
        self._close_canvas.bind("<Leave>", self._on_close_leave)
        self._close_canvas.bind("<Button-1>", self._on_close_click)

        footer = tk.Frame(self._root, bg=_BG, height=self._footer_height)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        self._copy_canvas = tk.Canvas(
            footer,
            bg=_BG,
            width=self._btn_size,
            height=self._btn_size,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._copy_canvas.pack(
            side="right",
            padx=(0, self._padding),
            pady=(self._footer_height - self._btn_size) // 2,
        )
        self._copy_canvas.bind("<Enter>", self._on_copy_enter)
        self._copy_canvas.bind("<Leave>", self._on_copy_leave)
        self._copy_canvas.bind("<Button-1>", self._on_copy_click)

        body = tk.Frame(self._root, bg=_BG)
        body.pack(side="top", fill="both", expand=True, padx=self._padding)

        self._scrollbar = tk.Canvas(
            body,
            bg=_BG,
            width=self._sb_width,
            highlightthickness=0,
            bd=0,
            cursor="arrow",
        )
        self._scrollbar.bind("<Configure>", self._on_scroll_configure)
        self._scrollbar.bind("<Enter>", self._on_scroll_enter)
        self._scrollbar.bind("<Leave>", self._on_scroll_leave)
        self._scrollbar.bind("<ButtonPress-1>", self._on_scroll_press)
        self._scrollbar.bind("<B1-Motion>", self._on_scroll_motion)
        self._scrollbar.bind("<ButtonRelease-1>", self._on_scroll_release)

        self._text_widget = tk.Text(
            body,
            bg=_BG,
            fg=_TEXT_FG,
            insertbackground=_BG,
            selectbackground=_SELECT_BG,
            selectforeground="#FFFFFF",
            relief="flat",
            bd=0,
            wrap="word",
            font=self._font,
            state="disabled",
            highlightthickness=0,
            padx=self._text_pad,
            pady=self._text_pad,
            spacing1=self._spacing_1,
            spacing2=self._spacing_2,
            yscrollcommand=self._on_text_scroll,
        )
        self._text_widget.pack(side="left", fill="both", expand=True)

        self._text_widget.bind("<Control-c>", self._copy_selection)
        self._text_widget.bind("<Control-C>", self._copy_selection)
        self._text_widget.bind("<Control-a>", self._select_all)
        self._text_widget.bind("<Control-A>", self._select_all)
        self._text_widget.bind("<MouseWheel>", self._on_mousewheel)

        for widget in (header, footer, self._scrollbar):
            widget.bind("<MouseWheel>", self._on_mousewheel)
        for widget in (header, footer):
            widget.bind("<ButtonPress-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)

        self._draw_close_button()
        self._draw_copy_button()

    def show(self, text, badge_label="Target Language: EN"):
        if not text:
            return
        self._queue.put(("show", (text, badge_label)))

    def close(self):
        self._queue.put(("close", None))

    def shutdown(self):
        self._queue.put(("shutdown", None))
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=3.0)

    def _drain(self):
        try:
            while True:
                action, payload = self._queue.get_nowait()
                try:
                    if action == "show":
                        self._apply_show(*payload)
                    elif action == "close":
                        self._apply_close()
                    elif action == "shutdown":
                        self._apply_close()
                        try:
                            self._root.destroy()
                        except Exception:
                            pass
                        self._text_widget = None
                        self._scrollbar = None
                        self._badge_canvas = None
                        self._close_canvas = None
                        self._copy_canvas = None
                        self._font = None
                        self._badge_font = None
                        self._root = None
                        return
                except Exception:
                    pass
        except queue.Empty:
            pass
        try:
            self._root.after(40, self._drain)
        except Exception:
            pass

    def _apply_show(self, text, badge_label="Target Language: EN"):
        self._current_text = text
        self._update_badge(badge_label)
        self._text_widget.configure(state="normal")
        self._text_widget.delete("1.0", "end")
        self._text_widget.insert("1.0", text)
        self._text_widget.configure(state="disabled")
        self._text_widget.yview_moveto(0.0)

        width, height, needs_scroll = self._measure(text)
        self._set_scrollbar(needs_scroll)

        if self._is_pinned and self._pinned_x is not None and self._pinned_y is not None:
            x, y = self._clamp(self._pinned_x, self._pinned_y, width, height)
        else:
            cursor_x, cursor_y = self._cursor_pos()
            x = cursor_x + self._gap
            y = cursor_y - height - self._gap
            x, y = self._clamp(x, y, width, height, (cursor_x, cursor_y))

        self._root.geometry(f"{width}x{height}+{x}+{y}")
        self._apply_noactivate()
        self._root.deiconify()
        self._root.lift()
        self._root.update_idletasks()
        self._scroll_first, self._scroll_last = self._text_widget.yview()
        self._apply_dwm()
        self._draw_scroll_thumb()
        self._visible = True

    def _apply_close(self):
        try:
            self._text_widget.configure(state="normal")
            self._text_widget.delete("1.0", "end")
            self._text_widget.configure(state="disabled")
        except Exception:
            pass
        try:
            self._badge_canvas.delete("all")
            self._badge_canvas.configure(width=1)
        except Exception:
            pass
        self._badge_label = None
        if self._copy_feedback_id is not None:
            try:
                self._root.after_cancel(self._copy_feedback_id)
            except Exception:
                pass
            self._copy_feedback_id = None
        self._draw_copy_button()
        self._set_scrollbar(False)
        self._scroll_first = 0.0
        self._scroll_last = 1.0
        self._scroll_hover = False
        self._scroll_drag = False
        self._current_text = None
        self._is_pinned = False
        self._pinned_x = None
        self._pinned_y = None
        self._visible = False
        self._root.withdraw()

    def _update_badge(self, badge_label):
        if not badge_label:
            badge_label = "Target Language: EN"
        self._badge_label = badge_label
        try:
            text_w = self._badge_font.measure(badge_label)
        except Exception:
            text_w = len(badge_label) * 7
        pill_w = text_w + 2 * self._pill_pad
        pill_h = self._badge_h
        canvas = self._badge_canvas
        canvas.configure(width=pill_w, height=pill_h)
        canvas.delete("all")
        self._round_rect(canvas, 1, 1, pill_w - 1, pill_h - 1, max(2, (pill_h - 2) // 2), _PILL_BG)
        canvas.create_text(
            pill_w // 2,
            pill_h // 2,
            text=badge_label,
            fill=_BADGE_FG,
            font=self._badge_font,
            anchor="center",
        )

    @staticmethod
    def _round_rect(canvas, x1, y1, x2, y2, radius, fill):
        radius = max(1, min(int(radius), int((x2 - x1) // 2), int((y2 - y1) // 2)))
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, splinesteps=12, fill=fill, outline="")

    def _draw_close_button(self):
        canvas = self._close_canvas
        if canvas is None:
            return
        canvas.delete("all")
        size = self._btn_size
        fill = _BUTTON_HOVER if self._close_hover else _BUTTON_BG
        fg = "#FFFFFF" if self._close_hover else _BADGE_FG
        canvas.create_oval(1, 1, size - 1, size - 1, fill=fill, outline="")
        line_w = max(1, int(round(1.4 * self._dpi_scale)))
        inset = size * 0.33
        canvas.create_line(inset, inset, size - inset, size - inset, fill=fg, width=line_w, capstyle="round")
        canvas.create_line(inset, size - inset, size - inset, inset, fill=fg, width=line_w, capstyle="round")

    def _draw_copy_button(self):
        canvas = self._copy_canvas
        if canvas is None:
            return
        canvas.delete("all")
        size = self._btn_size
        fill = _BUTTON_HOVER if self._copy_hover else _BUTTON_BG
        canvas.create_oval(1, 1, size - 1, size - 1, fill=fill, outline="")
        line_w = max(1, int(round(1.3 * self._dpi_scale)))
        if self._copy_feedback_id is not None:
            check_w = max(2, int(round(1.8 * self._dpi_scale)))
            canvas.create_line(
                size * 0.30, size * 0.52,
                size * 0.44, size * 0.67,
                size * 0.71, size * 0.35,
                fill=_COPY_OK,
                width=check_w,
                capstyle="round",
                joinstyle="round",
            )
            return
        canvas.create_rectangle(
            size * 0.27, size * 0.23, size * 0.68, size * 0.60,
            outline=_BADGE_FG, width=line_w,
        )
        canvas.create_rectangle(
            size * 0.35, size * 0.34, size * 0.76, size * 0.71,
            outline=_BADGE_FG, fill=fill, width=line_w,
        )

    def _set_scrollbar(self, visible):
        if visible and not self._scrollbar_visible:
            self._scrollbar.pack(
                side="right",
                fill="y",
                padx=(max(4, self._text_pad // 2), 0),
                before=self._text_widget,
            )
            self._scrollbar_visible = True
            self._scrollbar.configure(cursor="hand2")
        elif not visible and self._scrollbar_visible:
            self._scrollbar.pack_forget()
            self._scrollbar_visible = False
            self._scrollbar.configure(cursor="arrow")
            self._scrollbar.delete("all")

    def _on_text_scroll(self, first, last):
        try:
            self._scroll_first = float(first)
            self._scroll_last = float(last)
        except (TypeError, ValueError):
            return
        self._draw_scroll_thumb()

    def _draw_scroll_thumb(self):
        canvas = self._scrollbar
        if canvas is None or not self._scrollbar_visible:
            return
        try:
            height = canvas.winfo_height()
        except Exception:
            return
        if height <= 1:
            return
        canvas.delete("all")
        top = self._scroll_first * height
        bottom = self._scroll_last * height
        min_thumb = max(12, int(round(24 * self._dpi_scale)))
        if bottom - top < min_thumb:
            bottom = top + min_thumb
        if bottom > height:
            bottom = height
            top = max(0, bottom - min_thumb)
        fill = _SCROLL_THUMB_HOVER if (self._scroll_hover or self._scroll_drag) else _SCROLL_THUMB
        width = self._sb_width
        if bottom - top < width:
            bottom = top + width
        canvas.create_oval(0, top, width, top + width, fill=fill, outline="")
        canvas.create_rectangle(0, top + width / 2, width, bottom - width / 2, fill=fill, outline="")
        canvas.create_oval(0, bottom - width, width, bottom, fill=fill, outline="")

    def _on_scroll_configure(self, event):
        self._draw_scroll_thumb()

    def _on_scroll_enter(self, event):
        self._scroll_hover = True
        self._draw_scroll_thumb()

    def _on_scroll_leave(self, event):
        self._scroll_hover = False
        self._draw_scroll_thumb()

    def _on_scroll_press(self, event):
        if not self._scrollbar_visible:
            return "break"
        height = max(1, self._scrollbar.winfo_height())
        self._scroll_drag = True
        self._scroll_drag_offset = event.y - self._scroll_first * height
        self._draw_scroll_thumb()
        return "break"

    def _on_scroll_motion(self, event):
        if not self._scroll_drag:
            return "break"
        height = max(1, self._scrollbar.winfo_height())
        frac = (event.y - self._scroll_drag_offset) / height
        frac = max(0.0, min(1.0, frac))
        self._text_widget.yview_moveto(frac)
        return "break"

    def _on_scroll_release(self, event):
        self._scroll_drag = False
        self._draw_scroll_thumb()
        return "break"

    def _measure(self, text):
        horizontal = 2 * self._padding + 2 * self._text_pad + self._sb_width

        longest = 0
        for line in text.splitlines() or [""]:
            try:
                longest = max(longest, self._font.measure(line))
            except Exception:
                longest = max(longest, len(line) * 7)
        text_width = min(longest, self._width_max - horizontal)
        width = max(self._width_min, min(self._width_max, text_width + horizontal))

        wrap_px = max(1, width - horizontal)
        wrapped = 0
        for line in text.splitlines() or [""]:
            wrapped += self._wrap_lines(line, wrap_px)

        total = (
            wrapped * self._line_height
            + 2 * self._text_pad
            + self._header_height
            + self._footer_height
        )
        needs_scroll = total > self._height_max
        height = max(self._height_min, min(self._height_max, total))
        return width, height, needs_scroll

    def _wrap_lines(self, line, max_px):
        if not line:
            return 1
        words = line.split(" ")
        lines = 1
        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if self._font.measure(candidate) <= max_px:
                current = candidate
                continue
            if current:
                lines += 1
                current = ""
            if self._font.measure(word) <= max_px:
                current = word
                continue
            chunk = ""
            for ch in word:
                if self._font.measure(chunk + ch) <= max_px:
                    chunk += ch
                else:
                    if chunk:
                        lines += 1
                    chunk = ch
            current = chunk
        return lines

    def _cursor_pos(self):
        try:
            pt = wintypes.POINT()
            if _user32.GetCursorPos(ctypes.byref(pt)):
                return int(pt.x), int(pt.y)
        except Exception:
            pass
        return 0, 0

    def _clamp(self, x, y, width, height, ref=None):
        try:
            px, py = ref if ref is not None else (x, y)
            pt = wintypes.POINT(int(px), int(py))
            monitor = _user32.MonitorFromPoint(pt, _MONITOR_DEFAULTTONEAREST)
            info = _MONITORINFO()
            info.cbSize = ctypes.sizeof(_MONITORINFO)
            if monitor and _user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
                work = info.rcWork
                x = max(work.left, min(int(x), work.right - width))
                y = max(work.top, min(int(y), work.bottom - height))
        except Exception:
            pass
        return int(x), int(y)

    def _window_handle(self):
        hwnd = self._root.winfo_id()
        parent = _user32.GetParent(hwnd)
        if parent:
            hwnd = parent
        return hwnd

    def _apply_noactivate(self):
        try:
            hwnd = self._window_handle()
            style = _get_window_long(hwnd, _GWL_EXSTYLE)
            if not (style & _WS_EX_NOACTIVATE):
                _set_window_long(hwnd, _GWL_EXSTYLE, style | _WS_EX_NOACTIVATE)
        except Exception:
            pass

    def _apply_dwm(self):
        if _dwmapi is None:
            return
        try:
            hwnd = self._window_handle()
            pref = ctypes.c_int(_DWMWCP_ROUND)
            _dwmapi.DwmSetWindowAttribute(
                hwnd,
                _DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(pref),
                ctypes.sizeof(pref),
            )
            color = ctypes.c_uint(_DWMWA_BORDER_SLATE)
            _dwmapi.DwmSetWindowAttribute(
                hwnd,
                _DWMWA_BORDER_COLOR,
                ctypes.byref(color),
                ctypes.sizeof(color),
            )
        except Exception:
            pass

    def _on_close_enter(self, event):
        self._close_hover = True
        self._draw_close_button()

    def _on_close_leave(self, event):
        self._close_hover = False
        self._draw_close_button()

    def _on_close_click(self, event):
        self._apply_close()
        return "break"

    def _on_copy_enter(self, event):
        self._copy_hover = True
        self._draw_copy_button()

    def _on_copy_leave(self, event):
        self._copy_hover = False
        self._draw_copy_button()

    def _on_copy_click(self, event):
        self._copy_text()
        return "break"

    def _copy_text(self):
        if not self._current_text:
            return
        try:
            pyperclip.copy(self._current_text)
        except Exception:
            pass
        if self._copy_canvas is None:
            return
        if self._copy_feedback_id is not None:
            try:
                self._root.after_cancel(self._copy_feedback_id)
            except Exception:
                pass
        self._copy_feedback_id = self._root.after(1000, self._restore_copy_icon)
        self._draw_copy_button()

    def _restore_copy_icon(self):
        self._copy_feedback_id = None
        self._draw_copy_button()

    def _copy_selection(self, event):
        try:
            selected = self._text_widget.get("sel.first", "sel.last")
        except tk.TclError:
            return "break"
        if selected:
            self._root.clipboard_clear()
            self._root.clipboard_append(selected)
        return "break"

    def _select_all(self, event):
        self._text_widget.tag_add("sel", "1.0", "end-1c")
        return "break"

    def _on_mousewheel(self, event):
        if self._scrollbar_visible:
            self._text_widget.yview_scroll(int(-event.delta / 120), "units")
        return "break"

    def _on_drag_start(self, event):
        self._drag_offset_x = event.x_root - self._root.winfo_x()
        self._drag_offset_y = event.y_root - self._root.winfo_y()
        self._is_pinned = True
        self._pinned_x = self._root.winfo_x()
        self._pinned_y = self._root.winfo_y()

    def _on_drag_motion(self, event):
        x = event.x_root - self._drag_offset_x
        y = event.y_root - self._drag_offset_y
        self._root.geometry(f"+{x}+{y}")
        self._is_pinned = True
        self._pinned_x = x
        self._pinned_y = y
