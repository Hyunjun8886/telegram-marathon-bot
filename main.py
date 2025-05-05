import os
import logging
import gspread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # 로컬 테스트 시 사용

# 환경변수
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME", "list")

# Google Sheets 연결
def get_sheet():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise Exception("GOOGLE_CREDENTIALS_JSON 환경변수가 없습니다.")
    import json
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(SHEET_NAME)
    return sheet

# /list 명령어 핸들러
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    now = datetime.now()
    this_month = f"{now.month}월"

    months = [arg for arg in args if "월" in arg]
    regions = [arg.replace('"', '') for arg in args if "월" not in arg]
    if not months:
        months = [this_month]

    sheet = get_sheet()
    data = sheet.get_all_records()
    filtered = []
    for row in data:
        if row["월"] in months and (not regions or any(region in row["지역"] for region in regions)):
            filtered.append(f"{row['일자']} | {row['대회명']} | {row['지역']}")

    if filtered:
        text = "🏃‍♀️ 요청하신 대회 일정:\n" + "\n".join(filtered)
    else:
        text = "😢 해당 조건에 맞는 대회가 없습니다."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

# 봇 실행
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("list", list_command))
    app.run_polling()
