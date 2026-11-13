import json
import urllib.request
from datetime import datetime, timezone, timedelta

# URL API lịch thi đấu từ Ném Biên TV
url = "https://nembientv.com/cms-schedule.json"

try:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))

    # Định nghĩa thứ tự ưu tiên các nhóm môn thể thao (Bóng đá đứng đầu)
    category_order = {
        "Bóng Đá": 1,
        "Bóng Chuyền": 2,
        "Bóng Rổ": 3,
        "Bia": 4,
        "Esports": 5,
        "Thể Thao Khác": 6
    }

    matches_by_category = {cat: [] for cat in category_order.keys()}

    # Múi giờ Việt Nam (UTC+7)
    tz_vn = timezone(timedelta(hours=7))

    for match in data.get("response", []):
        match_id = match.get("matchId")
        sport_raw = match.get("sport", "").lower()
        league = match.get("league", "Giải Đấu")
        home = match.get("home", "Home")
        away = match.get("away", "Away")
        timestamp = match.get("timestamp", 0)

        # Chuyển đổi timestamp sang múi giờ Việt Nam (GMT+7)
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone(tz_vn)
        time_str = dt.strftime("%H:%M %d/%m")

        # Phân loại danh mục theo yêu cầu
        if "football" in sport_raw or "soccer" in sport_raw:
            category = "Bóng Đá"
        elif "volleyball" in sport_raw:
            category = "Bóng Chuyền"
        elif "basketball" in sport_raw:
            category = "Bóng Rổ"
        elif "snooker" in sport_raw or "billiards" in sport_raw or "pool" in sport_raw or "bia" in sport_raw:
            category = "Bia"
        elif "esports" in sport_raw or "dota" in sport_raw or "csgo" in sport_raw or "league" in sport_raw and "lol" in sport_raw:
            category = "Esports"
        else:
            category = "Bóng Đá"  # Mặc định ưu tiên đưa vào bóng đá nếu không khớp rõ ràng

        # Lấy tên BLV
        commentators = match.get("commentators", [])
        blv_name = commentators[0]["name"] if commentators else "Live"

        # Lấy logo đội nhà
        logo = match.get("homeLogo", "")

        # Tiêu đề hiển thị: Giờ Ngày | Đội nhà vs Đội khách [Tên BLV]
        title = f"{time_str} {home} vs {away} [{blv_name}]"

        # Link luồng phát
        stream_url = f"https://nembientv.com/live/{match_id}/index.m3u8"

        match_item = {
            "id": match_id,
            "title": title,
            "logo": logo,
            "group": category,  # Chỉ lấy tên nhóm gọn gàng (Bóng Đá, Bóng Chuyền...)
            "url": stream_url,
            "timestamp": timestamp
        }
        matches_by_category[category].append(match_item)

    # Bắt đầu tạo nội dung file M3U
    m3u_content = '#EXTM3U x-tvg-url=""\n'

    # Sắp xếp các danh mục theo đúng thứ tự yêu cầu
    sorted_categories = sorted(matches_by_category.keys(), key=lambda x: category_order.get(x, 99))

    for cat in sorted_categories:
        match_list = matches_by_category[cat]
        # Sắp xếp trận đấu theo thời gian sớm đến muộn trong từng danh mục
        match_list.sort(key=lambda x: x["timestamp"])
        
        for m in match_list:
            m3u_content += f'#EXTINF:-1 tvg-id="{m["id"]}" tvg-name="{m["title"]}" tvg-logo="{m["logo"]}" group-title="{m["group"]}",{m["title"]}\n'
            m3u_content += f'{m["url"]}\n'

    # Ghi ra file playlist.m3u
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print("Đã cập nhật tên nhóm gọn gàng thành công!")

except Exception as e:
    print(f"Lỗi: {e}")
    
