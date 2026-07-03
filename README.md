# ⚠️ Warning

This application uses **AutoHotkey** in the background to automate keyboard input. Because of this, some online games or anti-cheat systems may detect or interfere with its behavior. Please use the application at your own discretion.

---

# ClipTranslate

## Description

**ClipTranslate** is a lightweight translation application for Windows. It instantly translates selected text into **English** using the **Ctrl + Shift + X** shortcut and automatically copies the translated result to your clipboard.

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

- Instantly translates selected text into English.
- Automatically copies the translated text to the clipboard.
- Works in almost any application where text can be selected and copied, including games, web browsers, Discord, Notepad, Visual Studio Code, and more.
- Can automatically start with Windows from the system tray.
- Optional desktop notifications after each successful translation.
- Translation can be enabled or disabled directly from the system tray without closing the application.
- Lightweight and resource-efficient, typically using less than **50 MB** of RAM.

---

## Usage

1. Launch **ClipTranslate**.
2. If **AutoHotkey** is not installed, the application will notify you.
3. Type or locate any non-English text.
4. Select the text you want to translate.
5. Press **Ctrl + Shift + X**.
6. If notifications are enabled, a **"Text translated and copied to clipboard"** notification will appear.
7. Press **Ctrl + V** to paste the translated text.

Your selected text has now been translated into English and copied to the clipboard.
