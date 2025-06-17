# notification.py
# ฟังก์ชันสำหรับการส่งการแจ้งเตือนไปยัง API

import requests
from config import (
    SABAI_API_URL, 
    SABAI_API_TOKEN, 
    NOTIFICATION_TITLE, 
    NOTIFICATION_DESCRIPTION
)

def xstr(s):
    """แปลงค่าว่างเป็น None"""
    return None if s in ['', 'null'] else str(s)

def send_notification(row_data, indices):
    """
    ส่งการแจ้งเตือนไปยัง API
    
    Args:
        row_data (list): ข้อมูลแถวที่ต้องการส่งการแจ้งเตือน
        indices (dict): ดัชนีของคอลัมน์ต่างๆ
    
    Returns:
        dict: ผลลัพธ์การส่งการแจ้งเตือน
    """
    try:
        # สร้าง payload สำหรับ API
        payload = {
            'unit_id': xstr(row_data[indices['land_no']]) if indices['land_no'] != -1 else None,
            'title_en': NOTIFICATION_TITLE,
            'title_th': NOTIFICATION_TITLE,
            'description_en': NOTIFICATION_DESCRIPTION,
            'description_th': NOTIFICATION_DESCRIPTION,
            'feature': "payment::link",
            'phone': xstr(row_data[indices['phone']]) if indices['phone'] != -1 else None,
            'email': xstr(row_data[indices['email']]) if indices['email'] != -1 else None,
            'link_content': xstr(row_data[indices['payment_link']]) if indices['payment_link'] != -1 else None,
        }
        
        # ส่งคำขอไปยัง API
        response = requests.post(
            SABAI_API_URL, 
            json=payload, 
            headers={"Authorization": SABAI_API_TOKEN}
        )
        
        # ตรวจสอบสถานะการตอบกลับ
        if response.status_code == 200:
            return {
                'success': True,
                'response': response.json()
            }
        else:
            return {
                'success': False,
                'status_code': response.status_code,
                'error': response.text
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
