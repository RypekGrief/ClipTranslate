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
        "notify_translated_title": "ClipTranslate",
        "notify_translated_msg": "Text translated and copied to clipboard.",
        "notify_no_ahk_title": "ClipTranslate",
        "notify_no_ahk_msg": "AutoHotkey not found! Please install it.",
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
        "notify_translated_title": "ClipTranslate",
        "notify_translated_msg": "Metin çevrildi ve panoya kopyalandı.",
        "notify_no_ahk_title": "ClipTranslate",
        "notify_no_ahk_msg": "AutoHotkey bulunamadı! Lütfen kurun.",
    },
    "es": {
        "active": "Activo",
        "start_with_windows": "Iniciar con Windows",
        "show_notifications": "Mostrar Notificaciones",
        "language": "Idioma",
        "menu_language": "Idioma del Menú",
        "target_language": "Idioma de Destino",
        "about": "Acerca de",
        "exit": "Salir",
        "title": "ClipTranslate",
        "version": "Versión 1.1.0",
        "creator": "Creado por",
        "creator_name": "RypekGrief",
        "powered_by": "Desarrollado por Google Translate",
        "notify_translated_title": "ClipTranslate",
        "notify_translated_msg": "Texto traducido y copiado al portapapeles.",
        "notify_no_ahk_title": "ClipTranslate",
        "notify_no_ahk_msg": "¡AutoHotkey no encontrado! Por favor, instálelo.",
    },
    "fr": {
        "active": "Actif",
        "start_with_windows": "Démarrer avec Windows",
        "show_notifications": "Afficher les Notifications",
        "language": "Langue",
        "menu_language": "Langue du Menu",
        "target_language": "Langue Cible",
        "about": "À propos",
        "exit": "Quitter",
        "title": "ClipTranslate",
        "version": "Version 1.1.0",
        "creator": "Créé par",
        "creator_name": "RypekGrief",
        "powered_by": "Propulsé par Google Translate",
        "notify_translated_title": "ClipTranslate",
        "notify_translated_msg": "Texte traduit et copié dans le presse-papiers.",
        "notify_no_ahk_title": "ClipTranslate",
        "notify_no_ahk_msg": "AutoHotkey introuvable ! Veuillez l'installer.",
    },
    "de": {
        "active": "Aktiv",
        "start_with_windows": "Mit Windows starten",
        "show_notifications": "Benachrichtigungen anzeigen",
        "language": "Sprache",
        "menu_language": "Menüsprache",
        "target_language": "Zielsprache",
        "about": "Über",
        "exit": "Beenden",
        "title": "ClipTranslate",
        "version": "Version 1.1.0",
        "creator": "Erstellt von",
        "creator_name": "RypekGrief",
        "powered_by": "Powered by Google Translate",
        "notify_translated_title": "ClipTranslate",
        "notify_translated_msg": "Text übersetzt und in die Zwischenablage kopiert.",
        "notify_no_ahk_title": "ClipTranslate",
        "notify_no_ahk_msg": "AutoHotkey nicht gefunden! Bitte installieren.",
    },
}

LANGUAGE_NAMES = {
    "en": "English",
    "tr": "Türkçe",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
}

AVAILABLE_MENU_LANGUAGES = ["en", "tr", "es", "fr", "de"]


class Tray:
    def __init__(self, icon_path, state, menu_language, on_toggle_enabled, on_toggle_startup, on_toggle_notifications, on_menu_language_change):
        self.state = state
        self.menu_language = menu_language
        self.on_toggle_enabled = on_toggle_enabled
        self.on_toggle_startup = on_toggle_startup
        self.on_toggle_notifications = on_toggle_notifications
        self.on_menu_language_change = on_menu_language_change

        image = Image.open(icon_path)
        self.icon = pystray.Icon("ClipTranslate", image, "ClipTranslate", menu=self._menu())

    def _s(self, key):
        return STRINGS.get(self.menu_language, STRINGS["en"]).get(key, key)

    def tr(self, key):
        return self._s(key)

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
            pystray.MenuItem(s("menu_language"), self._menu_language_submenu()),
            pystray.MenuItem(s("target_language"), None, enabled=False),
        )

    def _menu_language_submenu(self):
        items = []
        for lang in AVAILABLE_MENU_LANGUAGES:
            checked = (lang == self.menu_language)
            items.append(
                pystray.MenuItem(
                    LANGUAGE_NAMES[lang],
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
