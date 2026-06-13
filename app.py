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

    m3u_content = '#EXTM3U x-tvg-url=""\n\n'

    for item in data:
        item["cookie"] = new_cookie
        
        if "mpd" in item:
            base_url = item["mpd"].split("?")[0]
            item["mpd"] = f"{base_url}?{new_cookie}"

        name = item.get("name", "")
        ch_id = item.get("id", "")
        logo = item.get("logo", "")
        group = item.get("group", "")
        mpd = item.get("mpd", "")
        keys = item.get("keys", {})

        m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}" tvg-logo="{logo}" group-title="{group}",{name}\n'
        m3u_content += '#KODIPROP:inputstream=inputstream.adaptive\n'
        m3u_content += '#KODIPROP:inputstream.adaptive.manifest_type=mpd\n'
        m3u_content += '#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
        
        if keys:
            key_list = list(keys.items())
            target_index = 2 if len(key_list) >= 3 else 0
            kid_hex, k_hex = key_list[target_index]
            
            m3u_content += f'#KODIPROP:inputstream.adaptive.license_key={kid_hex}:{k_hex}\n'

        m3u_content += '#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0\n'
        m3u_content += '#EXTVLCOPT:http-origin=https://jiotv.com\n'
        m3u_content += '#EXTVLCOPT:http-referrer=https://jiotv.com/\n'
        
        m3u_content += f'{mpd}\n\n'

    with open("apis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

except Exception:
    sys.exit(1)
