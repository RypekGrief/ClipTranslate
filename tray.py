import pystray
from PIL import Image
from languages import (
    STRINGS,
    TRANSLATED_LANGUAGE_NAMES,
    NATIVE_LANGUAGE_NAMES,
    AVAILABLE_MENU_LANGUAGES,
    AVAILABLE_TARGET_LANGUAGES,
)


class Tray:
    def __init__(self, icon_path, state, menu_language, on_toggle_enabled, on_toggle_startup, on_toggle_notifications, on_menu_language_change, on_target_language_change, on_auto_paste_change):
        self.state = state
        self.menu_language = menu_language
        self.on_toggle_enabled = on_toggle_enabled
        self.on_toggle_startup = on_toggle_startup
        self.on_toggle_notifications = on_toggle_notifications
        self.on_menu_language_change = on_menu_language_change
        self.on_target_language_change = on_target_language_change
        self.on_auto_paste_change = on_auto_paste_change

        image = Image.open(icon_path)
        self.icon = pystray.Icon("ClipTranslate", image, "ClipTranslate", menu=self._menu())

    def _s(self, key):
        return STRINGS.get(self.menu_language, STRINGS["en"]).get(key, key)

    def tr(self, key):
        return self._s(key)

    def _lang_name(self, lang_code):
        return TRANSLATED_LANGUAGE_NAMES.get(self.menu_language, TRANSLATED_LANGUAGE_NAMES["en"]).get(lang_code, lang_code)

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
            pystray.MenuItem(
                s("auto_paste"),
                self._toggle_auto_paste,
                checked=lambda item: self.state.get("auto_paste", True),
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
            pystray.MenuItem(s("menu_language"), self._menu_language_submenu()),
            pystray.MenuItem(s("target_language"), self._target_language_submenu()),
        )

    def _menu_language_submenu(self):
        items = []
        for lang in AVAILABLE_MENU_LANGUAGES:
            checked = (lang == self.menu_language)
            items.append(
                pystray.MenuItem(
                    NATIVE_LANGUAGE_NAMES[lang],
                    self._make_set_menu_language(lang),
                    checked=lambda item, l=lang: l == self.menu_language,
                    radio=True,
                )
            )
        return pystray.Menu(*items)

    def _make_set_menu_language(self, lang_code):
        def handler(icon, item):
            self._set_menu_language(lang_code)
        return handler

    def _set_menu_language(self, lang_code):
        self.menu_language = lang_code
        self.icon.menu = self._menu()
        self.on_menu_language_change(lang_code)

    def _target_language_submenu(self):
        items = []
        for lang in AVAILABLE_TARGET_LANGUAGES:
            items.append(
                pystray.MenuItem(
                    self._lang_name(lang),
                    self._make_set_target_language(lang),
                    checked=lambda item, l=lang: l == self.state["target_language"],
                    radio=True,
                )
            )
        return pystray.Menu(*items)

    def _make_set_target_language(self, lang_code):
        def handler(icon, item):
            self._set_target_language(lang_code)
        return handler

    def _set_target_language(self, lang_code):
        self.state["target_language"] = lang_code
        self.icon.menu = self._menu()
        self.on_target_language_change(lang_code)

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

    def _toggle_auto_paste(self, icon, item):
        self.state["auto_paste"] = not self.state.get("auto_paste", True)
        self.on_auto_paste_change(self.state["auto_paste"])

    def _exit(self, icon, item):
        self.icon.stop()

    def notify(self, title, message):
        self.icon.notify(message, title)

    def run(self):
        self.icon.run()
