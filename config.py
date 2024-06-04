from dotenv import load_dotenv
import os

class Config:
    load_dotenv()
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REDIRECT_URI = os.getenv('REDIRECT_URI')
    AUTHORIZATION_BASE_URL = os.getenv('AUTHORIZATION_BASE_URL')
    TOKEN_URL = os.getenv('TOKEN_URL')
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # Разрешаем использовать http для тестирования
    NOTION_VERSION = "2022-06-28"
    NOTION_API_KEY = os.getenv('NOTION_API_KEY')
    CORS_HEADERS = 'Content-Type'