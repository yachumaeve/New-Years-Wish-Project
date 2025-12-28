import os
import mysql.connector
from flask import Flask, jsonify, request # 新增 request 處理 POST 資料

app = Flask(__name__)

# 資料庫連線配置
db_config = {
    'host': os.getenv('DB_HOST', 'mysql-service'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    """封裝連線建立邏輯"""
    return mysql.connector.connect(**db_config)

# 1. 取得所有收件人資料 (Recipient)
@app.route('/recipients', methods=['GET'])
def get_recipients():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 撈取所有收件人資訊
        cursor.execute("SELECT * FROM Recipient")
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": "無法讀取收件人資料", "details": str(e)}), 500

# 2. 儲存捐贈者資料並更新認領狀態 (Donor)
@app.route('/donors', methods=['POST'])
def create_donor():
    data = request.json # 接收前端 JSON 資料
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 開始交易 (Transaction) 確保兩步驟同時成功
        # 步驟 A: 插入 Donor 資料
        insert_query = """
            INSERT INTO Donor (donor_name, contact_phone, email, recipient_id)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            data['donor_name'], 
            data['contact_phone'], 
            data['email'], 
            data['recipient_id']
        ))
        
        # 步驟 B: 將對應的 Recipient 狀態改為已認領 (True)
        update_query = "UPDATE Recipient SET is_taken_on = TRUE WHERE recipient_id = %s"
        cursor.execute(update_query, (data['recipient_id'],))
        
        conn.commit() # 確認提交變更
        
        cursor.close()
        conn.close()
        return jsonify({"message": "認領成功！"}), 201
    except Exception as e:
        if 'conn' in locals(): conn.rollback() # 失敗時回滾
        return jsonify({"error": "儲存失敗", "details": str(e)}), 500

@app.route('/')
def index():
    return "Python Backend 正在運行中..."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)