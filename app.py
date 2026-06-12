import requests
import time
import json
import sys
import os

url = os.environ.get("API_URL")

if not url:
    sys.exit(1)

new_cookie = None

for _ in range(30):
    try:
        response = requests.get(url, timeout=10).json()
        if "extracted_cookie" in response:
            new_cookie = response["extracted_cookie"]
            break
    except Exception:
        pass
    time.sleep(10)

if not new_cookie:
    sys.exit(1)

try:
    with open("apis.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        item["cookie"] = new_cookie
        if "mpd" in item:
            base_url = item["mpd"].split("?")[0]
            item["mpd"] = f"{base_url}?{new_cookie}"

    with open("apis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
except Exception:
    sys.exit(1)
