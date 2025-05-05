# Telegram Marathon Bot

이 텔레그램 봇은 구글시트에 기록된 마라톤 대회 정보를 `/list` 명령어로 조회할 수 있습니다.

## 명령어 예시
- `/list 5월 6월`
- `/list 6월 "서울" "전남"`

## 환경 변수 (.env 또는 Render 환경 설정에 추가)
- `TELEGRAM_TOKEN`: 봇 토큰
- `GOOGLE_SHEET_ID`: 스프레드시트 ID
- `SHEET_NAME`: 시트 이름 (기본: `list`)
- `GOOGLE_CREDENTIALS_JSON`: 서비스 계정 JSON 내용 전체
