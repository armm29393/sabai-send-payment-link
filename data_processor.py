from config import (
    IS_GEN_PAYMENT_LINK, 
    IS_SEND_NOTI, 
    PAYMENT_LINK,
    LAND_NO,
    PHONE,
    EMAIL
)
from notification import send_notification
import time

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
    
    noti_success = 0
    noti_failed = 0
    
    # อัพเดตข้อมูลใน spreadsheet
    for row_data in rows_to_update:
        row_num = row_data["row"]
        data = row_data["data"]
        
        # ส่งการแจ้งเตือนไปยัง API
        result = send_notification(data, indices)
        
        if result['success']:
            print(f"ส่งการแจ้งเตือนสำเร็จสำหรับแถวที่ {row_num}")
            
            # ตรวจสอบว่าต้องเพิ่มคอลัมน์ is Send Noti หรือไม่
            if len(data) <= indices['is_send_noti']:
                # เพิ่มคอลัมน์ที่ว่างจนถึง is_send_noti_index
                while len(data) < indices['is_send_noti']:
                    data.append("")
                data.append("Done")
            else:
                data[indices['is_send_noti']] = "Done"
            
            # อัพเดตข้อมูลใน spreadsheet
            print(f"กำลังอัพเดตข้อมูลในแถวที่ {row_num} - เปลี่ยน is Send Noti เป็น Done")
            update_sheet_row(row_num, data)
            print(f"อัพเดตข้อมูลในแถวที่ {row_num} เรียบร้อยแล้ว")
            noti_success += 1
        else:
            logger.print(f"ส่งการแจ้งเตือนไม่สำเร็จสำหรับแปลง {data[indices['land_no']] if indices['land_no'] != -1 else 'ไม่ระบุ'} (แถว {row_num})")
            logger.print(f"Error: {result.get('error', 'Unknown error')}")
            logger.print("-" * 30)
            noti_failed += 1

        # หน่วงเวลาเล็กน้อยเพื่อไม่ให้ยิง API ถี่เกินไป
        time.sleep(1)

    return noti_success, noti_failed, len(rows_to_update) > 0
