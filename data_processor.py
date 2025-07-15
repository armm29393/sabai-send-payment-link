from config import (
    ERROR_RES,
    IS_GEN_PAYMENT_LINK, 
    IS_SEND_NOTI, 
    PAYMENT_LINK,
    LAND_NO,
    PHONE,
    EMAIL,
    TIMESTAMP
)
from datetime import datetime
from notification import send_notification
from sheets_service import update_sheet_row
import time
import pytz
import json

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
        if header == TIMESTAMP:
            indices['timestamp'] = i
        elif header == PAYMENT_LINK:
            indices['payment_link'] = i
        elif header == IS_GEN_PAYMENT_LINK:
            indices['is_gen_payment_link'] = i
        elif header == IS_SEND_NOTI:
            indices['is_send_noti'] = i
        elif header == LAND_NO:
            indices['land_no'] = i
        elif header == PHONE:
            indices['phone'] = i
        elif header == EMAIL:
            indices['email'] = i
        elif header == ERROR_RES:
            indices['error'] = i
    
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
    import traceback
    
    try:
        logger.print(f"[process_sheet_data] เริ่มประมวลผลข้อมูล จำนวนแถว: {len(values)}")
        
        thai_tz = pytz.timezone('Asia/Bangkok')
        # ดึงข้อมูลส่วนหัวจากแถวแรก
        headers = values[0]
        logger.print(f"[process_sheet_data] Headers: {headers}")
        
        # หาตำแหน่งคอลัมน์ที่ต้องการ
        indices = find_column_indices(headers)
        logger.print(f"[process_sheet_data] Column indices: {indices}")
        
        # ตรวจสอบว่าพบคอลัมน์ที่จำเป็นหรือไม่
        required_columns = ['payment_link', 'is_gen_payment_link', 'is_send_noti']
        for col in required_columns:
            if indices[col] == -1:
                raise Exception(f"ไม่พบคอลัมน์ที่จำเป็น ({col})")
        
        # ตรวจสอบและอัพเดตข้อมูล
        rows_to_update = []
        
        for i in range(1, len(values)):
            try:
                row = values[i]
                logger.print(f"[process_sheet_data] กำลังตรวจสอบแถวที่ {i+1}, จำนวนคอลัมน์: {len(row)}")
                
                # ตรวจสอบว่า row มีข้อมูลครบทุกคอลัมน์ที่ต้องการหรือไม่
                required_indices = [indices['payment_link'], indices['is_gen_payment_link']]
                max_required_index = max(required_indices)
                
                if len(row) <= max_required_index:
                    logger.print(f"[process_sheet_data] ข้ามแถวที่ {i+1} เนื่องจากข้อมูลไม่ครบ (ต้องการ index {max_required_index}, มี {len(row)})")
                    continue
                
                # ตรวจสอบเงื่อนไข: is Gen Payment Link = Done และ Payment Link เริ่มต้นด้วย https:// และ is Send Noti ไม่เท่ากับ Done
                is_send_noti_done = (len(row) > indices['is_send_noti'] and indices['is_send_noti'] >= 0 and row[indices['is_send_noti']] == "Done")
                
                # ตรวจสอบว่ามี payment_link และ is_gen_payment_link หรือไม่
                payment_link_value = row[indices['payment_link']] if indices['payment_link'] < len(row) else ""
                is_gen_payment_link_value = row[indices['is_gen_payment_link']] if indices['is_gen_payment_link'] < len(row) else ""
                
                if (is_gen_payment_link_value == "Done" and 
                    payment_link_value.startswith("https://") and 
                    not is_send_noti_done):
                    
                    logger.print(f"[process_sheet_data] แถวที่ {i+1} เข้าเงื่อนไขการส่งโนติฯ")
                    
                    # แสดงข้อมูลของแถวที่เข้าเงื่อนไข
                    for j in range(min(len(headers), len(row))):
                        # ข้ามคอลัมน์ที่ไม่ต้องการแสดง
                        if headers[j] in [PAYMENT_LINK, IS_GEN_PAYMENT_LINK, IS_SEND_NOTI, TIMESTAMP]:
                            continue
                        logger.print(f"{headers[j]}: {row[j]}")
                    
                    logger.print("-" * 30)
                    
                    # เตรียมข้อมูลสำหรับอัพเดต is Send Noti เป็น Done
                    rows_to_update.append({
                        "row": i + 1,  # แถวใน spreadsheet (เริ่มจาก 1)
                        "data": row.copy()  # ใช้ copy เพื่อไม่ให้กระทบข้อมูลเดิม
                    })
                    
            except Exception as row_error:
                logger.print(f"[process_sheet_data] Error ในแถวที่ {i+1}: {str(row_error)}")
                logger.print(f"[process_sheet_data] Stack trace: {traceback.format_exc()}")
                continue
        
        logger.print(f"[process_sheet_data] พบแถวที่ต้องอัพเดต: {len(rows_to_update)} แถว")
        
    except Exception as e:
        logger.print(f"[process_sheet_data] Critical error: {str(e)}")
        logger.print(f"[process_sheet_data] Stack trace: {traceback.format_exc()}")
        raise
    
    noti_success = 0
    noti_failed = 0
    
    # อัพเดตข้อมูลใน spreadsheet
    for row_data in rows_to_update:
        row_num = row_data["row"]
        data = row_data["data"]
        
        try:
            logger.print(f"[update_row] กำลังประมวลผลแถวที่ {row_num}, ข้อมูลปัจจุบัน: {len(data)} คอลัมน์")
            logger.print(f"[update_row] Indices: {indices}")
            
            # ส่งการแจ้งเตือนไปยัง API
            result = send_notification(data, indices)
            
            if result['success']:
                logger.print(f"[update_row] ส่งการแจ้งเตือนสำเร็จสำหรับแถวที่ {row_num}")
                
                # ตรวจสอบว่าต้องเพิ่มคอลัมน์ is Send Noti หรือไม่
                if indices['is_send_noti'] >= 0:  # ตรวจสอบว่า index ถูกต้อง
                    if len(data) <= indices['is_send_noti']:
                        logger.print(f"[update_row] เพิ่มคอลัมน์ is_send_noti ที่ index {indices['is_send_noti']}, ข้อมูลปัจจุบัน: {len(data)}")
                        # เพิ่มคอลัมน์ที่ว่างจนถึง is_send_noti_index
                        while len(data) < indices['is_send_noti']:
                            data.append("")
                        data.append("Done")
                    else:
                        logger.print(f"[update_row] อัพเดต is_send_noti ที่ index {indices['is_send_noti']}")
                        data[indices['is_send_noti']] = "Done"

                # update timestamp
                timestamp = datetime.now(thai_tz).strftime("%Y-%m-%d %H:%M:%S")
                if 'timestamp' in indices and indices['timestamp'] >= 0:  # ตรวจสอบว่า timestamp index ถูกต้อง
                    if len(data) <= indices['timestamp']:
                        logger.print(f"[update_row] เพิ่มคอลัมน์ timestamp ที่ index {indices['timestamp']}, ข้อมูลปัจจุบัน: {len(data)}")
                        # เพิ่มคอลัมน์ที่ว่างจนถึง timestamp
                        while len(data) < indices['timestamp']:
                            data.append("")
                        data.append(timestamp)
                    else:
                        logger.print(f"[update_row] อัพเดต timestamp ที่ index {indices['timestamp']}")
                        data[indices['timestamp']] = timestamp

                # อัพเดตข้อมูลใน spreadsheet
                logger.print(f"[update_row] กำลังอัพเดตข้อมูลในแถวที่ {row_num} - เปลี่ยน is Send Noti เป็น Done, ข้อมูลสุดท้าย: {len(data)} คอลัมน์")
                update_sheet_row(row_num, data)
                logger.print(f"[update_row] อัพเดตข้อมูลในแถวที่ {row_num} เรียบร้อยแล้ว")
                noti_success += 1
            else:
                land_no_value = "ไม่ระบุ"
                if indices['land_no'] != -1 and indices['land_no'] < len(data):
                    land_no_value = data[indices['land_no']]
                
                logger.print(f"[update_row] ส่งการแจ้งเตือนไม่สำเร็จสำหรับแปลง {land_no_value} (แถว {row_num})")
                logger.print(f"[update_row] Error: {result.get('error', 'Unknown error')}")
                logger.print("-" * 30)
                noti_failed += 1
                
                prettyErr = False
                # ดึงข้อความ error จาก response
                error_message = "Unknown error"
                error_detail = result.get('error', '')
                
                # ตรวจสอบว่า error เป็น JSON หรือไม่
                try:
                    if not prettyErr and isinstance(error_detail, str) and error_detail.startswith('{'):
                        err = json.loads(error_detail)
                        errStr = json.dumps(err, indent=4, ensure_ascii=False)
                        error_message = errStr
                    else:
                        if isinstance(error_detail, str):
                            error_json = json.loads(error_detail)
                            if 'message' in error_json:
                                error_message = error_json['message']
                            elif 'error' in error_json and 'detail' in error_json['error']:
                                error_message = error_json['error']['detail']
                        elif isinstance(error_detail, dict) and 'message' in error_detail:
                            error_message = error_detail['message']
                except json.JSONDecodeError:
                    # ถ้าไม่ใช่ JSON ให้ใช้ HTTP status code
                    error_message = f"HTTP Error: {result.get('status_code', 'Unknown')}"

                # เพิ่ม error message เป็นคอลัมน์สุดท้าย
                if 'error' in indices and indices['error'] >= 0:  # ตรวจสอบว่า error index ถูกต้อง
                    if len(data) <= indices['error']:
                        logger.print(f"[update_row] เพิ่มคอลัมน์ error ที่ index {indices['error']}, ข้อมูลปัจจุบัน: {len(data)}")
                        # เพิ่มคอลัมน์ที่ว่างจนถึง error
                        while len(data) < indices['error']:
                            data.append("")
                        data.append(error_message)
                    else:
                        logger.print(f"[update_row] อัพเดต error ที่ index {indices['error']}")
                        data[indices['error']] = error_message

                # อัพเดตข้อมูลใน spreadsheet พร้อม error message
                logger.print(f"[update_row] กำลังอัพเดตข้อมูลในแถวที่ {row_num} - เพิ่ม error message, ข้อมูลสุดท้าย: {len(data)} คอลัมน์")
                update_sheet_row(row_num, data)
                logger.print(f"[update_row] อัพเดตข้อมูลในแถวที่ {row_num} เรียบร้อยแล้ว")

        except Exception as update_error:
            logger.print(f"[update_row] Critical error ในการอัพเดตแถวที่ {row_num}: {str(update_error)}")
            logger.print(f"[update_row] Stack trace: {traceback.format_exc()}")
            logger.print(f"[update_row] Data length: {len(data)}, Indices: {indices}")
            noti_failed += 1

        # หน่วงเวลาเล็กน้อยเพื่อไม่ให้ยิง API ถี่เกินไป
        time.sleep(1)

    return noti_success, noti_failed, len(rows_to_update) > 0
