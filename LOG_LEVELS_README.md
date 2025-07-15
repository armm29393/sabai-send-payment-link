# Log Levels Implementation

ระบบได้รับการปรับปรุงให้มี log levels เพื่อควบคุมปริมาณ log ที่ส่งไป Discord

## การใช้งาน

### Normal Mode (Default)
```bash
# ส่ง request ปกติ
curl -X POST https://your-api-endpoint \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json"
```

### Verbose Mode
```bash
# เพิ่ม verbose header
curl -X POST https://your-api-endpoint \
  -H "x-api-key: your-api-key" \
  -H "verbose: true" \
  -H "Content-Type: application/json"

# หรือใช้ query parameter
curl -X POST "https://your-api-endpoint?verbose=true" \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json"
```

## Log Levels

### ERROR (🚨)
- **เมื่อไหร่**: เกิดข้อผิดพลาดที่สำคัญ
- **ส่งไป Discord**: ✅ เสมอ (ทั้ง normal และ verbose mode)
- **ตัวอย่าง**: การเชื่อมต่อ API ล้มเหลว, ข้อผิดพลาดในการอัพเดต Google Sheets

### INFO (ℹ️)
- **เมื่อไหร่**: ข้อมูลสำคัญและสรุปผลลัพธ์
- **ส่งไป Discord**: ✅ เสมอ (ทั้ง normal และ verbose mode)
- **ตัวอย่าง**: จำนวนการส่งโนติฯ ที่สำเร็จ, ข้อมูลลูกค้าที่ต้องส่งโนติฯ

### DEBUG (🔍)
- **เมื่อไหร่**: ข้อมูลละเอียดสำหรับ debugging
- **ส่งไป Discord**: ✅ เฉพาะ verbose mode เท่านั้น
- **ตัวอย่าง**: รายละเอียดการตรวจสอบแต่ละแถว, ข้อมูล payload ที่ส่งไป API

## การทดสอบ

รันไฟล์ทดสอบเพื่อดูความแตกต่างระหว่าง log levels:

```bash
python test_debug.py
```

ไฟล์นี้จะทดสอบ:
1. Logger ใน normal mode vs verbose mode
2. Lambda function ใน normal mode vs verbose mode
3. แสดงตัวอย่าง logs ที่จะส่งไป Discord ในแต่ละ mode

## ผลลัพธ์

### Normal Mode
- Discord จะได้รับเฉพาะ logs ที่สำคัญ (ERROR, INFO)
- ลดความยุ่งเหยิงใน Discord channel
- เหมาะสำหรับการใช้งานประจำ

### Verbose Mode  
- Discord จะได้รับ logs ทุกระดับ (ERROR, INFO, DEBUG)
- มีข้อมูลละเอียดสำหรับ debugging
- เหมาะสำหรับการแก้ไขปัญหา

## ตัวอย่าง Logs

### Normal Mode Discord Message:
```
**SABAI Payment Link Notification Log - 2025-01-15 21:45:00**

ℹ️ เริ่มประมวลผลข้อมูล จำนวนแถว: 150
ℹ️ พบแถวที่ 25 ต้องส่งโนติฯ
Land No: A-001
Customer Name: นาย ทดสอบ ระบบ
Phone: 0812345678
ℹ️ ------------------------------
ℹ️ พบแถวที่ต้องอัพเดต: 1 แถว
✅ ส่งการแจ้งเตือนสำเร็จสำหรับแถวที่ 25
ℹ️ ส่งโนติฯ Payment Link สำเร็จ 1 รายการ, ล้มเหลว 0 รายการ
```

### Verbose Mode Discord Message:
```
**SABAI Payment Link Notification Log - 2025-01-15 21:45:00**

🔧 Verbose mode เปิดใช้งาน - จะแสดง log ทุกรายละเอียด
ℹ️ เริ่มประมวลผลข้อมูล จำนวนแถว: 150
🔍 [process_sheet_data] Headers: ['Land No', 'Payment Link', 'Is Gen Payment Link', ...]
🔍 [process_sheet_data] Column indices: {'payment_link': 1, 'is_gen_payment_link': 2, ...}
🔍 กำลังตรวจสอบแถวที่ 2, จำนวนคอลัมน์: 8
🔍 ข้ามแถวที่ 2 เนื่องจากข้อมูลไม่ครบ
...
🔍 กำลังตรวจสอบแถวที่ 25, จำนวนคอลัมน์: 8
ℹ️ พบแถวที่ 25 ต้องส่งโนติฯ
Land No: A-001
Customer Name: นาย ทดสอบ ระบบ
Phone: 0812345678
ℹ️ ------------------------------
ℹ️ พบแถวที่ต้องอัพเดต: 1 แถว
🔍 กำลังประมวลผลแถวที่ 25, ข้อมูลปัจจุบัน: 8 คอลัมน์
🔍 Indices: {'payment_link': 1, 'is_gen_payment_link': 2, ...}
✅ ส่งการแจ้งเตือนสำเร็จสำหรับแถวที่ 25
🔍 อัพเดต is_send_noti ที่ index 3
🔍 อัพเดต timestamp ที่ index 6
🔍 กำลังอัพเดตข้อมูลในแถวที่ 25 - เปลี่ยน is Send Noti เป็น Done, ข้อมูลสุดท้าย: 8 คอลัมน์
🔍 อัพเดตข้อมูลในแถวที่ 25 เรียบร้อยแล้ว
ℹ️ ส่งโนติฯ Payment Link สำเร็จ 1 รายการ, ล้มเหลว 0 รายการ
```

## ตัวอย่างกรณี Error

### กรณี API Error 404 - User Not Found

เมื่อ API ส่ง error response กลับมา เช่น:
```json
{
  "success": false,
  "code": "2004", 
  "message": "user not found",
  "error": {
    "detail": "user not found",
    "name": "bad request error"
  }
}
```

### Normal Mode Discord Message (เมื่อเกิด Error):
```
**SABAI Payment Link Notification Log - 2025-01-15 21:45:00**

ℹ️ เริ่มประมวลผลข้อมูล จำนวนแถว: 150
ℹ️ พบแถวที่ 25 ต้องส่งโนติฯ
Land No: A-001
Customer Name: นาย ทดสอบ ระบบ
Phone: 0812345678
ℹ️ ------------------------------
ℹ️ พบแถวที่ต้องอัพเดต: 1 แถว
❌ ส่งการแจ้งเตือนไม่สำเร็จสำหรับแปลง A-001 (แถว 25)
❌ Error: {"success":false,"code":"2004","message":"user not found","error":{"detail":"user not found","name":"bad request error"}}
ℹ️ ส่งโนติฯ Payment Link สำเร็จ 0 รายการ, ล้มเหลว 1 รายการ
```

### Verbose Mode Discord Message (เมื่อเกิด Error):
```
**SABAI Payment Link Notification Log - 2025-01-15 21:45:00**

🔧 Verbose mode เปิดใช้งาน - จะแสดง log ทุกรายละเอียด
ℹ️ เริ่มประมวลผลข้อมูล จำนวนแถว: 150
🔍 [process_sheet_data] Headers: ['Land No', 'Payment Link', 'Is Gen Payment Link', ...]
🔍 [process_sheet_data] Column indices: {'payment_link': 1, 'is_gen_payment_link': 2, ...}
🔍 กำลังตรวจสอบแถวที่ 2, จำนวนคอลัมน์: 8
🔍 ข้ามแถวที่ 2 เนื่องจากข้อมูลไม่ครบ
...
🔍 กำลังตรวจสอบแถวที่ 25, จำนวนคอลัมน์: 8
ℹ️ พบแถวที่ 25 ต้องส่งโนติฯ
Land No: A-001
Customer Name: นาย ทดสอบ ระบบ
Phone: 0812345678
ℹ️ ------------------------------
ℹ️ พบแถวที่ต้องอัพเดต: 1 แถว
🔍 กำลังประมวลผลแถวที่ 25, ข้อมูลปัจจุบัน: 8 คอลัมน์
🔍 Indices: {'payment_link': 1, 'is_gen_payment_link': 2, ...}
❌ ส่งการแจ้งเตือนไม่สำเร็จสำหรับแปลง A-001 (แถว 25)
❌ Error: {"success":false,"code":"2004","message":"user not found","error":{"detail":"user not found","name":"bad request error"}}
🔍 เพิ่มคอลัมน์ error ที่ index 7, ข้อมูลปัจจุบัน: 8
🔍 กำลังอัพเดตข้อมูลในแถวที่ 25 - เพิ่ม error message, ข้อมูลสุดท้าย: 8 คอลัมน์
🔍 อัพเดตข้อมูลในแถวที่ 25 เรียบร้อยแล้ว
ℹ️ ส่งโนติฯ Payment Link สำเร็จ 0 รายการ, ล้มเหลว 1 รายการ
```

### การจัดการ Error:
1. **Error Logging**: ระบบจะ log error message ด้วย level ERROR (❌)
2. **Google Sheets Update**: Error message จะถูกบันทึกลงในคอลัมน์ "Error" ของ Google Sheets
3. **Discord Notification**: 
   - Normal Mode: แสดงเฉพาะ error message หลัก
   - Verbose Mode: แสดงรายละเอียดการอัพเดต Google Sheets ด้วย
4. **Developer Alert**: เมื่อมี error จะแท็ก developer Discord IDs เพิ่มเติม

## การ Deploy

ไม่ต้องเปลี่ยนแปลงการ deploy ใดๆ ระบบจะทำงานใน normal mode โดย default และสามารถเปิด verbose mode ได้ตามต้องการผ่าน request headers หรือ query parameters
