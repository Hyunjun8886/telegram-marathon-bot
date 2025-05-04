import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import gspread
from google.oauth2 import service_account
from datetime import datetime

# ✅ 환경변수
TOKEN = os.getenv("TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

# ✅ 인증 처리
info = json.loads(GOOGLE_CREDS_JSON)
creds = service_account.Credentials.from_service_account_info(info)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("list")  # 정리된 시트 사용

# ✅ 로깅
logging.basicConfig(level=logging.INFO)

# ✅ /list 명령어 처리
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    now = datetime.now()
    month_filter = []
    region_filter = []

    # 인자 구분 (숫자: 월, 문자열: 지역)
    for arg in args:
        if arg.endswith("월") or arg.strip("월").isdigit():
            month_filter.append(arg.strip("월"))
        else:
            region_filter.append(arg.replace('"', '').replace("“", "").replace("”", ""))

    values = sheet.get_all_records()
    result = []

    for row in values:
        race_month = str(row.get("월", ""))
        race_region = str(row.get("지역", ""))[:2]  # 앞 2글자

        # 월 필터 적용
        if month_filter and race_month not in month_filter:
            continue
        # 지역 필터 적용
        if region_filter and not any(r in race_region for r in region_filter):
            continue

        result.append(f"{row['일자']} | {row['종목']} | {row['대회명']} | {row['장소']}")

    if result:
        reply = "🏃‍♂️ 검색된 대회 목록:\n" + "\n".join(result[:20])  # 최대 20개
    else:
        reply = "❌ 조건에 맞는 대회가 없습니다."

    await update.message.reply_text(reply)

# ✅ 메인 실행
if __name__ == '__main__':
    print("🤖 러닝매니저 봇 실행 중...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("list", list_command))
    app.run_polling()
