import json
import os
import sys
import time
import ctypes
import threading
import subprocess
import winreg
import pyperclip

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
_ahk_process = None
_last_seq = 0
_ipc_ready = threading.Event()
_stop_event = threading.Event()

TRIGGER_FILE = os.path.join(
    os.environ.get("TEMP", os.environ.get("TMP", ".")),
    "ClipTranslate.trigger",
)

DONE_FILE = os.path.join(
    os.environ.get("TEMP", os.environ.get("TMP", ".")),
    "ClipTranslate.done",
)


def _exe_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _resource_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(_exe_dir(), "config.json")
ICON_PATH = os.path.join(_resource_dir(), "icon.ico")
AHK_SCRIPT = os.path.join(_resource_dir(), "translate.ahk")


def load_config():
    global config
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

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


def _find_autohotkey():
    import shutil

    exe_names = [
        "AutoHotkeyU64.exe", "AutoHotkey64.exe",
        "AutoHotkeyU32.exe", "AutoHotkey.exe",
        "AutoHotkeyA32.exe", "AutoHotkey32.exe",
    ]

    for name in exe_names:
        ahk = shutil.which(name)
        if ahk:
            return ahk

    base_dirs = [
        os.environ.get("ProgramFiles", "C:\\Program Files"),
        os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
    ]

    for base in base_dirs:
        ahk_dir = os.path.join(base, "AutoHotkey")
        if not os.path.isdir(ahk_dir):
            continue
        for root, _dirs, files in os.walk(ahk_dir):
            for name in exe_names:
                if name in files:
                    return os.path.join(root, name)

    return None


def _start_ahk():
    global _ahk_process

    ahk_exe = _find_autohotkey()
    if not ahk_exe:
        return False

    try:
        _ahk_process = subprocess.Popen(
            [ahk_exe, AHK_SCRIPT],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def _stop_ahk():
    global _ahk_process
    if _ahk_process:
        try:
            _ahk_process.terminate()
            _ahk_process.wait(timeout=2)
        except Exception:
            try:
                _ahk_process.kill()
            except Exception:
                pass
        _ahk_process = None


def _handle_translate():
    global _last_seq

    try:
        if not config.get("enabled", True):
            return

        user32 = ctypes.windll.user32
        curr = user32.GetClipboardSequenceNumber()
        if curr == _last_seq:
            return

        try:
            text = pyperclip.paste()
        except Exception:
            return

        if not text or not text.strip():
            return

        _last_seq = curr

        translated = translator.translate(text, config["target_language"])

        if translated:
            pyperclip.copy(translated)
            _last_seq = user32.GetClipboardSequenceNumber()
            if config.get("auto_paste", True):
                try:
                    open(DONE_FILE, "w").close()
                except OSError:
                    pass
            if config.get("show_notifications", True) and _tray_app:
                _tray_app.notify(
                    _tray_app.tr("notify_translated_title"),
                    _tray_app.tr("notify_translated_msg"),
                )
    except Exception:
        pass


def _ipc_thread():
    _ipc_ready.set()

    while not _stop_event.is_set():
        if os.path.isfile(TRIGGER_FILE):
            try:
                os.remove(TRIGGER_FILE)
            except OSError:
                pass
            _handle_translate()
        time.sleep(0.1)


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


def main():
    global config, _tray_app

    load_config()

    _cleanup_old_startup_shortcut()

    actual_startup = is_startup_enabled()
    if config["start_with_windows"] != actual_startup:
        set_startup(config["start_with_windows"])

    threading.Thread(target=_ipc_thread, daemon=True).start()
    _ipc_ready.wait(timeout=5.0)

    ahk_ok = _start_ahk()

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

    if not ahk_ok:
        threading.Timer(1.0, lambda: _tray_app.notify(
            _tray_app.tr("notify_no_ahk_title"),
            _tray_app.tr("notify_no_ahk_msg"),
        )).start()

    _tray_app.run()

    _stop_event.set()
    _stop_ahk()


if __name__ == "__main__":
    main()
