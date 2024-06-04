from flask import render_template, redirect, url_for, make_response, current_app, jsonify, make_response, session, request
from . import auth, models
from requests_oauthlib import OAuth2Session
from app import db
import datetime

@auth.route('/login')
def login():
    notion = OAuth2Session(current_app.config.get('CLIENT_ID'), redirect_uri=current_app.config.get('REDIRECT_URI'), scope=["databases.read"])
    authorization_url, state = notion.authorization_url(current_app.config.get('AUTHORIZATION_BASE_URL'))
    session['oauth_state'] = state
    return redirect(authorization_url)

@auth.route('/callback')
def callback():
    notion = OAuth2Session(current_app.config.get('CLIENT_ID'), state=session['oauth_state'], redirect_uri=current_app.config.get('REDIRECT_URI'))
    try:
        token = notion.fetch_token(current_app.config.get('TOKEN_URL'), client_secret=current_app.config.get('CLIENT_SECRET'), authorization_response=request.url)
        print('token:', token)

        user_info = notion.get('https://api.notion.com/v1/users/me', headers={"Notion-Version": "2022-06-28"}).json()

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
    
@auth.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('notion_access_token')
    return resp

@auth.route('/check_token')
def check_token():
    access_token = request.cookies.get('notion_access_token')
    if not access_token:
        return jsonify({"valid": False})

    notion = OAuth2Session(current_app.config.get('CLIENT_ID'), token={'access_token': access_token})
    try:
        response = notion.get('https://api.notion.com/v1/users/me', headers={"Notion-Version": "2022-06-28"})
        response.raise_for_status()
        return jsonify({"valid": True})
    except Exception as e:
        # Удаляем токен из базы данных и куки при ошибке запроса или токена
        token_record = models.Token.query.filter_by(token=access_token).first()
        if token_record:
            db.session.delete(token_record)
            db.session.commit()
        resp = make_response(jsonify({"valid": False}))
        resp.delete_cookie('notion_access_token')
        return resp
    
@auth.route('/delete_all')
def delete_all():
    models.Token.query.delete()
    db.session.commit()
    return "All records deleted"

def set_token(access_token, user_id):
    existing_token = models.Token.query.filter_by(user_id=user_id).first()
    if existing_token:
        existing_token.token = access_token
        existing_token.created_at = datetime.utcnow()
    else:
        new_token = models.Token(token=access_token, user_id=user_id)
        db.session.add(new_token)
    db.session.commit()
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('notion_access_token', access_token, httponly=True, secure=False)
    return resp

### Функция для авторизации пользователя
def user_is_authenticated():
    access_token = request.cookies.get('notion_access_token')
    if not access_token:
        return False

    notion = OAuth2Session(current_app.config.get('CLIENT_ID'), token={'access_token': access_token})
    try:
        response = notion.get('https://api.notion.com/v1/users/me', headers={"Notion-Version": "2022-06-28"})
        response.raise_for_status()
        return True
    except Exception as e:
        # Удаляем токен из базы данных и куки при ошибке запроса или токена
        token_record = models.Token.query.filter_by(token=access_token).first()
        if token_record:
            db.session.delete(token_record)
            db.session.commit()
        resp = make_response(jsonify({"valid": False}))
        resp.delete_cookie('notion_access_token')
        return False