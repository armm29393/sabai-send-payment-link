# config.py
# ไฟล์สำหรับเก็บค่า configuration ต่างๆ

import os

# Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
SHEET_NAME = os.environ.get("SHEET_NAME", "ชีต1")

# Column Headers
IS_GEN_PAYMENT_LINK = "is Gen Payment Link"
IS_SEND_NOTI = "is Send Noti"
PAYMENT_LINK = "Payment Link"
LAND_NO = "หมายเลขแปลง ตัวอย่างเช่น 1099-001"
PHONE = "เบอร์โทรศัพท์"
EMAIL = "อีเมล์"

# SABAI API
SABAI_API_URL = os.environ.get("SABAI_API_URL")
SABAI_API_TOKEN = os.environ.get("SABAI_API_TOKEN")

# Discord webhook
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
DISCORD_USER_IDS = [
    '406684705497415690', # aof
    '757997300059734088', # aom
]  # Default empty list if no file is found

# Notification Content
NOTIFICATION_TITLE = "เรียน ท่านเจ้าของบ้าน"
NOTIFICATION_BUTTON = "ดำเนินการชำระเงิน"
NOTIFICATION_DESCRIPTION = f'ตามที่ท่านได้แจ้งความประสงค์ในการชำระค่าบริการสาธารณะ กรุณาดำเนินการชำระเงินโดยการกดปุ่ม "{NOTIFICATION_BUTTON}" ด้านล่างภายใน 24 ชั่วโมง นับจากได้รับข้อความนี้ เงื่อนไขการชำระเงินเป็นไปตามที่ธนาคารกำหนด ขอขอบพระคุณมา ณ โอกาสนี้'

X_API_KEY = os.environ.get("X_API_KEY")

# ตรวจสอบว่ามีการกำหนดค่าที่จำเป็นหรือไม่
def validate_config():
    """ตรวจสอบว่ามีการกำหนดค่า configuration ที่จำเป็นหรือไม่"""
    required_configs = {
        "SPREADSHEET_ID": SPREADSHEET_ID,
        "SABAI_API_URL": SABAI_API_URL,
        "SABAI_API_TOKEN": SABAI_API_TOKEN,
        "DISCORD_WEBHOOK_URL": DISCORD_WEBHOOK_URL,
        "X_API_KEY": X_API_KEY,
    }
    
    missing_configs = [key for key, value in required_configs.items() if not value]
    
    if missing_configs:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_configs)}")
