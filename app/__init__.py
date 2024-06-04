from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()
# migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    app.secret_key = os.urandom(24)  # Генерация случайного ключа для безопасного хранения данных сессии


    CORS(app)  # Включаем CORS для всего приложения 

    
    db.init_app(app)

    # migrate.init_app(app, db)
    with app.app_context():
        # from . import models  # Импорт моделей
        from .notion.auth import models
        db.create_all()

        from .main import main as main_blueprint
        from .notion.auth import auth as notion_auth_blueprint
        from .notion import notion as notion_blueprint

        app.register_blueprint(main_blueprint)
        app.register_blueprint(notion_auth_blueprint, url_prefix='/notion/auth')
        app.register_blueprint(notion_blueprint, url_prefix='/notion')

        return app
