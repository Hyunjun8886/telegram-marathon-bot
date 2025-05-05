import os
import json
import gspread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 구글 시트 연결
def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials_info = json.loads(os.environ['GOOGLE_CREDENTIALS_JSON'])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(os.environ['GOOGLE_SHEET_ID']).worksheet(os.environ['SHEET_NAME'])
    return sheet

# 필터링된 메시지 생성
def filter_races(sheet, keywords):
    rows = sheet.get_all_records()
    matched = []

    for row in rows:
        race_month = str(row.get("월", "")).strip()
        region = str(row.get("지역", "")).strip()

        # 키워드 모두 포함하면 매칭
        if all(any(kw in str(value) for value in [race_month, region]) for kw in keywords):
            matched.append(row)

    return matched

# 텔레그램 명령어 핸들러
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sheet = get_sheet()
        keywords = context.args  # 사용자가 입력한 인자들 (예: /list 5월 광주)

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
        await update.message.reply_text(f"오류 발생: {e}")

# 봇 실행
if __name__ == "__main__":
    token = os.environ["TELEGRAM_TOKEN"]
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("list", list_command))
    app.run_polling()
