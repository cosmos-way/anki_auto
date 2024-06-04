from app import db
from datetime import datetime
    
# Модель для хранения токенов
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<Token {self.token}>'