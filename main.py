import os
import json
import datetime
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import gspread
from google.oauth2.service_account import Credentials

# 구글 시트 설정
SPREADSHEET_ID = '1RiZyD5oxzZCTyveLhB9Y3H2rsurzK35cQMHg39Pzz3I'
WORKSHEET_NAME = 'list'

# 구글 인증 (Railway 환경 변수에서 JSON 파싱)
google_creds = json.loads(os.environ['GOOGLE_CREDENTIALS'])
creds = Credentials.from_service_account_info(google_creds)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)

# 텔레그램 봇 토큰
BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']  # Railway에 등록한 환경변수

# 날짜 처리 유틸
def extract_month(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').month
    except:
        return None

def extract_region(text):
    return text[:2] if text else ''

# /list 명령어 처리
async def list_race(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("📌 예시: /list 5월 또는 /list 5월 광주 전남")
        return

    months = []
    regions = []

    for arg in args:
        if '월' in arg:
            try:
                months.append(int(arg.replace('월', '')))
            except:
                continue
        else:
            regions.append(arg.replace('"', '').replace("'", ''))

    rows = sheet.get_all_records()
    filtered = []

    for row in rows:
        race_month = extract_month(row['일자'])
        race_region = extract_region(row['지역'])

        if (not months or race_month in months) and (not regions or any(r in race_region for r in regions)):
            filtered.append(f"{row['일자']} | {row['종목']} | {row['대회명']} | {row['지역']} | {row['접수 시작일']} ~ {row['접수 마감일']}\n🔗 {row['링크']}")

    if filtered:
        message = f"🏃‍♂️ 총 {len(filtered)}개의 대회가 있습니다:\n\n" + "\n\n".join(filtered[:20])
    else:
        message = "📭 조건에 맞는 대회가 없습니다."

    await update.message.reply_text(message)

# 봇 실행
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("list", list_race))
    app.run_polling()
