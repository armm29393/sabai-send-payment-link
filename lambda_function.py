# lambda_function.py
# ฟังก์ชันหลักสำหรับ AWS Lambda

import json

from config import (
    validate_config,
    X_API_KEY,
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
from data_processor import process_sheet_data

def lambda_handler(event, context):
    """
    ฟังก์ชันหลักสำหรับ AWS Lambda
    
    Args:
        event (dict): ข้อมูลเหตุการณ์จาก AWS Lambda
        context (object): ข้อมูลบริบทจาก AWS Lambda
    
    Returns:
        dict: ผลลัพธ์การทำงาน
    """
    # ตรวจสอบค่า configuration
    try:
        validate_config()
    except Exception as e:
        error_message = str(e)
        logger.print(f"เกิดข้อผิดพลาด: {error_message}")
        logger.send_to_discord(['400624061925031946'])
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'เกิดข้อผิดพลาด: {error_message}'
            })
        }

    headers = event.get("headers") or {}
    provided_api_key = headers.get("x-api-key")

    if provided_api_key != X_API_KEY:
        return {"statusCode": 403, "body": json.dumps({"success": False, "message": "Invalid API key"})}
    
    # โหลด Discord user IDs
    discord_user_ids = load_discord_user_ids()
    
    # สร้าง logger
    logger = Logger()
    
    try:
        # รับข้อมูลจาก Google Sheets
        values = get_sheet_data()
        
        # ประมวลผลข้อมูล
        noti_success, noti_failed, has_updates = process_sheet_data(values, logger)

        # แท็กผู้ใช้เฉพาะเมื่อมีการอัพเดตข้อมูล
        if has_updates:
            logger.print(f"ส่งโนติฯ Payment Link สำเร็จ {noti_success} รายการ, ล้มเหลว {noti_failed} รายการ")
            logger.send_to_discord(discord_user_ids)
        else:
            logger.print("ไม่พบข้อมูลที่ต้องส่งโนติฯ")
            logger.send_to_discord()  # ไม่ต้องแท็กผู้ใช้ถ้าไม่มีการอัพเดต
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': f'ส่งโนติฯ Payment Link สำเร็จ {noti_success} รายการ, ล้มเหลว {noti_failed} รายการ',
            })
        }
    
    except Exception as e:
        error_message = str(e)
        logger.print(f"เกิดข้อผิดพลาด: {error_message}")
        logger.send_to_discord(['400624061925031946'])
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'เกิดข้อผิดพลาด: {error_message}'
            })
        }

# สำหรับการทดสอบในเครื่อง local
if __name__ == "__main__":
    lambda_handler(None, None)
