from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import datetime
import uuid

app = Flask(__name__)

# Разрешаем доступ к API из любого источника
CORS(app)

# Путь к файлу, где хранятся письма
MAIL_FILE_PATH = "mails.json"

# Проверка наличия файла для хранения писем
def load_mails():
    try:
        with open(MAIL_FILE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_mails(mails):
    with open(MAIL_FILE_PATH, "w") as f:
        json.dump(mails, f, indent=4)

@app.route('/')
def index():
    return render_template_string(open("web.html").read())

@app.route('/mail/send', methods=['POST'])
def send_mail():
    try:
        data = request.json
        from_ = data['from']
        to = data['to']
        theme = data['theme']
        message = data['message']
        
        # Загружаем письма
        mails = load_mails()
        
        for from__ in mails:
            if from_ == from__:
                return jsonify({"status": "ERROR", "message": "This email is already in use"})
        
        # Генерируем уникальный ID для нового письма
        message_id = str(uuid.uuid4())
        
        # Добавляем новое письмо с нормальным временем и уникальным ID
        mails.append({
            "id": message_id,
            "from": from_, 
            "to": to, 
            "theme": theme, 
            "message": message, 
            "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Сохраняем обновленный список писем
        save_mails(mails)
        
        return jsonify({"status": "OK", "id": message_id})
    
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 400

@app.route('/mail/get', methods=['POST'])
def get_mail():
    try:
        to = request.json['to']
        
        # Загружаем все письма
        mails = load_mails()
        
        result = {}
        
        # Фильтруем письма для конкретного получателя
        for mail in mails:
            if mail['to'] == to:
                result[mail['id']] = {
                    "from": mail['from'],
                    "message": mail['message'], 
                    "time": mail['time'], 
                    "theme": mail['theme']
                }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 400

@app.route('/mail/delete', methods=['POST'])
def delete_mail():
    try:
        data = request.json
        message_id = data['id']
        
        # Загружаем все письма
        mails = load_mails()
        
        # Убираем письмо по уникальному ID
        mails = [mail for mail in mails if mail['id'] != message_id]
        
        # Сохраняем обновленный список писем
        save_mails(mails)
        
        return jsonify({"status": "OK"})
    
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)