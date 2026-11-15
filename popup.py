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


class TranslationPopup:
    WIDTH_MIN = 220
    WIDTH_MAX = 420
    HEIGHT_MIN = 70
    HEIGHT_MAX = 320
    HEADER_HEIGHT = 26
    PADDING = 8
    BORDER = 1
    GAP = 12
    SCROLLBAR_WIDTH = 8

    def __init__(self):
        self._queue = queue.Queue()
        self._thread = None
        self._start_lock = threading.Lock()
        self._ready = threading.Event()
        self._root = None
        self._text_widget = None
        self._scrollbar = None
        self._copy_btn = None
        self._copy_feedback_id = None
        self._font = None
        self._line_height = 14
        self._dpi_scale = 1.0
        self._width_min = self.WIDTH_MIN
        self._width_max = self.WIDTH_MAX
        self._height_min = self.HEIGHT_MIN
        self._height_max = self.HEIGHT_MAX
        self._header_height = self.HEADER_HEIGHT
        self._padding = self.PADDING
        self._border = self.BORDER
        self._gap = self.GAP
        self._scrollbar_visible = False
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
        self._padding = int(round(self.PADDING * dpi_scale))
        self._border = int(round(self.BORDER * dpi_scale))
        self._gap = int(round(self.GAP * dpi_scale))
        self._root.withdraw()
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.configure(bg="#262626")
        self._root.resizable(False, False)

        self._font = tkfont.Font(family="Segoe UI", size=10)
        self._line_height = self._font.metrics("linespace")

        container = tk.Frame(self._root, bg="#000000")
        container.pack(fill="both", expand=True, padx=self._border, pady=self._border)

        header = tk.Frame(container, bg="#000000", height=self._header_height)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        btn_pad = int(round(8 * dpi_scale))
        btn_gap = int(round(4 * dpi_scale))
        btn_pad_y = int(round(2 * dpi_scale))

        close_btn = tk.Label(
            header,
            text="\u2715",
            bg="#000000",
            fg="#FFFFFF",
            font=self._font,
            padx=btn_pad,
            cursor="hand2",
        )
        close_btn.pack(side="right", padx=(0, btn_gap), pady=btn_pad_y)
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg="#222222"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg="#000000"))
        close_btn.bind("<Button-1>", self._on_close_click)

        self._copy_btn = tk.Label(
            header,
            text="\u29C9",
            bg="#000000",
            fg="#FFFFFF",
            font=self._font,
            padx=btn_pad,
            cursor="hand2",
        )
        self._copy_btn.pack(side="right", padx=(0, btn_gap), pady=btn_pad_y)
        self._copy_btn.bind("<Enter>", lambda e: self._copy_btn.configure(bg="#222222"))
        self._copy_btn.bind("<Leave>", lambda e: self._copy_btn.configure(bg="#000000"))
        self._copy_btn.bind("<Button-1>", self._on_copy_click)

        body = tk.Frame(container, bg="#000000")
        body.pack(side="top", fill="both", expand=True, padx=self._padding, pady=(0, self._padding))

        self._scrollbar = tk.Scrollbar(
            body,
            orient="vertical",
            width=self.SCROLLBAR_WIDTH,
            bg="#1A1A1A",
            troughcolor="#000000",
            activebackground="#333333",
            bd=0,
            relief="flat",
            highlightthickness=0,
        )

        self._text_widget = tk.Text(
            body,
            bg="#000000",
            fg="#FFFFFF",
            insertbackground="#000000",
            selectbackground="#333333",
            selectforeground="#FFFFFF",
            relief="flat",
            bd=0,
            wrap="word",
            font=("Segoe UI", 10),
            state="disabled",
            highlightthickness=0,
            padx=0,
            pady=0,
            yscrollcommand=self._scrollbar.set,
        )
        self._scrollbar.configure(command=self._text_widget.yview)
        self._text_widget.pack(side="left", fill="both", expand=True)

        self._text_widget.bind("<Control-c>", self._copy_selection)
        self._text_widget.bind("<Control-C>", self._copy_selection)
        self._text_widget.bind("<Control-a>", self._select_all)
        self._text_widget.bind("<Control-A>", self._select_all)
        self._text_widget.bind("<MouseWheel>", self._on_mousewheel)

        for widget in (header, body):
            widget.bind("<ButtonPress-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)
            widget.bind("<MouseWheel>", self._on_mousewheel)

    def show(self, text):
        if not text:
            return
        self._queue.put(("show", text))

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
                        self._apply_show(payload)
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
                        self._copy_btn = None
                        self._font = None
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

    def _apply_show(self, text):
        self._current_text = text
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
        self._visible = True

    def _apply_close(self):
        try:
            self._text_widget.configure(state="normal")
            self._text_widget.delete("1.0", "end")
            self._text_widget.configure(state="disabled")
        except Exception:
            pass
        if self._copy_feedback_id is not None:
            try:
                self._root.after_cancel(self._copy_feedback_id)
            except Exception:
                pass
            self._copy_feedback_id = None
        if self._copy_btn is not None:
            try:
                self._copy_btn.configure(text="\u29C9")
            except Exception:
                pass
        self._current_text = None
        self._is_pinned = False
        self._pinned_x = None
        self._pinned_y = None
        self._visible = False
        self._root.withdraw()

    def _set_scrollbar(self, visible):
        if visible and not self._scrollbar_visible:
            self._scrollbar.pack(side="right", fill="y")
            self._scrollbar_visible = True
        elif not visible and self._scrollbar_visible:
            self._scrollbar.pack_forget()
            self._scrollbar_visible = False

    def _measure(self, text):
        border = 2 * self._border
        padding = 2 * self._padding

        longest = 0
        for line in text.splitlines() or [""]:
            try:
                longest = max(longest, self._font.measure(line))
            except Exception:
                longest = max(longest, len(line) * 7)
        text_width = min(longest, self._width_max - border - padding)
        width = max(self._width_min, min(self._width_max, text_width + border + padding))

        wrap_px = max(1, width - border - padding - self.SCROLLBAR_WIDTH)
        wrapped = 0
        for line in text.splitlines() or [""]:
            wrapped += self._wrap_lines(line, wrap_px)

        total = wrapped * self._line_height + self._header_height + padding + border
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

    def _apply_noactivate(self):
        try:
            hwnd = self._root.winfo_id()
            parent = _user32.GetParent(hwnd)
            if parent:
                hwnd = parent
            style = _get_window_long(hwnd, _GWL_EXSTYLE)
            if not (style & _WS_EX_NOACTIVATE):
                _set_window_long(hwnd, _GWL_EXSTYLE, style | _WS_EX_NOACTIVATE)
        except Exception:
            pass

    def _on_close_click(self, event):
        self._apply_close()
        return "break"

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
        if self._copy_btn is None:
            return
        self._copy_btn.configure(text="\u2713")
        if self._copy_feedback_id is not None:
            try:
                self._root.after_cancel(self._copy_feedback_id)
            except Exception:
                pass
        self._copy_feedback_id = self._root.after(1000, self._restore_copy_icon)

    def _restore_copy_icon(self):
        self._copy_feedback_id = None
        if self._copy_btn is not None:
            try:
                self._copy_btn.configure(text="\u29C9")
            except Exception:
                pass

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
