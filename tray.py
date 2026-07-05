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
        "notify_startup_error_title": "Error",
        "notify_startup_error_msg": "Failed to update Windows startup setting.",
        "auto_paste": "Auto Paste",
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
        "notify_startup_error_title": "Hata",
        "notify_startup_error_msg": "Windows başlangıç ayarı güncellenemedi.",
        "auto_paste": "Otomatik Yapıştırma",
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
        "notify_startup_error_title": "Error",
        "notify_startup_error_msg": "No se pudo actualizar la configuración de inicio de Windows.",
        "auto_paste": "Pegado Automático",
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
        "notify_startup_error_title": "Erreur",
        "notify_startup_error_msg": "Échec de la mise à jour du démarrage Windows.",
        "auto_paste": "Collage Automatique",
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
        "notify_startup_error_title": "Fehler",
        "notify_startup_error_msg": "Windows-Starteinstellung konnte nicht aktualisiert werden.",
        "auto_paste": "Automatisches Einfügen",
    },
    "ru": {
        "active": "Активно",
        "start_with_windows": "Запускать с Windows",
        "show_notifications": "Показывать уведомления",
        "language": "Язык",
        "menu_language": "Язык меню",
        "target_language": "Язык перевода",
        "about": "О программе",
        "exit": "Выход",
        "title": "ClipTranslate",
        "version": "Версия 1.2.0",
        "creator": "Создатель",
        "creator_name": "RypekGrief",
        "powered_by": "Powered by Google Translate",
        "notify_translated_title": "ClipTranslate",
        "notify_translated_msg": "Текст переведён и скопирован в буфер обмена.",
        "notify_no_ahk_title": "ClipTranslate",
        "notify_no_ahk_msg": "AutoHotkey не найден! Пожалуйста, установите его.",
        "notify_startup_error_title": "Ошибка",
        "notify_startup_error_msg": "Не удалось обновить настройку автозапуска Windows.",
        "auto_paste": "Автовставка",
    },
    "it": {
        "active": "Attivo",
        "start_with_windows": "Avvia con Windows",
        "show_notifications": "Mostra notifiche",
        "language": "Lingua",
        "menu_language": "Lingua del menu",
        "target_language": "Lingua di destinazione",
        "about": "Informazioni",
        "exit": "Esci",
        "title": "ClipTranslate",
        "version": "Versione 1.2.0",
        "creator": "Creato da",
        "creator_name": "RypekGrief",
        "powered_by": "Powered by Google Translate",
        "notify_translated_title": "ClipTranslate",
        "notify_translated_msg": "Testo tradotto e copiato negli appunti.",
        "notify_no_ahk_title": "ClipTranslate",
        "notify_no_ahk_msg": "AutoHotkey non trovato! Installalo.",
        "notify_startup_error_title": "Errore",
        "notify_startup_error_msg": "Impossibile aggiornare l'impostazione di avvio di Windows.",
        "auto_paste": "Incolla automatico",
    },
    "pl": {
        "active": "Aktywny",
        "start_with_windows": "Uruchom z Windows",
        "show_notifications": "Pokaż powiadomienia",
        "language": "Język",
        "menu_language": "Język menu",
        "target_language": "Język docelowy",
        "about": "O programie",
        "exit": "Wyjście",
        "title": "ClipTranslate",
        "version": "Wersja 1.2.0",
        "creator": "Stworzone przez",
        "creator_name": "RypekGrief",
        "powered_by": "Powered by Google Translate",
        "notify_translated_title": "ClipTranslate",
        "notify_translated_msg": "Tekst przetłumaczony i skopiowany do schowka.",
        "notify_no_ahk_title": "ClipTranslate",
        "notify_no_ahk_msg": "Nie znaleziono AutoHotkey! Zainstaluj go.",
        "notify_startup_error_title": "Błąd",
        "notify_startup_error_msg": "Nie udało się zaktualizować ustawienia uruchamiania Windows.",
        "auto_paste": "Automatyczne wklejanie",
    },
    "ro": {
        "active": "Activ",
        "start_with_windows": "Pornește cu Windows",
        "show_notifications": "Arată notificări",
        "language": "Limbă",
        "menu_language": "Limba meniului",
        "target_language": "Limba țintă",
        "about": "Despre",
        "exit": "Ieșire",
        "title": "ClipTranslate",
        "version": "Versiunea 1.2.0",
        "creator": "Creat de",
        "creator_name": "RypekGrief",
        "powered_by": "Powered by Google Translate",
        "notify_translated_title": "ClipTranslate",
        "notify_translated_msg": "Text tradus și copiat în clipboard.",
        "notify_no_ahk_title": "ClipTranslate",
        "notify_no_ahk_msg": "AutoHotkey nu a fost găsit! Instalați-l.",
        "notify_startup_error_title": "Eroare",
        "notify_startup_error_msg": "Actualizarea setării de pornire Windows a eșuat.",
        "auto_paste": "Lipire automată",
    },
    "uk": {
        "active": "Активно",
        "start_with_windows": "Запускати з Windows",
        "show_notifications": "Показувати сповіщення",
        "language": "Мова",
        "menu_language": "Мова меню",
        "target_language": "Мова перекладу",
        "about": "Про програму",
        "exit": "Вихід",
        "title": "ClipTranslate",
        "version": "Версія 1.2.0",
        "creator": "Створено",
        "creator_name": "RypekGrief",
        "powered_by": "Powered by Google Translate",
        "notify_translated_title": "ClipTranslate",
        "notify_translated_msg": "Текст перекладено та скопійовано в буфер обміну.",
        "notify_no_ahk_title": "ClipTranslate",
        "notify_no_ahk_msg": "AutoHotkey не знайдено! Будь ласка, встановіть його.",
        "notify_startup_error_title": "Помилка",
        "notify_startup_error_msg": "Не вдалося оновити налаштування автозапуску Windows.",
        "auto_paste": "Автовставка",
    },
}

TRANSLATED_LANGUAGE_NAMES = {
    "en": {"en": "English", "tr": "Turkish", "es": "Spanish", "fr": "French", "de": "German", "ru": "Russian", "it": "Italian", "pl": "Polish", "ro": "Romanian", "uk": "Ukrainian"},
    "tr": {"en": "İngilizce", "tr": "Türkçe", "es": "İspanyolca", "fr": "Fransızca", "de": "Almanca", "ru": "Rusça", "it": "İtalyanca", "pl": "Lehçe", "ro": "Romence", "uk": "Ukraynaca"},
    "es": {"en": "Inglés", "tr": "Turco", "es": "Español", "fr": "Francés", "de": "Alemán", "ru": "Ruso", "it": "Italiano", "pl": "Polaco", "ro": "Rumano", "uk": "Ucraniano"},
    "fr": {"en": "Anglais", "tr": "Turc", "es": "Espagnol", "fr": "Français", "de": "Allemand", "ru": "Russe", "it": "Italien", "pl": "Polonais", "ro": "Roumain", "uk": "Ukrainien"},
    "de": {"en": "Englisch", "tr": "Türkisch", "es": "Spanisch", "fr": "Französisch", "de": "Deutsch", "ru": "Russisch", "it": "Italienisch", "pl": "Polnisch", "ro": "Rumänisch", "uk": "Ukrainisch"},
    "ru": {"en": "Английский", "tr": "Турецкий", "es": "Испанский", "fr": "Французский", "de": "Немецкий", "ru": "Русский", "it": "Итальянский", "pl": "Польский", "ro": "Румынский", "uk": "Украинский"},
    "it": {"en": "Inglese", "tr": "Turco", "es": "Spagnolo", "fr": "Francese", "de": "Tedesco", "ru": "Russo", "it": "Italiano", "pl": "Polacco", "ro": "Rumeno", "uk": "Ucraino"},
    "pl": {"en": "Angielski", "tr": "Turecki", "es": "Hiszpański", "fr": "Francuski", "de": "Niemiecki", "ru": "Rosyjski", "it": "Włoski", "pl": "Polski", "ro": "Rumuński", "uk": "Ukraiński"},
    "ro": {"en": "Engleză", "tr": "Turcă", "es": "Spaniolă", "fr": "Franceză", "de": "Germană", "ru": "Rusă", "it": "Italiană", "pl": "Poloneză", "ro": "Română", "uk": "Ucraineană"},
    "uk": {"en": "Англійська", "tr": "Турецька", "es": "Іспанська", "fr": "Французька", "de": "Німецька", "ru": "Російська", "it": "Італійська", "pl": "Польська", "ro": "Румунська", "uk": "Українська"},
}

NATIVE_LANGUAGE_NAMES = {
    "en": "English",
    "tr": "Türkçe",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "ru": "Русский",
    "it": "Italiano",
    "pl": "Polski",
    "ro": "Română",
    "uk": "Українська",
}

AVAILABLE_MENU_LANGUAGES = sorted(["en", "tr", "es", "fr", "de", "ru", "it", "pl", "ro", "uk"])

AVAILABLE_TARGET_LANGUAGES = sorted(["en", "tr", "es", "fr", "de", "ru", "it", "pl", "ro", "uk"])


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
