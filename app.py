import requests
import time
import json
import sys
import os
import base64

def hex_to_base64url(hex_string):
    try:
        return base64.urlsafe_b64encode(bytes.fromhex(hex_string)).decode('utf-8').rstrip('=')
    except Exception:
        return ""

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

    ott_nav_content = '#EXTM3U x-tvg-url=""\n\n'
    ns_player_data = []

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

        target_kid_hex = ""
        target_k_hex = ""
        if keys:
            key_list = list(keys.items())
            target_index = 2 if len(key_list) >= 3 else 0
            target_kid_hex, target_k_hex = key_list[target_index]

        ns_item = {
            "name": name,
            "logo": logo,
            "title": name,
            "drmlicense": f"{target_kid_hex}:{target_k_hex}" if target_kid_hex else "",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0",
            "referer": "https://jiotv.com/",
            "cookie": new_cookie,
            "link": mpd
        }
        ns_player_data.append(ns_item)

        ott_nav_content += f'#EXTINF:-1 tvg-id="{ch_id}" tvg-logo="{logo}" group-title="{group}",{name}\n'
        ott_nav_content += '#KODIPROP:inputstream=inputstream.adaptive\n'
        ott_nav_content += '#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey\n'
        
        if target_kid_hex and target_k_hex:
            kid_b64 = hex_to_base64url(target_kid_hex)
            k_b64 = hex_to_base64url(target_k_hex)
            if kid_b64 and k_b64:
                license_key_dict = {
                    "keys": [{"kty": "oct", "kid": kid_b64, "k": k_b64}],
                    "type": "temporary"
                }
                license_key_json = json.dumps(license_key_dict, separators=(',', ':'))
                ott_nav_content += f'#KODIPROP:inputstream.adaptive.license_key={license_key_json}\n'

        ott_nav_content += '#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0\n'
        ott_nav_content += '#EXTVLCOPT:http-origin=https://jiotv.com\n'
        ott_nav_content += '#EXTVLCOPT:http-referrer=https://jiotv.com/\n'
        ott_nav_content += f'#EXTVLCOPT:http-cookie={new_cookie}\n'
        
        ott_nav_content += f'{mpd}\n\n'

    with open("apis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    with open("ns_player.m3u", "w", encoding="utf-8") as f:
        json.dump(ns_player_data, f, indent=4)

    with open("ott_nav_player.m3u", "w", encoding="utf-8") as f:
        f.write(ott_nav_content)

except Exception:
    sys.exit(1)
