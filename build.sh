#!/bin/bash

# สร้างโฟลเดอร์สำหรับเก็บไฟล์ที่จะอัพโหลด
mkdir -p build
mkdir -p build/package

# ติดตั้ง dependencies ใน build/package
python -m pip install -r requirements.txt --target build/package

# คัดลอกไฟล์ Python ไปยังโฟลเดอร์ build/package
cp *.py build/package/

# สร้างไฟล์ ZIP
cd build/package
zip -r ../lambda_function.zip .
cd ../..

echo "สร้างไฟล์ ZIP สำเร็จ: build/lambda_function.zip"
echo "คุณสามารถอัพโหลดไฟล์นี้ไปยัง AWS Lambda ได้"
