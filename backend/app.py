import os
import mysql.connector
import re # 引入正則表達式用於驗證 email
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
    data = request.json
    
    # 1. 基本防護：確保必要欄位都存在且不為空
    required_fields = ['donor_name', 'contact_phone', 'email', 'recipient_id']
    if not all(field in data and str(data[field]).strip() for field in required_fields):
        return jsonify({"error": "請完整填寫所有欄位"}), 400

    # 2. 資料格式驗證：例如驗證 Email 格式（防止雜亂資料）
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, data['email']):
        return jsonify({"error": "Email 格式不正確"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # --- 安全的參數化查詢 (防止 SQL Injection) ---
        # 這裡我們傳入 (data['recipient_id'],) 而不是直接拼湊字串
        check_query = "SELECT is_taken_on FROM Recipient WHERE recipient_id = %s FOR UPDATE"
        cursor.execute(check_query, (data['recipient_id'],)) 
        recipient = cursor.fetchone()

        if not recipient:
            return jsonify({"error": "找不到該願望資料"}), 404
        if recipient['is_taken_on']:
            return jsonify({"message": "您目前選取的願望已經被領取，請重新認領其他願望。"}), 400

        # --- 執行寫入 ---
        insert_query = """
            INSERT INTO Donor (donor_name, contact_phone, email, recipient_id)
            VALUES (%s, %s, %s, %s)
        """
        # mysql-connector 會自動幫這些參數做轉義處理，惡意程式碼會被當成純文字儲存
        donor_values = (
            data['donor_name'], 
            data['contact_phone'], 
            data['email'], 
            data['recipient_id']
        )
        cursor.execute(insert_query, donor_values)
        
        # 更新狀態
        update_query = "UPDATE Recipient SET is_taken_on = TRUE WHERE recipient_id = %s"
        cursor.execute(update_query, (data['recipient_id'],))
        
        conn.commit() 
        return jsonify({"message": "認領成功！"}), 201

    except Exception as e:
        if conn: conn.rollback()
        # 注意：生產環境不要把詳細的 e 丟給前端，這裡為了調試先留著
        return jsonify({"error": "伺服器內部錯誤", "details": str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

# 3. 處理瀏覽人次 (GET 取得, POST 增加)
@app.route('/view-count', methods=['GET', 'POST'])
def handle_view_count():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            # 每次呼叫 POST，計數器就 +1
            update_query = "UPDATE SiteStats SET view_count = view_count + 1 WHERE id = 1"
            cursor.execute(update_query)
            conn.commit()
            return jsonify({"message": "Count incremented"}), 200
        else:
            # 呼叫 GET，回傳目前的數字
            cursor.execute("SELECT view_count FROM SiteStats WHERE id = 1")
            result = cursor.fetchone()
            return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "統計功能異常", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/')
def index():
    return "Python Backend 正在運行中..."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)