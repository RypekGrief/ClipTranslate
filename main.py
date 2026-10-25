import importlib
import json
import os
import sys
import time
import ctypes
from ctypes import wintypes
import threading
import winreg

DEPENDENCIES = [
    ("pyperclip", "pyperclip"),
    ("pystray", "pystray"),
    ("PIL", "Pillow"),
    ("keyboard", "keyboard"),
]


def _ensure_dependencies():
    missing = []
    for import_name, pip_name in DEPENDENCIES:
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(pip_name)
    if missing:
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing, "--quiet"]
        )


_ensure_dependencies()

import pyperclip
import keyboard

import translator
import tray

DEFAULT_CONFIG = {
    "hotkey": "ctrl+shift+x",
    "target_language": "en",
    "menu_language": "en",
    "start_with_windows": True,
    "enabled": True,
    "show_notifications": True,
    "auto_paste": True,
}

config = {}
_tray_app = None
_busy = False
_busy_lock = threading.Lock()


def _resource_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_DIR = os.path.join(os.environ["APPDATA"], "ClipTranslate")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
ICON_PATH = os.path.join(_resource_dir(), "icon.ico")


def _migrate_old_config():
    old_paths = []
    if getattr(sys, "frozen", False):
        old_paths.append(os.path.join(os.path.dirname(sys.executable), "config.json"))
    else:
        old_paths.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"))
    for old in old_paths:
        if os.path.isfile(old) and old != CONFIG_PATH:
            import shutil as _shutil
            try:
                _shutil.copy2(old, CONFIG_PATH)
                return
            except OSError:
                pass


def load_config():
    global config, config_was_reset
    config_was_reset = False

    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.isfile(CONFIG_PATH):
        _migrate_old_config()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}
        config_was_reset = True

    changed = False
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
            changed = True

    if changed:
        save_config()


def save_config():
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def set_startup(enable):
    reg_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_SET_VALUE)
        if enable:
            if getattr(sys, "frozen", False):
                cmd = f'"{sys.executable}"'
            else:
                pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
                if os.path.exists(pythonw):
                    cmd = f'"{pythonw}" "{os.path.abspath(__file__)}"'
                else:
                    cmd = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(reg, "ClipTranslate", 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(reg, "ClipTranslate")
            except FileNotFoundError:
                pass
        winreg.CloseKey(reg)
        return True
    except Exception:
        return False


def is_startup_enabled():
    reg_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_READ)
        winreg.QueryValueEx(reg, "ClipTranslate")
        winreg.CloseKey(reg)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


def _cleanup_old_startup_shortcut():
    startup_dir = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup",
    )
    shortcut_path = os.path.join(startup_dir, "ClipTranslate.lnk")
    if os.path.exists(shortcut_path):
        try:
            os.remove(shortcut_path)
        except OSError:
            pass


def _clipboard_wait(timeout=1.0):
    user32 = ctypes.windll.user32
    start_seq = user32.GetClipboardSequenceNumber()
    deadline = time.time() + timeout
    while time.time() < deadline:
        if user32.GetClipboardSequenceNumber() != start_seq:
            return True
        time.sleep(0.01)
    return False


_clip_user32 = ctypes.WinDLL("user32", use_last_error=True)
_clip_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_clip_kernel32.GlobalSize.argtypes = [wintypes.HANDLE]
_clip_kernel32.GlobalSize.restype = ctypes.c_size_t
_clip_kernel32.GlobalLock.argtypes = [wintypes.HANDLE]
_clip_kernel32.GlobalLock.restype = ctypes.c_void_p
_clip_kernel32.GlobalUnlock.argtypes = [wintypes.HANDLE]
_clip_kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
_clip_kernel32.GlobalAlloc.restype = wintypes.HANDLE
_clip_user32.OpenClipboard.argtypes = [wintypes.HWND]
_clip_user32.GetClipboardData.argtypes = [ctypes.c_uint]
_clip_user32.GetClipboardData.restype = wintypes.HANDLE
_clip_user32.SetClipboardData.argtypes = [ctypes.c_uint, wintypes.HANDLE]
_clip_user32.SetClipboardData.restype = wintypes.HANDLE
_clip_user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
_clip_user32.GetAsyncKeyState.restype = wintypes.SHORT
_clip_user32.keybd_event.argtypes = [ctypes.c_byte, ctypes.c_byte, ctypes.c_uint, ctypes.c_void_p]

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_LSHIFT = 0xA0
VK_RSHIFT = 0xA1
VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3
VK_LMENU = 0xA4
VK_RMENU = 0xA5
VK_X = 0x58
KEYEVENTF_KEYUP = 0x0002


def _wait_for_physical_release(timeout=0.5):
    deadline = time.time() + timeout
    vks = (VK_SHIFT, VK_LSHIFT, VK_RSHIFT, VK_CONTROL, VK_LCONTROL, VK_RCONTROL, VK_MENU, VK_LMENU, VK_RMENU, VK_X)
    while time.time() < deadline:
        if not any(_clip_user32.GetAsyncKeyState(vk) & 0x8000 for vk in vks):
            break
        time.sleep(0.01)


def _release_modifiers():
    for vk in (VK_LSHIFT, VK_RSHIFT, VK_SHIFT, VK_LCONTROL, VK_RCONTROL, VK_CONTROL, VK_LMENU, VK_RMENU, VK_MENU):
        if _clip_user32.GetAsyncKeyState(vk) & 0x8000:
            _clip_user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
    for mod in ('shift', 'left shift', 'right shift', 'ctrl', 'left ctrl', 'right ctrl', 'alt', 'left alt', 'right alt'):
        try:
            keyboard.release(mod)
        except Exception:
            pass
    try:
        with keyboard._pressed_events_lock:
            keyboard._pressed_events.clear()
    except Exception:
        pass


def _save_clipboard():
    if not _clip_user32.OpenClipboard(None):
        return {}
    saved = {}
    fmt = 0
    try:
        while True:
            fmt = _clip_user32.EnumClipboardFormats(fmt)
            if not fmt:
                break
            h_data = _clip_user32.GetClipboardData(fmt)
            if h_data:
                size = _clip_kernel32.GlobalSize(h_data)
                ptr = _clip_kernel32.GlobalLock(h_data)
                if ptr:
                    data = ctypes.string_at(ptr, size)
                    _clip_kernel32.GlobalUnlock(h_data)
                    saved[fmt] = (data, size)
    except Exception:
        pass
    finally:
        _clip_user32.CloseClipboard()
    return saved


def _restore_clipboard(saved):
    if not saved:
        return
    if not _clip_user32.OpenClipboard(None):
        return
    try:
        _clip_user32.EmptyClipboard()
        for fmt, (data, size) in saved.items():
            h_data = _clip_kernel32.GlobalAlloc(0x0042, size)
            if h_data:
                ptr = _clip_kernel32.GlobalLock(h_data)
                if ptr:
                    ctypes.memmove(ptr, data, size)
                    _clip_kernel32.GlobalUnlock(h_data)
                    _clip_user32.SetClipboardData(fmt, h_data)
    except Exception:
        pass
    finally:
        _clip_user32.CloseClipboard()


def _notify_error(title_key, msg_key):
    if _tray_app:
        _tray_app.notify(_tray_app.tr(title_key), _tray_app.tr(msg_key))


def _perform_translate():
    saved_clipboard = _save_clipboard()
    try:
        _wait_for_physical_release(0.5)
        _release_modifiers()
        time.sleep(0.05)
        pyperclip.copy("")
        keyboard.send('ctrl+c')
        if not _clipboard_wait(3.0):
            return
        try:
            text = pyperclip.paste()
        except Exception:
            _notify_error("notify_clipboard_error_title", "notify_clipboard_error_msg")
            return
        if not text or not text.strip():
            return
        translated = translator.translate(text, config["target_language"])
        if not translated:
            _notify_error("notify_translate_error_title", "notify_translate_error_msg")
            return
        pyperclip.copy(translated)
        if config.get("auto_paste", True):
            time.sleep(0.05)
            keyboard.send('ctrl+v')
            time.sleep(0.25)
        if config.get("show_notifications", True) and _tray_app:
            _tray_app.notify(
                _tray_app.tr("notify_translated_title"),
                _tray_app.tr("notify_translated_msg"),
            )
    finally:
        _release_modifiers()
        if config.get("auto_paste", True):
            _restore_clipboard(saved_clipboard)


def _dispatch_hotkey():
    global _busy
    if not config.get("enabled", True):
        return
    with _busy_lock:
        if _busy:
            return
        _busy = True
    try:
        _perform_translate()
    except Exception:
        _notify_error("notify_translate_error_title", "notify_translate_error_msg")
    finally:
        _busy = False


def _on_hotkey():
    threading.Thread(target=_dispatch_hotkey, daemon=True).start()


def _start_hotkey():
    try:
        keyboard.add_hotkey('ctrl+shift+x', _on_hotkey, suppress=True, trigger_on_release=True)
    except Exception:
        _notify_error("notify_hotkey_error_title", "notify_hotkey_error_msg")


def _stop_hotkey():
    try:
        keyboard.unhook_all()
    except Exception:
        pass


def on_toggle_enabled(new_state):
    config["enabled"] = new_state
    save_config()


def on_toggle_startup(new_state):
    if set_startup(new_state):
        config["start_with_windows"] = new_state
        save_config()
    else:
        config["start_with_windows"] = not new_state
        save_config()
        if _tray_app:
            _tray_app.notify(
                _tray_app.tr("notify_startup_error_title"),
                _tray_app.tr("notify_startup_error_msg"),
            )


def on_toggle_notifications(new_state):
    config["show_notifications"] = new_state
    save_config()


def on_menu_language_change(new_lang):
    config["menu_language"] = new_lang
    save_config()


def on_target_language_change(new_lang):
    config["target_language"] = new_lang
    save_config()


def on_auto_paste_change(new_state):
    config["auto_paste"] = new_state
    save_config()


def _acquire_single_instance_lock():
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CreateMutexW(None, False, "ClipTranslate_SingleInstance")
    ERROR_ALREADY_EXISTS = 183
    return ctypes.get_last_error() != ERROR_ALREADY_EXISTS


def main():
    global config, _tray_app

    if not _acquire_single_instance_lock():
        return

    load_config()

    _cleanup_old_startup_shortcut()

    actual_startup = is_startup_enabled()
    if config["start_with_windows"] != actual_startup:
        set_startup(config["start_with_windows"])

    _tray_app = tray.Tray(
        ICON_PATH,
        config,
        config["menu_language"],
        on_toggle_enabled,
        on_toggle_startup,
        on_toggle_notifications,
        on_menu_language_change,
        on_target_language_change,
        on_auto_paste_change,
    )

    _start_hotkey()

    if config_was_reset:
        _notify_error("notify_config_error_title", "notify_config_error_msg")

    _tray_app.run()

    _stop_hotkey()


if __name__ == "__main__":
    main()
