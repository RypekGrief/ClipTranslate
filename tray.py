import pystray
from PIL import Image

STRINGS = {
    "en": {
        "active": "Active",
        "start_with_windows": "Start with Windows",
        "show_notifications": "Show Notifications",
        "language": "Language",
        "menu_language": "Menu Language",
        "target_language": "Target Language",
        "about": "About",
        "exit": "Exit",
        "title": "ClipTranslate",
        "version": "Version 1.1.0",
        "creator": "Created by",
        "creator_name": "RypekGrief",
        "powered_by": "Powered by Google Translate",
    },
    "tr": {
        "active": "Aktif",
        "start_with_windows": "Windows ile Başlat",
        "show_notifications": "Bildirimleri Göster",
        "language": "Dil",
        "menu_language": "Menü Dili",
        "target_language": "Çevrilen Dil",
        "about": "Hakkında",
        "exit": "Çıkış",
        "title": "ClipTranslate",
        "version": "Sürüm 1.1.0",
        "creator": "Oluşturan",
        "creator_name": "RypekGrief",
        "powered_by": "Powered by Google Translate",
    },
}


class Tray:
    def __init__(self, icon_path, state, menu_language, on_toggle_enabled, on_toggle_startup, on_toggle_notifications):
        self.state = state
        self.menu_language = menu_language
        self.on_toggle_enabled = on_toggle_enabled
        self.on_toggle_startup = on_toggle_startup
        self.on_toggle_notifications = on_toggle_notifications

        image = Image.open(icon_path)
        self.icon = pystray.Icon("ClipTranslate", image, "ClipTranslate", menu=self._menu())

    def _s(self, key):
        return STRINGS.get(self.menu_language, STRINGS["en"]).get(key, key)

    def _menu(self):
        s = self._s
        return pystray.Menu(
            pystray.MenuItem(
                s("active"),
                self._toggle_enabled,
                checked=lambda item: self.state["enabled"],
            ),
            pystray.MenuItem(
                s("start_with_windows"),
                self._toggle_startup,
                checked=lambda item: self.state["start_with_windows"],
            ),
            pystray.MenuItem(
                s("show_notifications"),
                self._toggle_notifications,
                checked=lambda item: self.state["show_notifications"],
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(s("language"), self._language_menu()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(s("about"), self._about_menu()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(s("exit"), self._exit),
        )

    def _language_menu(self):
        s = self._s
        return pystray.Menu(
            pystray.MenuItem(s("menu_language"), None, enabled=False),
            pystray.MenuItem(s("target_language"), None, enabled=False),
        )

    def _about_menu(self):
        s = self._s
        return pystray.Menu(
            pystray.MenuItem(s("title"), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(s("version"), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(s("creator"), None, enabled=False),
            pystray.MenuItem(s("creator_name"), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(s("powered_by"), None, enabled=False),
        )

    def _toggle_enabled(self, icon, item):
        self.state["enabled"] = not self.state["enabled"]
        self.on_toggle_enabled(self.state["enabled"])

    def _toggle_startup(self, icon, item):
        self.state["start_with_windows"] = not self.state["start_with_windows"]
        self.on_toggle_startup(self.state["start_with_windows"])

    def _toggle_notifications(self, icon, item):
        self.state["show_notifications"] = not self.state["show_notifications"]
        self.on_toggle_notifications(self.state["show_notifications"])

    def _exit(self, icon, item):
        self.icon.stop()

    def notify(self, title, message):
        self.icon.notify(message, title)

    def run(self):
        self.icon.run()
