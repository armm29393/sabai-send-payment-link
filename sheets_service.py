# sheets_service.py
# ฟังก์ชันสำหรับการเชื่อมต่อกับ Google Sheets API

import os
import json
import boto3
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import SCOPES, SPREADSHEET_ID, SHEET_NAME

def get_credentials():
    """
    รับ credentials สำหรับ Google Sheets API
    สำหรับ AWS Lambda จะใช้ credentials จาก AWS Secrets Manager
    """
    try:
        # สำหรับ AWS Lambda ใช้ Secrets Manager
        if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            secret_name = "google_sheets_credentials"
            region_name = "ap-southeast-1"  # เปลี่ยนเป็นภูมิภาคที่คุณใช้
            
            # สร้าง client สำหรับ Secrets Manager
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=region_name
            )
            
            # รับค่า secret
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
            
            # แปลงค่า secret เป็น JSON
            secret = get_secret_value_response['SecretString']
            service_account_info = json.loads(secret)
            
            # สร้าง credentials จาก service account info
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES)
            
            return credentials
        else:
            # สำหรับการทดสอบในเครื่อง local
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json', scopes=SCOPES)
            return credentials
    except Exception as e:
        print(f"Error getting credentials: {e}")
        raise

def get_sheet_service():
    """สร้าง service สำหรับ Google Sheets API"""
    try:
        credentials = get_credentials()
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error creating sheet service: {e}")
        raise

def get_sheet_data():
    """รับข้อมูลจาก Google Sheets"""
    try:
        service = get_sheet_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID, 
            range=SHEET_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values:
            raise Exception("ไม่พบข้อมูลใน Google Sheet")
            
        return values
    except HttpError as err:
        print(f"Google API error: {err}")
        raise
    except Exception as e:
        print(f"Error getting sheet data: {e}")
        raise

def update_sheet_row(row_num, data):
    """อัพเดตข้อมูลใน Google Sheets"""
    import traceback
    try:
        # ใช้ print เพื่อให้ debug logs ยังคงแสดงใน console
        print(f"[update_sheet_row] กำลังอัพเดตแถวที่ {row_num}, จำนวนข้อมูล: {len(data)} คอลัมน์")
        print(f"[update_sheet_row] ข้อมูล: {data}")
        
        service = get_sheet_service()
        sheet = service.spreadsheets()
        
        # ตรวจสอบว่าข้อมูลไม่ว่าง
        if not data:
            raise Exception("ข้อมูลที่จะอัพเดตเป็นรายการว่าง")
        
        # คำนวณ range สำหรับการอัพเดต
        end_column = chr(65 + len(data) - 1)  # A=65, B=66, etc.
        update_range = f"{SHEET_NAME}!A{row_num}:{end_column}{row_num}"
        
        print(f"[update_sheet_row] Update range: {update_range}")
        
        body = {"values": [data]}
        
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=update_range,
            valueInputOption="RAW",
            body=body
        ).execute()
        
        print(f"[update_sheet_row] อัพเดตสำเร็จ: {result.get('updatedCells', 0)} เซลล์")
        return True
        
    except HttpError as err:
        print(f"[update_sheet_row] Google API error: {err}")
        print(f"[update_sheet_row] Stack trace: {traceback.format_exc()}")
        raise
    except Exception as e:
        print(f"[update_sheet_row] Error updating sheet: {e}")
        print(f"[update_sheet_row] Stack trace: {traceback.format_exc()}")
        print(f"[update_sheet_row] Row: {row_num}, Data length: {len(data) if data else 0}")
        raise
