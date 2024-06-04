from flask import jsonify, render_template, current_app, request
import notion_client

from app.notion.auth.routes import user_is_authenticated
from . import main
from flask import Blueprint, render_template
from app.notion.auth import models as notion_models

main_blueprint = Blueprint('main', __name__)

@main.route('/')
def index():
    token_record = notion_models.Token.query.order_by(notion_models.Token.id.desc()).first()
    if token_record:
        return render_template('index.html', token=token_record.token, auth=user_is_authenticated)
    else:
        return render_template('login.html')

    
@main.route("/export-anki", methods=["GET"])
def export_anki():
    # Проверяем авторизацию пользователя
    if not user_is_authenticated(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Получаем ID базы данных из параметров запроса
    database_id = request.args.get('database_id')
    if not database_id:
        return jsonify({"error": "No database ID provided"}), 400

    # Загружаем данные из базы данных Notion
    client = notion_client.Client(auth= current_app.config.get("NOTION_API_KEY"))
    results = client.databases.query(database_id=database_id)

    # Здесь код для создания Anki пакета
    # anki_package = create_anki_package(results)
    
    return jsonify({"anki_package": ""})