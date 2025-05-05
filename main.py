import os
import json
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ✅ 구글 시트 연결 함수
def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    credentials = Credentials.from_service_account_info(info, scopes=scopes)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"]).worksheet(os.environ["SHEET_NAME"])
    return sheet

# ✅ 키워드 필터링
def filter_races(sheet, keywords):
    rows = sheet.get_all_records()
    matched = []

    for row in rows:
        race_month = str(row.get("월", "")).strip()
        region = str(row.get("지역", "")).strip()

        if all(any(kw in str(val) for val in [race_month, region]) for kw in keywords):
            matched.append(row)

    return matched

# ✅ /list 명령어 핸들러
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sheet = get_sheet()
        keywords = context.args

        if not keywords:
            await update.message.reply_text("📌 사용법: /list [월] [지역] 예) /list 5월 광주")
            return

        results = filter_races(sheet, keywords)

        if not results:
            await update.message.reply_text("😢 해당 조건에 맞는 대회가 없습니다.")
            return

        msg = "\n\n".join([
            f"📅 {row['일자']} - 🏃‍♀️ {row['대회명']} ({row['지역']})\n🔗 {row.get('링크', '')}"
            for row in results
        ])
        await update.message.reply_text(msg[:4000])  # 메시지 길이 제한 대응
    except Exception as e:
        await update.message.reply_text(f"🚨 오류 발생: {e}")

# ✅ 봇 실행
if __name__ == "__main__":
    token = os.environ["TELEGRAM_TOKEN"]
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("list", list_command))
    app.run_polling()
