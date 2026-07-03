[![Latest Release](https://img.shields.io/github/v/release/RypekGrief/ClipTranslate)](https://github.com/RypekGrief/ClipTranslate/releases) ![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows) ![Python](https://img.shields.io/badge/Python-3.14+-3776AB?logo=python&logoColor=white) ![License](https://img.shields.io/github/license/RypekGrief/ClipTranslate) ![Status](https://img.shields.io/badge/Status-Active-success)
# ⚠️ Warning

This application uses **AutoHotkey** in the background to automate keyboard input. Because of this, some online games or anti-cheat systems may detect or interfere with its behavior. Please use the application at your own discretion.

---

# ClipTranslate

## Description

**ClipTranslate** is a lightweight translation application for Windows. It instantly translates selected text into your preferred language using the **Ctrl + Shift + X** shortcut, automatically copies the translated result to the clipboard, and pastes it back into the active application.

---

## Installation

### Requirements

- [Python](https://www.python.org/downloads/windows/)
- [AutoHotkey v2](https://www.autohotkey.com/)

After installing the requirements, open a Command Prompt in the project folder and run:

```bash
py -m pip install -r requirements.txt
```

---

## Features

- Instantly translates selected text into your preferred target language.
- Automatically copies and pastes the translated text back into the active application.
- Supports **5 interface languages** that can be changed from the system tray.
- Supports changing the **target translation language** directly from the system tray.
- Works in almost any application where text can be selected and copied, including games, web browsers, Discord, Notepad, Visual Studio Code, and more.
- Can automatically start with Windows.
- Optional desktop notifications after each successful translation.
- Translation can be enabled or disabled directly from the system tray without closing the application.
- Lightweight and resource-efficient, typically using less than **50 MB** of RAM.

---

## Usage

1. Launch **ClipTranslate**.
2. If **AutoHotkey** is not installed, the application will notify you.
3. Type or locate any text that you want to translate.
4. Select the text.
5. Press **Ctrl + Shift + X**.
6. ClipTranslate will automatically:
   - Copy the selected text.
   - Translate it into the selected target language.
   - Copy the translated text to the clipboard.
   - Paste it back into the active application.
7. If notifications are enabled, a **"Text translated and copied to clipboard"** notification will appear.

The selected text will be replaced with its translated version automatically.
