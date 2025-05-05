import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 환경 변수에서 설정 가져오기
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# 구글 시트 클라이언트 생성
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(GOOGLE_CREDENTIALS_JSON), scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(SHEET_NAME)
    return sheet

# /list 명령어 핸들러
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sheet = get_sheet()
        data = sheet.get_all_records()

        if not data:
            await update.message.reply_text("😢 해당 조건에 맞는 대회가 없습니다.")
            return

        # 메시지 생성
        message = ""
        for row in data:
            message += f"📅 {row['일자']} - {row['대회명']} ({row['지역']})\n🔗 {row['링크']}\n\n"

        await update.message.reply_text(message.strip())

    except Exception as e:
        logging.exception("에러 발생:")
        await update.message.reply_text("⚠️ 데이터를 불러오는 중 오류가 발생했습니다.")

# 봇 실행
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("list", list_command))
    app.run_polling()
