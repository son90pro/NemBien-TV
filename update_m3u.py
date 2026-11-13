import json
import urllib.request
from datetime import datetime

# URL API lịch thi đấu từ Ném Biên TV
url = "https://nembientv.com/cms-schedule.json"

try:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))

    # Bắt đầu nội dung file M3U
    m3u_content = '#EXTM3U x-tvg-url=""\n'

    # Duyệt qua danh sách trận đấu từ API
    for match in data.get("response", []):
        match_id = match.get("matchId")
        sport = match.get("sport", "football")
        league = match.get("league", "Thể Thao")
        home = match.get("home", "Home")
        away = match.get("away", "Away")
        timestamp = match.get("timestamp", 0)

        # Chuyển đổi timestamp sang giờ ngày tháng (giờ Việt Nam UTC+7)
        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%H:%M %d/%m")

        # Lấy tên BLV
        commentators = match.get("commentators", [])
        blv_name = commentators[0]["name"] if commentators else "Live"

        # Lấy logo đội nhà làm icon cho kênh
        logo = match.get("homeLogo", "")

        # Tiêu đề hiển thị chuẩn định dạng mẫu yêu cầu: Giờ Ngày | Đội nhà vs Đội khách [Tên BLV]
        title = f"{time_str} {home} vs {away} [{blv_name}]"

        # Link luồng phát (Anh có thể thay thế bằng link stream thực tế hoặc link bắt từ matchId của web)
        # Ví dụ link phát sóng giả định dựa trên matchId:
        stream_url = f"https://nembientv.com/live/{match_id}/index.m3u8"

        # Thêm vào định dạng M3U chuẩn IPTV
        m3u_content += f'#EXTINF:-1 tvg-id="{match_id}" tvg-name="{title}" tvg-logo="{logo}" group-title="{league} - NÉM BIÊN TV",{title}\n'
        m3u_content += f"{stream_url}\n"

    # Ghi ra file playlist.m3u
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print("Cập nhật file playlist.m3u thành công!")

except Exception as e:
    print(f"Lỗi khi cập nhật: {e}")
  
