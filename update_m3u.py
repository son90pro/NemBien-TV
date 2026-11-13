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

    for match in data.get("response", []):
        match_id = match.get("matchId")
        sport_raw = match.get("sport", "").lower()
        home = match.get("home", "Home")
        away = match.get("away", "Away")
        timestamp = match.get("timestamp", 0)

        if not match_id:
            continue

        # Lấy link stream thực tế bằng cách gọi API chi tiết của từng trận
        stream_url = ""
        try:
            detail_url = f"https://nembientv.com/truc-tiep/{match_id}?kd_source=1"
            detail_req = urllib.request.Request(
                detail_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(detail_req, timeout=5) as detail_res:
                detail_data = json.loads(detail_res.read().decode("utf-8"))
                stream_url = detail_data.get("streamUrl", "")
        except Exception:
            # Fallback nếu không gọi được API chi tiết
            stream_url = f"https://play.saigon8386.live/{match_id}/index.m3u8"

        # Nếu không có streamUrl thì bỏ qua trận đó
        if not stream_url:
            continue

        # Chuyển đổi timestamp sang múi giờ Việt Nam (GMT+7)
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone(tz_vn)
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

        match_
        
