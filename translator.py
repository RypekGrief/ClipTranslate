import urllib.request
import urllib.parse
import json
import time


def translate(text, target_language="en"):
    data = urllib.parse.urlencode({
        "client": "gtx",
        "sl": "auto",
        "tl": target_language,
        "dt": "t",
        "q": text,
    }).encode()
    url = "https://translate.googleapis.com/translate_a/single"
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return "".join(item[0] for item in result[0])
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(1.0 * (attempt + 1))
                continue
            return None
        except Exception:
            return None
    return None
