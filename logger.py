# logger.py
# คลาส Logger สำหรับการเก็บ log และส่งไปที่ Discord

import json
import requests
import pytz
from datetime import datetime
from config import DISCORD_WEBHOOK_URL

class Logger:
    def __init__(self, verbose=False):
        self.logs = []
        self.verbose = verbose
        self.log_levels = {
            'ERROR': 0,
            'INFO': 1,
            'DEBUG': 2
        }
    
    def _log(self, message, level='INFO'):
        """Internal logging method with level support"""
        print(message)
        log_entry = {
            'message': str(message),
            'level': level
        }
        self.logs.append(log_entry)
    
    def error(self, message):
        """Log error messages (always sent to Discord)"""
        self._log(f"❌ {message}", 'ERROR')
    
    def info(self, message):
        """Log info messages (always sent to Discord)"""
        self._log(f"ℹ️ {message}", 'INFO')
    
    def debug(self, message):
        """Log debug messages (sent only in verbose mode)"""
        self._log(f"🔍 {message}", 'DEBUG')
    
    def print(self, message):
        """Legacy method for backward compatibility"""
        self.info(message)
    
    def get_log_text(self):
        """Get filtered log text based on verbose setting"""
        if self.verbose:
            # Verbose mode: return all logs
            return "\n".join([log['message'] for log in self.logs])
        else:
            # Normal mode: return only ERROR and INFO logs
            filtered_logs = [
                log['message'] for log in self.logs 
                if log['level'] in ['ERROR', 'INFO']
            ]
            return "\n".join(filtered_logs)
    
    def send_to_discord(self, user_ids=None):
        log_text = self.get_log_text()
        if not log_text:
            return
        
        # แบ่งข้อความถ้ายาวเกิน 2000 ตัวอักษร (ข้อจำกัดของ Discord)
        chunks = [log_text[i:i+1900] for i in range(0, len(log_text), 1900)]
        
        # รับเวลาปัจจุบันในรูปแบบ timezone ของไทย
        thai_tz = pytz.timezone('Asia/Bangkok')
        timestamp = datetime.now(thai_tz).strftime("%Y-%m-%d %H:%M:%S")
        
        # ส่งข้อความแรกพร้อมกับ log
        first_message = f"**SABAI Payment Link Notification Log - {timestamp}**\n```\n{chunks[0]}\n```"
        payload = {"content": first_message}
        try:
            response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending to Discord: {e}")
        
        # ส่งข้อความต่อไป (ถ้ามี)
        for i in range(1, len(chunks)):
            message = f"**Continued ({i+1}/{len(chunks)}):**\n```\n{chunks[i]}\n```"
            payload = {"content": message}
            try:
                response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
                response.raise_for_status()
            except Exception as e:
                print(f"Error sending to Discord: {e}")
        
        # แท็กผู้ใช้ Discord (ถ้ามี)
        if user_ids and len(user_ids) > 0:
            mentions = " ".join([f"<@{user_id}>" for user_id in user_ids])
            notification_message = f"cc {mentions}"
            payload = {"content": notification_message}
            try:
                response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
                response.raise_for_status()
            except Exception as e:
                print(f"Error sending mentions to Discord: {e}")

def load_discord_user_ids():
    """โหลด Discord user IDs จากไฟล์ JSON"""
    from config import DISCORD_USER_IDS
    try:
        with open("/tmp/discord_users.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("user_ids", [])
    except (FileNotFoundError, json.JSONDecodeError):
        # ถ้าไม่พบไฟล์หรือไฟล์ไม่ถูกต้อง ให้ใช้ค่าเริ่มต้น
        return DISCORD_USER_IDS
