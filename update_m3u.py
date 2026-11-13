import json
import urllib.request
from datetime import datetime, timezone, timedelta

# URL API lịch thi đấu tổng
SCHEDULE_URL = "https://nembientv.com/cms-schedule.json"

try:
    req = urllib.request.Request(
        SCHEDULE_URL, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))

    # Định nghĩa thứ tự ưu tiên các nhóm môn thể thao
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

        # Chuyển đổi timestamp sang múi giờ Việt Nam (GMT+7)
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone(tz_vn)
        match_date = dt.date()

        # Chỉ lấy các trận trong ngày hôm nay và ngày hôm sau
        if match_date != today_date and match_date != tomorrow_date:
            continue

        # Cố gắng lấy link stream thực tế từ API chi tiết
        stream_url = ""
        try:
            detail_url = f"https://nembientv.com/truc-tiep/{match_id}?kd_source=1"
            detail_req = urllib.request.Request(
                detail_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(detail_req, timeout=3) as detail_res:
                detail_data = json.loads(detail_res.read().decode("utf-8"))
                stream_url = detail_data.get("streamUrl", "")
        except Exception:
            stream_url = ""

        # Nếu trận chưa đá (chưa có streamUrl), dùng link dự phòng để vẫn hiển thị trên danh sách
        if not stream_url:
            stream_url = f"https://nembientv.com/live/{match_id}/index.m3u8"

        time_str = dt.strftime("%H:%M %d/%m")

        # Phân loại danh mục
        if "football" in sport_raw or "soccer" in sport_raw:
            category = "Bóng Đá"
        elif "volleyball" in sport_raw:
            category = "Bóng Chuyền"
        elif "basketball" in sport_raw:
            category = "Bóng Rổ"
        elif "snooker" in sport_raw or "billiards" in sport_raw or "pool" in sport_raw or "bia" in sport_raw:
            category = "Bia"
        elif "esports" in sport_raw or "dota" in sport_raw or "csgo" in sport_raw or "lol" in sport_raw:
            category = "Esports"
        else:
            category = "Bóng Đá"  # Mặc định đưa vào bóng đá

        # Lấy tên BLV
        commentators = match.get("commentators", [])
        blv_name = commentators[0]["name"] if commentators else "Live"

        # Lấy logo đội nhà
        logo = match.get("homeLogo", "")

        # Tiêu đề chuẩn hiển thị: Giờ Ngày | Đội nhà vs Đội khách [Tên BLV]
        title = f"{time_str} {home} vs {away} [{blv_name}]"

        match_item = {
            "id": match_id,
            "title": title,
            "logo": logo,
            "group": category,
            "url": stream_url,
            "timestamp": timestamp
        }
        matches_by_category[category].append(match_item)

    # Tạo nội dung file M3U chuẩn IPTV
    m3u_content = '#EXTM3U x-tvg-url=""\n'

    # Sắp xếp danh mục theo thứ tự ưu tiên (Bóng đá lên đầu)
    sorted_categories = sorted(matches_by_category.keys(), key=lambda x: category_order.get(x, 99))

    for cat in sorted_categories:
        match_list = matches_by_category[cat]
        # Sắp xếp các trận đấu theo thời gian từ sớm đến muộn
        match_list.sort(key=lambda x: x["timestamp"])
        
        for m in match_list:
            m3u_content += f'#EXTINF:-1 tvg-id="{m["id"]}" tvg-name="{m["title"]}" tvg-logo="{m["logo"]}" group-title="{m["group"]}",{m["title"]}\n'
            m3u_content += f'{m["url"]}\n'

    # Ghi ra file playlist.m3u
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print("Cập nhật đầy đủ danh sách hôm nay và ngày mai thành công!")

except Exception as e:
    print(f"Lỗi hệ thống: {e}")
    
