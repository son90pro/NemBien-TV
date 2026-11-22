import json
import urllib.request
from datetime import datetime, timezone, timedelta

SCHEDULE_URL = "https://nembientv.com/cms-schedule.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Encoding": "identity",
    "Referer": "https://nembientv.com/",
}

try:
    req = urllib.request.Request(SCHEDULE_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    category_order = {
        "Bóng Đá": 1,
        "Bóng Chuyền": 2,
        "Bóng Rổ": 3,
        "Bia": 4,
        "Esports": 5,
        "Thể Thao Khác": 6,
    }

    matches_by_category = {cat: [] for cat in category_order.keys()}

    tz_vn = timezone(timedelta(hours=7))
    now_vn = datetime.now(tz_vn)
    today_date = now_vn.date()
    tomorrow_date = today_date + timedelta(days=1)

    for match in data.get("response", []):
        match_id = match.get("matchId")
        sport_raw = match.get("sport", "").lower()
        home = match.get("home", "Home")
        away = match.get("away", "Away")
        timestamp = match.get("timestamp", 0)

        if not match_id or not timestamp:
            continue

        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone(tz_vn)
        match_date = dt.date()

        if match_date != today_date and match_date != tomorrow_date:
            continue

        stream_url = ""
        try:
            detail_url = f"https://nembientv.com/truc-tiep/{match_id}?kd_source=1"
            detail_req = urllib.request.Request(detail_url, headers=HEADERS)
            with urllib.request.urlopen(detail_req, timeout=6) as detail_res:
                detail_data = json.loads(detail_res.read().decode("utf-8"))
                stream_url = detail_data.get("streamUrl", "")
        except Exception:
            stream_url = ""

        if not stream_url:
            stream_url = f"https://nembientv.com/live/{match_id}/index.m3u8"

        time_str = dt.strftime("%H:%M %d/%m")

        if "football" in sport_raw or "soccer" in sport_raw:
            category = "Bóng Đá"
        elif "volleyball" in sport_raw:
            category = "Bóng Chuyền"
        elif "basketball" in sport_raw:
            category = "Bóng Rổ"
        elif any(k in sport_raw for k in ["snooker", "billiards", "pool", "bia"]):
            category = "Bia"
        elif any(k in sport_raw for k in ["esports", "dota", "csgo", "lol"]):
            category = "Esports"
        else:
            category = "Bóng Đá"

        commentators = match.get("commentators", [])
        blv_name = commentators[0]["name"] if commentators else "Live"
        logo = match.get("homeLogo", "")
        title = f"{time_str} {home} vs {away} [{blv_name}]"

        matches_by_category[category].append({
            "id": match_id,
            "title": title,
            "logo": logo,
            "group": category,
            "url": stream_url,
            "timestamp": timestamp,
        })

    m3u_content = '#EXTM3U x-tvg-url=""\n'
    sorted_categories = sorted(
        matches_by_category.keys(), key=lambda x: category_order.get(x, 99)
    )

    for cat in sorted_categories:
        match_list = matches_by_category[cat]
        match_list.sort(key=lambda x: x["timestamp"])
        for m in match_list:
            m3u_content += (
                f'#EXTINF:-1 tvg-id="{m["id"]}" tvg-name="{m["title"]}" '
                f'tvg-logo="{m["logo"]}" group-title="{m["group"]}",{m["title"]}\n'
            )
            m3u_content += f'{m["url"]}\n'

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print("Cập nhật playlist.m3u thành công!")

except Exception as e:
    print(f"Lỗi hệ thống: {e}")
