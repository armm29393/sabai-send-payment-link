# lambda_function.py
# ฟังก์ชันหลักสำหรับ AWS Lambda

import time
from datetime import datetime

from config import (
    IS_GEN_PAYMENT_LINK, 
    IS_SEND_NOTI, 
    PAYMENT_LINK,
    LAND_NO,
    PHONE,
    EMAIL
)
from logger import Logger, load_discord_user_ids
from sheets_service import get_sheet_data, update_sheet_row
from notification import send_notification

def find_column_indices(headers):
    """
    หาตำแหน่งคอลัมน์ที่ต้องการ
    
    Args:
        headers (list): รายการหัวข้อคอลัมน์
    
    Returns:
        dict: ดัชนีของคอลัมน์ต่างๆ
    """
    indices = {
        'payment_link': -1,
        'is_gen_payment_link': -1,
        'is_send_noti': -1,
        'land_no': -1,
        'phone': -1,
        'email': -1
    }
    
    for i, header in enumerate(headers):
        if header == PAYMENT_LINK:
            indices['payment_link'] = i
        elif header == IS_GEN_PAYMENT_LINK:
            indices['is_gen_payment_link'] = i
        elif header == IS_SEND_NOTI:
            indices['is_send_noti'] = i
        elif header == LAND_NO:
            # lambda_function.py (ต่อ)
            indices['land_no'] = i
        elif header == PHONE:
            indices['phone'] = i
        elif header == EMAIL:
            indices['email'] = i
    
    return indices

def process_sheet_data(values, logger):
    """
    ประมวลผลข้อมูลจาก Google Sheets
    
    Args:
        values (list): ข้อมูลจาก Google Sheets
        logger (Logger): Logger สำหรับบันทึก log
    
    Returns:
        tuple: (จำนวนการแจ้งเตือนที่ส่งสำเร็จ, มีการอัพเดตข้อมูลหรือไม่)
    """
    # ดึงข้อมูลส่วนหัวจากแถวแรก
    headers = values[0]
    
    # หาตำแหน่งคอลัมน์ที่ต้องการ
    indices = find_column_indices(headers)
    
    # ตรวจสอบว่าพบคอลัมน์ที่จำเป็นหรือไม่
    required_columns = ['payment_link', 'is_gen_payment_link', 'is_send_noti']
    for col in required_columns:
        if indices[col] == -1:
            raise Exception(f"ไม่พบคอลัมน์ที่จำเป็น ({col})")
    
    # ตรวจสอบและอัพเดตข้อมูล
    rows_to_update = []
    
    for i in range(1, len(values)):
        row = values[i]
        
        # ตรวจสอบว่า row มีข้อมูลครบทุกคอลัมน์ที่ต้องการหรือไม่
        if len(row) <= max(indices['payment_link'], indices['is_gen_payment_link']):
            continue
        
        # ตรวจสอบเงื่อนไข: is Gen Payment Link = Done และ Payment Link เริ่มต้นด้วย https:// และ is Send Noti ไม่เท่ากับ Done
        is_send_noti_done = (len(row) > indices['is_send_noti'] and row[indices['is_send_noti']] == "Done")
        
        if (row[indices['is_gen_payment_link']] == "Done" and 
            row[indices['payment_link']].startswith("https://") and 
            not is_send_noti_done):
            
            # แสดงข้อมูลของแถวที่เข้าเงื่อนไข
            for j in range(min(len(headers), len(row))):
                # ข้ามคอลัมน์ที่ไม่ต้องการแสดง
                if headers[j] in [PAYMENT_LINK, IS_GEN_PAYMENT_LINK, IS_SEND_NOTI, PHONE, EMAIL]:
                    continue
                logger.print(f"{headers[j]}: {row[j]}")
            
            logger.print("-" * 30)
            
            # เตรียมข้อมูลสำหรับอัพเดต is Send Noti เป็น Done
            rows_to_update.append({
                "row": i + 1,  # แถวใน spreadsheet (เริ่มจาก 1)
                "data": row.copy()  # ใช้ copy เพื่อไม่ให้กระทบข้อมูลเดิม
            })
    
    sent_noti = 0
    
    # อัพเดตข้อมูลใน spreadsheet
    for row_data in rows_to_update:
        row_num = row_data["row"]
        data = row_data["data"]
        
        # ส่งการแจ้งเตือนไปยัง API
        result = send_notification(data, indices)
        
        if result['success']:
            logger.print(f"ส่งการแจ้งเตือนสำเร็จสำหรับแถวที่ {row_num}")
            
            # ตรวจสอบว่าต้องเพิ่มคอลัมน์ is Send Noti หรือไม่
            if len(data) <= indices['is_send_noti']:
                # เพิ่มคอลัมน์ที่ว่างจนถึง is_send_noti_index
                while len(data) < indices['is_send_noti']:
                    data.append("")
                data.append("Done")
            else:
                data[indices['is_send_noti']] = "Done"
            
            # อัพเดตข้อมูลใน spreadsheet
            logger.print(f"กำลังอัพเดตข้อมูลในแถวที่ {row_num} - เปลี่ยน is Send Noti เป็น Done")
            update_sheet_row(row_num, data)
            logger.print(f"อัพเดตข้อมูลในแถวที่ {row_num} เรียบร้อยแล้ว")
            sent_noti += 1
        else:
            logger.print(f"ส่งการแจ้งเตือนไม่สำเร็จสำหรับแถวที่ {row_num}")
            logger.print(f"Error: {result.get('error', 'Unknown error')}")
        
        logger.print("-" * 30)
        
        # หน่วงเวลาเล็กน้อยเพื่อไม่ให้ยิง API ถี่เกินไป
        time.sleep(1)
    
    return sent_noti, len(rows_to_update) > 0

def lambda_handler(event, context):
    """
    ฟังก์ชันหลักสำหรับ AWS Lambda
    
    Args:
        event (dict): ข้อมูลเหตุการณ์จาก AWS Lambda
        context (object): ข้อมูลบริบทจาก AWS Lambda
    
    Returns:
        dict: ผลลัพธ์การทำงาน
    """
    # โหลด Discord user IDs
    discord_user_ids = load_discord_user_ids()
    
    # สร้าง logger
    logger = Logger()
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.print(f"**SABAI Payment Link Notification Log - {timestamp}**")
        
        # รับข้อมูลจาก Google Sheets
        values = get_sheet_data()
        
        # ประมวลผลข้อมูล
        sent_noti, has_updates = process_sheet_data(values, logger)
        
        # แท็กผู้ใช้เฉพาะเมื่อมีการอัพเดตข้อมูล
        if has_updates:
            logger.print(f"ส่งโนติฯ Payment Link สำเร็จ {sent_noti} รายการ")
            logger.send_to_discord(discord_user_ids)
        else:
            logger.print("ไม่พบข้อมูลที่ต้องส่งโนติฯ")
            logger.send_to_discord()  # ไม่ต้องแท็กผู้ใช้ถ้าไม่มีการอัพเดต
        
        return {
            'statusCode': 200,
            'body': f'ส่งโนติฯ Payment Link สำเร็จ {sent_noti} รายการ'
        }
    
    except Exception as e:
        error_message = str(e)
        logger.print(f"เกิดข้อผิดพลาด: {error_message}")
        logger.send_to_discord(discord_user_ids)
        
        return {
            'statusCode': 500,
            'body': f'เกิดข้อผิดพลาด: {error_message}'
        }

# สำหรับการทดสอบในเครื่อง local
if __name__ == "__main__":
    lambda_handler(None, None)
