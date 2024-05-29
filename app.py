from dotenv import load_dotenv
import notion_client
import random
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, redirect, request, session, url_for, jsonify, make_response, render_template
from requests_oauthlib import OAuth2Session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Генерация случайного ключа для безопасного хранения данных сессии

# Настройки OAuth
load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = os.getenv('REDIRECT_URI')
authorization_base_url = os.getenv('AUTHORIZATION_BASE_URL')
token_url = os.getenv('TOKEN_URL')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # Разрешаем использовать http для тестирования
NOTION_VERSION = "2022-06-28"

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
# DATABASE_ID = os.getenv('DATABASE_ID')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tokens.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
client = notion_client.Client(auth=NOTION_API_KEY)

# Модель для хранения токенов
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<Token {self.token}>'

# Создание таблиц в базе данных
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    token_record = Token.query.order_by(Token.id.desc()).first()
    if token_record:
        return render_template('index.html', token=token_record.token)
    else:
        return render_template('login.html')
    
@app.route('/login')
def login():
    notion = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=["databases.read"])
    authorization_url, state = notion.authorization_url(authorization_base_url)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    notion = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
    try:
        token = notion.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
        headers = {"Notion-Version": NOTION_VERSION}
        user_info = notion.get('https://api.notion.com/v1/users/me', headers=headers).json()

        # Отладочный вывод
        print('User info:', user_info)

        # Попробуем получить id пользователя из ответа
        user_id = user_info.get('id')

        # Если идентификатор пользователя не найден, вернуть ошибку
        if not user_id:
            return jsonify({"error": "User ID not found in the response", "details": user_info}), 400

        return set_token(token['access_token'], user_id)
    except Exception as e:
        return jsonify({"error": str(e)})

def set_token(access_token, user_id):
    new_token = Token(token=access_token, user_id=user_id)
    db.session.add(new_token)
    db.session.commit()
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('notion_access_token', access_token, httponly=True, secure=True)
    return resp

@app.route('/fetch_data')
def fetch_data():
    access_token = request.cookies.get('notion_access_token')
    if not access_token:
        return redirect(url_for('login'))

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Notion-Version": NOTION_VERSION
    }
    notion = OAuth2Session(client_id, token={'access_token': access_token})
    response = notion.get('https://api.notion.com/v1/databases/YOUR_DATABASE_ID/query', headers=headers)
    return jsonify(response.json())

@app.route("/export-anki", methods=["GET"])
def export_anki():
    # Проверяем авторизацию пользователя
    if not user_is_authenticated(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Получаем ID базы данных из параметров запроса
    database_id = request.args.get('database_id')
    if not database_id:
        return jsonify({"error": "No database ID provided"}), 400

    # Загружаем данные из базы данных Notion
    results = client.databases.query(database_id=database_id)

    # Здесь код для создания Anki пакета
    anki_package = create_anki_package(results)
    
    return jsonify({"anki_package": anki_package})

def create_anki_package(data):
    # Здесь логика преобразования данных Notion в формат Anki
    return "Пакет Anki создан"



### Функция для авторизации пользователя
def user_is_authenticated():
    token = request.headers.get('Authorization')
    if not token:
        return False
    # Проверяем токен в базе данных
    token_record = Token.query.filter_by(token=token).first()
    return token_record is not None

### Роут для демонстрации защищенного доступа
@app.route("/protected-resource", methods=["GET"])
def protected_resource():
    if not user_is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({"message": "This is protected data"})


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
