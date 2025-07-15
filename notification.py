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
    return None if s in ['', 'null'] else str(s).strip()

def send_notification(row_data, indices):
    """
    ส่งการแจ้งเตือนไปยัง API
    
    Args:
        row_data (list): ข้อมูลแถวที่ต้องการส่งการแจ้งเตือน
        indices (dict): ดัชนีของคอลัมน์ต่างๆ
    
    Returns:
        dict: ผลลัพธ์การส่งการแจ้งเตือน
    """
    import traceback
    
    try:
        # ใช้ print เพื่อให้ debug logs ยังคงแสดงใน console
        print(f"[send_notification] เริ่มส่งการแจ้งเตือน")
        print(f"[send_notification] Row data length: {len(row_data)}")
        print(f"[send_notification] Indices: {indices}")
        
        # ตรวจสอบข้อมูลที่จำเป็น
        if not row_data:
            raise Exception("ข้อมูลแถวเป็นรายการว่าง")
        
        # ดึงข้อมูลแต่ละฟิลด์อย่างปลอดภัย
        def safe_get_value(index_key):
            try:
                index = indices.get(index_key, -1)
                if index == -1:
                    print(f"[send_notification] ไม่พบ index สำหรับ {index_key}")
                    return None
                if index >= len(row_data):
                    print(f"[send_notification] Index {index} สำหรับ {index_key} เกินขนาดข้อมูล ({len(row_data)})")
                    return None
                value = xstr(row_data[index])
                print(f"[send_notification] {index_key} (index {index}): {value}")
                return value
            except Exception as e:
                print(f"[send_notification] Error getting {index_key}: {str(e)}")
                return None
        
        # สร้าง payload สำหรับ API
        unit_id = safe_get_value('land_no')
        phone = safe_get_value('phone')
        email = safe_get_value('email')
        link_content = safe_get_value('payment_link')
        
        payload = {
            'unit_id': unit_id,
            'title_en': NOTIFICATION_TITLE,
            'title_th': NOTIFICATION_TITLE,
            'description_en': NOTIFICATION_DESCRIPTION,
            'description_th': NOTIFICATION_DESCRIPTION,
            'feature': "payment::link",
            'phone': phone,
            'email': email,
            'link_content': link_content,
        }
        
        print(f"[send_notification] Payload: {payload}")
        
        # ส่งคำขอไปยัง API
        print(f"[send_notification] กำลังส่งคำขอไปยัง: {SABAI_API_URL}")
        response = requests.post(
            SABAI_API_URL, 
            json=payload, 
            headers={"Authorization": SABAI_API_TOKEN},
            timeout=30  # เพิ่ม timeout
        )
        
        print(f"[send_notification] Response status: {response.status_code}")
        print(f"[send_notification] Response text: {response.text}")
        
        # ตรวจสอบสถานะการตอบกลับ
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"[send_notification] Response JSON: {response_json}")
                return {
                    'success': True,
                    'response': response_json
                }
            except Exception as json_error:
                print(f"[send_notification] Error parsing JSON: {str(json_error)}")
                return {
                    'success': True,  # ถือว่าสำเร็จถ้า status 200 แม้ JSON จะ parse ไม่ได้
                    'response': response.text
                }
        else:
            return {
                'success': False,
                'status_code': response.status_code,
                'error': response.text
            }
            
    except requests.exceptions.Timeout:
        error_msg = "API request timeout"
        print(f"[send_notification] {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except requests.exceptions.RequestException as req_error:
        error_msg = f"Request error: {str(req_error)}"
        print(f"[send_notification] {error_msg}")
        print(f"[send_notification] Stack trace: {traceback.format_exc()}")
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"[send_notification] {error_msg}")
        print(f"[send_notification] Stack trace: {traceback.format_exc()}")
        return {
            'success': False,
            'error': error_msg
        }
