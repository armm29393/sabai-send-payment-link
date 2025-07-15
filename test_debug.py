#!/usr/bin/env python3
# test_debug.py
# ไฟล์สำหรับทดสอบและ debug ระบบ พร้อม log levels

import json
import traceback
from lambda_function import lambda_handler

def test_lambda_function(verbose=False):
    """ทดสอบฟังก์ชัน lambda_handler พร้อม error handling ที่ดีขึ้น"""
    
    # สร้าง mock event สำหรับการทดสอบ
    test_event = {
        "headers": {
            "x-api-key": "c8d01abc-7b86-48f4-892e-b83d9f3b7e99"  # ใส่ API key ที่ถูกต้อง
        }
    }
    
    # เพิ่ม verbose header ถ้าต้องการ
    if verbose:
        test_event["headers"]["verbose"] = "true"
    
    test_context = None
    
    mode_text = "VERBOSE MODE" if verbose else "NORMAL MODE"
    print("=" * 50)
    print(f"เริ่มการทดสอบ Lambda Function ({mode_text})")
    print("=" * 50)
    
    try:
        # เรียกใช้ฟังก์ชัน lambda_handler
        result = lambda_handler(test_event, test_context)
        
        print("\n" + "=" * 50)
        print("ผลลัพธ์การทดสอบ:")
        print("=" * 50)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print("\n" + "🚨" * 20)
        print("เกิดข้อผิดพลาดในการทดสอบ:")
        print("🚨" * 20)
        print(f"Error: {str(e)}")
        print(f"Error Type: {type(e).__name__}")
        print("\nStack Trace:")
        print(traceback.format_exc())
        print("🚨" * 20)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'Test failed: {str(e)}',
                'error_type': type(e).__name__,
                'stack_trace': traceback.format_exc()
            })
        }

def test_individual_functions():
    """ทดสอบฟังก์ชันแต่ละส่วนแยกกัน"""
    
    print("\n" + "=" * 50)
    print("ทดสอบฟังก์ชันแต่ละส่วน")
    print("=" * 50)
    
    # ทดสอบการโหลด config
    try:
        from config import validate_config
        print("✅ โหลด config สำเร็จ")
        validate_config()
        print("✅ validate_config สำเร็จ")
    except Exception as e:
        print(f"❌ Error ใน config: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
    
    # ทดสอบการเชื่อมต่อ Google Sheets
    try:
        from sheets_service import get_sheet_data
        print("✅ โหลด sheets_service สำเร็จ")
        
        # ลองดึงข้อมูลจาก Google Sheets
        values = get_sheet_data()
        print(f"✅ ดึงข้อมูลจาก Google Sheets สำเร็จ: {len(values)} แถว")
        
        if len(values) > 0:
            print(f"Headers: {values[0]}")
            print(f"จำนวนคอลัมน์: {len(values[0])}")
            
            # แสดงตัวอย่างข้อมูลแถวแรก (ถ้ามี)
            if len(values) > 1:
                print(f"ตัวอย่างข้อมูลแถวที่ 2: {values[1]}")
                print(f"จำนวนคอลัมน์ในแถวที่ 2: {len(values[1])}")
        
    except Exception as e:
        print(f"❌ Error ใน sheets_service: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
    
    # ทดสอบ data processor
    try:
        from data_processor import find_column_indices
        print("✅ โหลด data_processor สำเร็จ")
        
        # ทดสอบ find_column_indices ด้วยข้อมูลตัวอย่าง
        sample_headers = ["Land No", "Payment Link", "Is Gen Payment Link", "Is Send Noti", "Phone", "Email", "Timestamp", "Error"]
        indices = find_column_indices(sample_headers)
        print(f"✅ find_column_indices สำเร็จ: {indices}")
        
    except Exception as e:
        print(f"❌ Error ใน data_processor: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
    
    # ทดสอบ logger
    try:
        from logger import Logger
        print("✅ โหลด logger สำเร็จ")
        
        # ทดสอบ normal mode
        test_logger_normal = Logger(verbose=False)
        test_logger_normal.info("ทดสอบ info log")
        test_logger_normal.debug("ทดสอบ debug log (ไม่ควรแสดงใน normal mode)")
        test_logger_normal.error("ทดสอบ error log")
        
        print("✅ สร้าง logger instance (normal mode) สำเร็จ")
        print("Normal mode logs:")
        print(test_logger_normal.get_log_text())
        
        # ทดสอบ verbose mode
        test_logger_verbose = Logger(verbose=True)
        test_logger_verbose.info("ทดสอบ info log")
        test_logger_verbose.debug("ทดสอบ debug log (ควรแสดงใน verbose mode)")
        test_logger_verbose.error("ทดสอบ error log")
        
        print("\n✅ สร้าง logger instance (verbose mode) สำเร็จ")
        print("Verbose mode logs:")
        print(test_logger_verbose.get_log_text())
        
    except Exception as e:
        print(f"❌ Error ใน logger: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")

def test_log_levels():
    """ทดสอบ log levels โดยเฉพาะ"""
    
    print("\n" + "=" * 50)
    print("ทดสอบ Log Levels")
    print("=" * 50)
    
    from logger import Logger
    
    print("🔍 ทดสอบ Normal Mode (ไม่แสดง DEBUG logs):")
    print("-" * 30)
    normal_logger = Logger(verbose=False)
    normal_logger.error("Error message - ควรแสดง")
    normal_logger.info("Info message - ควรแสดง")
    normal_logger.debug("Debug message - ไม่ควรแสดง")
    
    print("Logs ที่จะส่งไป Discord (Normal Mode):")
    print(normal_logger.get_log_text())
    
    print("\n🔍 ทดสอบ Verbose Mode (แสดงทุก logs):")
    print("-" * 30)
    verbose_logger = Logger(verbose=True)
    verbose_logger.error("Error message - ควรแสดง")
    verbose_logger.info("Info message - ควรแสดง")
    verbose_logger.debug("Debug message - ควรแสดง")
    
    print("Logs ที่จะส่งไป Discord (Verbose Mode):")
    print(verbose_logger.get_log_text())

if __name__ == "__main__":
    print("🔧 เริ่มการทดสอบและ Debug พร้อม Log Levels")
    print("=" * 60)
    
    # ทดสอบ log levels
    test_log_levels()
    
    # ทดสอบฟังก์ชันแต่ละส่วนก่อน
    test_individual_functions()
    
    # ทดสอบฟังก์ชันหลักใน normal mode
    print("\n" + "🧪" * 20)
    print("ทดสอบ NORMAL MODE")
    print("🧪" * 20)
    test_lambda_function(verbose=False)
    
    # ทดสอบฟังก์ชันหลักใน verbose mode
    print("\n" + "🧪" * 20)
    print("ทดสอบ VERBOSE MODE")
    print("🧪" * 20)
    test_lambda_function(verbose=True)
    
    print("\n" + "=" * 60)
    print("🏁 การทดสอบเสร็จสิ้น")
    print("=" * 60)
    
    print("\n📋 สรุปการใช้งาน:")
    print("- Normal request: ไม่ต้องส่ง verbose parameter")
    print("- Verbose request: เพิ่ม header 'verbose: true' หรือ query parameter '?verbose=true'")
    print("- Normal mode จะส่งเฉพาะ ERROR และ INFO logs ไป Discord")
    print("- Verbose mode จะส่งทุก logs (ERROR, INFO, DEBUG) ไป Discord")
