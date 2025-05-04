import time
import requests
import gspread
import datetime
import re
from google.oauth2.service_account import Credentials

# 🔐 Google Sheets 인증 설정
SERVICE_ACCOUNT_FILE = 'D:/HJ작업/python/web scraper/competition-schedule.json'
SPREADSHEET_ID = '1RiZyD5oxzZCTyveLhB9Y3H2rsurzK35cQMHg39Pzz3I'
SHEET_NAME = 'list'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# 🤖 Telegram 설정
TOKEN = '7828556997:AAHuEXRpm4iitn24tN-w7V7-u-2x_CqGbIU'  # ✅ ✅ ✅ 여기만 바꾸면 됩니다!
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# 📄 시트 데이터 불러오기
def get_sheet_data():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    return sheet.get_all_values()[1:]  # 헤더 제외

# 🧠 명령어 파서 (월 or 지역 or 둘 다 가능)
def parse_flexible_command(text):
    quoted = re.findall(r'"([^"]+)"', text)
    months = re.findall(r'(\d{1,2})월', text)

    # /list 제거 후 나머지 토큰 중 한글 (월 제거)
    tokens = text.replace("/list", "").strip().split()
    unquoted = [t for t in tokens if '월' not in t and not t.startswith('"')]
    regions = quoted + unquoted

    return [int(m) for m in months], regions

# 🎯 필터링
def filter_races(rows, month_list, region_list):
    results = []
    for row in rows:
        date_str, _, _, name, _, _, region, link = row[:8]
        try:
            race_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            continue

        if month_list and race_date.month not in month_list:
            continue
        if region_list and not any(r in region for r in region_list):
            continue

        results.append(f"📌 {name} ({date_str})\n📍{region}\n🔗 {link}")
    return results

# 📬 메시지 전송
def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", data={"chat_id": chat_id, "text": text})

# 🔁 메시지 처리 루프
def run_bot():
    print("🤖 러닝매니저 봇 실행 중... (/list 6월 '서울')")
    offset = None
    while True:
        try:
            res = requests.get(f"{API_URL}/getUpdates", params={"timeout": 30, "offset": offset})
            data = res.json()
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message")
                if not message:
                    continue

                text = message.get("text", "")
                chat_id = message["chat"]["id"]

                if text.startswith("/list"):
                    month_list, region_list = parse_flexible_command(text)
                    rows = get_sheet_data()
                    filtered = filter_races(rows, month_list, region_list)

                    if filtered:
                        label = f"📅 월: {'전체' if not month_list else ', '.join(str(m) + '월' for m in month_list)}"
                        label += f"\n📍 지역: {'전체' if not region_list else ', '.join(region_list)}"
                        send_message(chat_id, f"{label}\n\n" + "\n\n".join(filtered[:10]))
                    else:
                        msg = f"📭 결과 없음\n월: {'전체' if not month_list else ', '.join(str(m)+'월' for m in month_list)}"
                        if region_list:
                            msg += f"\n지역: {', '.join(region_list)}"
                        send_message(chat_id, msg)
        except Exception as e:
            print("❌ 오류 발생:", e)
        time.sleep(2)

# ▶️ 실행
if __name__ == "__main__":
    run_bot()
