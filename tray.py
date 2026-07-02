import pystray
from PIL import Image


class Tray:
    def __init__(self, icon_path, state, on_toggle_enabled, on_toggle_startup, on_toggle_notifications):
        self.state = state
        self.on_toggle_enabled = on_toggle_enabled
        self.on_toggle_startup = on_toggle_startup
        self.on_toggle_notifications = on_toggle_notifications

        image = Image.open(icon_path)
        self.icon = pystray.Icon("ClipTranslate", image, "ClipTranslate", menu=self._menu())

    def _menu(self):
        return pystray.Menu(
            pystray.MenuItem(
                "Aktif",
                self._toggle_enabled,
                checked=lambda item: self.state["enabled"],
            ),
            pystray.MenuItem(
                "Windows ile Başlat",
                self._toggle_startup,
                checked=lambda item: self.state["start_with_windows"],
            ),
            pystray.MenuItem(
                "Bildirimleri Göster",
                self._toggle_notifications,
                checked=lambda item: self.state["show_notifications"],
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Hakkında", self._about_menu()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Çıkış", self._exit),
        )

    def _about_menu(self):
        return pystray.Menu(
            pystray.MenuItem("ClipTranslate", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Version 1.0.0", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Oluşturan", None, enabled=False),
            pystray.MenuItem("RypekGrief", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Powered by Google Translate", None, enabled=False),
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
