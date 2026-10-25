import urllib.request
import urllib.parse
import json
import time

_TIMEOUT = 5
_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def _try_gtx(text, target_language):
    url = 'https://translate.googleapis.com/translate_a/single'
    params = urllib.parse.urlencode({
        'client': 'gtx',
        'sl': 'auto',
        'tl': target_language,
        'dt': 't',
        'q': text,
    })
    req = urllib.request.Request(
        f'{url}?{params}',
        headers={'User-Agent': _USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    return ''.join(item[0] for item in result[0])


def _try_dict_chrome_ex(text, target_language):
    url = 'https://clients5.google.com/translate_a/t'
    params = urllib.parse.urlencode({
        'client': 'dict-chrome-ex',
        'sl': 'auto',
        'tl': target_language,
        'q': text,
    })
    req = urllib.request.Request(
        f'{url}?{params}',
        headers={'User-Agent': _USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    return result[0][0]


def translate(text, target_language="en"):
    for attempt in range(3):
        try:
            return _try_gtx(text, target_language)
        except Exception:
            if attempt < 2:
                time.sleep(1.0 * (attempt + 1))
    try:
        return _try_dict_chrome_ex(text, target_language)
    except Exception:
        return None
