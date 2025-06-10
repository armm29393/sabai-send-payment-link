# config.py
# ไฟล์สำหรับเก็บค่า configuration ต่างๆ

# Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "15ax0....HdJc"  # Replace with your actual spreadsheet ID
SHEET_NAME = "ชีต1"

# Column Headers
IS_GEN_PAYMENT_LINK = "is Gen Payment Link"
IS_SEND_NOTI = "is Send Noti"
PAYMENT_LINK = "Payment Link"
LAND_NO = "หมายเลขแปลง ตัวอย่างเช่น 1099-001"
PHONE = "เบอร์โทรศัพท์"
EMAIL = "อีเมล์"

# SABAI API
SABAI_API_URL = "https://test.com/noti"
SABAI_API_TOKEN = "Bearer eyJhbGci...DIg"  # Replace with your actual API token

# Discord webhook
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/12....Cx4"
DISCORD_USER_IDS = []  # Default empty list if no file is found

# Notification Content
NOTIFICATION_TITLE = "เรียน ท่านเจ้าของบ้าน"
NOTIFICATION_BUTTON = "ดำเนินการชำระเงิน"
NOTIFICATION_DESCRIPTION = f'ตามที่ท่านได้แจ้งความประสงค์ในการชำระค่าบริการสาธารณะ กรุณาดำเนินการชำระเงินโดยการกดปุ่ม "{NOTIFICATION_BUTTON}" ด้านล่างภายใน 24 ชั่วโมง นับจากได้รับข้อความนี้ เงื่อนไขการชำระเงินเป็นไปตามที่ธนาคารกำหนด ขอขอบพระคุณมา ณ โอกาสนี้'
