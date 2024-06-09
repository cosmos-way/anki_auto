from html import unescape
from flask import jsonify, make_response, request, current_app
import markdown
import requests
from requests_oauthlib import OAuth2Session
from . import notion
import markdown2
from app import db
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from html import unescape
from bs4 import BeautifulSoup
from flask_socketio import SocketIO, emit
import time
from app.anki import pkg as Anki

socketio = SocketIO(current_app)

@notion.route('/fetch_rows', methods=['POST'])
def fetch_rows():
    access_token = request.cookies.get('notion_access_token')
    if not access_token:
        return jsonify({"error": "Not authorized"}), 401

    notion = OAuth2Session(current_app.config.get("CLIENT_ID"), token={'access_token': access_token})
    database_id = request.json.get('database_id')
    if not database_id:
        return jsonify({"error": "Database ID is required"}), 400

    try:
        response = notion.post(f'https://api.notion.com/v1/databases/{database_id}/query', headers={"Notion-Version": "2022-06-28"})
        response.raise_for_status()
        data = response.json()

        # Проверка наличия информации на страницах
        for row in data['results']:
            page_id = row['id']
            page_response = notion.get(f'https://api.notion.com/v1/pages/{page_id}', headers={"Notion-Version": "2022-06-28"})
            page_data = page_response.json()
            row['is_empty'] = not any(page_data['properties'][prop]['id'] for prop in page_data['properties'])

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@notion.route('/fetch_page', methods=['POST'])
def fetch_page():
    access_token = request.cookies.get('notion_access_token')
    if not access_token:
        return jsonify({"error": "Not authorized"}), 401

    notion = OAuth2Session(current_app.config.get("CLIENT_ID"), token={'access_token': access_token})
    page_id = request.json.get('page_id')
    if not page_id:
        return jsonify({"error": "Page ID is required"}), 400

    try:
        response = notion.get(f'https://api.notion.com/v1/pages/{page_id}', headers={"Notion-Version": "2022-06-28"})
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@notion.route('/convert_page', methods=['POST'])
def convert_page():
    page_id = request.json.get('page_id')
    access_token = request.cookies.get('notion_access_token')
    if not page_id:
        return jsonify({"error": "Page ID is required"}), 400

    try:
        response = requests.post('http://localhost:3000/convert', json={"pageId": page_id, "token": access_token})
        response.raise_for_status()
        print(response.json())
        md_content = response.json().get('pageHtml')
        html = markdown.markdown(md_content, extensions=['fenced_code'])
        # Unescape HTML entities
        html = unescape(html)
        output_html = highlight_code(html)

        return jsonify({ "html":output_html})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@notion.route('/fetch_data', methods=['POST'])
def fetch_data():
    access_token = request.cookies.get('notion_access_token')
    if not access_token:
        return jsonify({"error": "Not authorized"}), 401

    notion = OAuth2Session(current_app.config.get("CLIENT_ID"), token={'access_token': access_token})
    try:
        headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Notion-Version": current_app.config.get("NOTION_VERSION")
        }
        database_id = request.json.get('database_id')
        if not database_id:
            return jsonify({"error": "Database ID is required"}), 400
        response = notion.get(f'https://api.notion.com/v1/databases/{database_id}', headers=headers)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except Exception as e:
        # Удаляем токен из базы данных и куки при ошибке запроса или токена
        # token_record = Token.query.filter_by(token=access_token).first()
        # if token_record:
        #     db.session.delete(token_record)
        #     db.session.commit()
        resp = make_response(jsonify({"error": "Token invalid or expired"}), 401)
        # resp.delete_cookie('notion_access_token')
        print(e)
        return resp
    
@notion.route('/fetch_block_children', methods=['POST'])
def fetch_block_children():
    access_token = request.cookies.get('notion_access_token')
    if not access_token:
        return jsonify({"error": "Not authorized"}), 401

    notion = OAuth2Session(current_app.config.get("CLIENT_ID"), token={'access_token': access_token})
    block_id = request.json.get('block_id')
    if not block_id:
        return jsonify({"error": "Block ID is required"}), 400

    try:
        response = notion.get(f'https://api.notion.com/v1/blocks/{block_id}/children', headers={"Notion-Version": "2022-06-28"})
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@notion.route('/fetch_block', methods=['POST'])
def fetch_block():
    access_token = request.cookies.get('notion_access_token')
    if not access_token:
        return jsonify({"error": "Not authorized"}), 401

    notion = OAuth2Session(current_app.config.get("CLIENT_ID"), token={'access_token': access_token})
    block_id = request.json.get('block_id')
    if not block_id:
        return jsonify({"error": "Block ID is required"}), 400

    try:
        response = notion.get(f'https://api.notion.com/v1/blocks/{block_id}', headers={"Notion-Version": "2022-06-28"})
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
def highlight_code(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    formatter = HtmlFormatter(noclasses=True)  # Используем встроенные стили

    # Обрабатываем каждый тег <code>
    for code in soup.find_all('code'):
        # Определяем язык программирования из атрибута class (например, class="language-python")
        if 'class' in code.attrs:
            class_names = code['class']
            for class_name in class_names:
                if class_name.startswith('language-'):
                    language = class_name[len('language-'):]
                    break
            else:
                continue
        else:
            continue

        # Получаем код из тега
        code_text = code.get_text()
        
        # Получаем лексер для нужного языка
        lexer = get_lexer_by_name(language)
        
        # Форматируем код с подсветкой
        highlighted_code = highlight(code_text, lexer, formatter)
        
        # Извлекаем только содержимое внутри <pre><code>...</code></pre>
        highlighted_code_soup = BeautifulSoup(highlighted_code, 'html.parser')
        new_code = highlighted_code_soup.find('div')
        
        # Замена оригинального тега <code> на подсвеченный
        code.replace_with(new_code)

    return str(soup)

@notion.route('/fetch_all_database_pages', methods=['POST'])
def fetch_all_database_pages():
    access_token = request.cookies.get('notion_access_token')
    if not access_token:
        return jsonify({"error": "Not authorized"}), 401
    
    try:
        database_id = request.json.get('database_id')
        if not database_id:
            return jsonify({"error": "Database ID is required"}), 400
        pages = get_list_of_all_pages_in_db(access_token, database_id)
        result = getAllPages(pages)

        return jsonify(result)
    except Exception as e:
        resp = make_response(jsonify({"error": "Token invalid or expired"}), 401)
        print(e)
        return resp
    
@notion.route('/getAnki', methods=['POST'])
def fetch_all_database_pages_anki():
    access_token = request.cookies.get('notion_access_token')
    if not access_token:
        return jsonify({"error": "Not authorized"}), 401
    
    try:
        database_id = request.json.get('database_id')
        if not database_id:
            return jsonify({"error": "Database ID is required"}), 400
        (pages, database_name) = get_list_of_all_pages_in_db(access_token, database_id)
        result = getAllPages(pages)
        result['model_id']=database_id
        result['deck_id']=database_id
        result['title']=database_name
        file = generate_anki_package(result)

        return jsonify(file)
    except Exception as e:
        resp = make_response(jsonify({"error": "Token invalid or expired"}), 401)
        print(e)
        return resp

def getAllPages(pages):
    access_token = request.cookies.get('notion_access_token')
       
    result = []
    N = len(pages)
    i=0
    for page in pages:
        page_id = page['id']
        print(page_id)
        i=i+1
        try:
            converterResponse = requests.post('http://localhost:3000/convert', json={"pageId": page_id, "token": access_token})
            converterResponse.raise_for_status()
            print(converterResponse)
            md_content = converterResponse.json().get('pageHtml')
            html = markdown.markdown(md_content, extensions=['fenced_code'])
            # Unescape HTML entities
            html = unescape(html)
            output_html = highlight_code(html)

            print(converterResponse.json().get('question'))
            print(converterResponse.json().get('answer'))
            
            
            result.append({
                'id': page_id,
                'question': converterResponse.json().get('question'),
                'answer': converterResponse.json().get('answer'),
                'answer_html' : output_html
            })
            progress = (i / N) * 100
            
            socketio.emit('progress', {'progress': progress})
        except Exception as e:
            progress = (i / N) * 100
            socketio.emit('progress', {'progress': progress})
            print(e)
    
    data = {'cards':result};
    return data

def get_list_of_all_pages_in_db(access_token, database_id):
    if not access_token:
        return jsonify({"error": "Not authorized"}), 401
    
    notion = OAuth2Session(current_app.config.get("CLIENT_ID"), token={'access_token': access_token})
    try:
        headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Notion-Version": current_app.config.get("NOTION_VERSION")
        }
        if not database_id:
            return []
        response = notion.post(f'https://api.notion.com/v1/databases/{database_id}/query', headers=headers)
        response.raise_for_status()
        data = response.json()
        pages = data.get('results', [])
        
        return (pages, '')
    except Exception as e:
        return ([], '')

def generate_anki_package(json):
    file = Anki.main(json)
    # socketio.emit('complete', {'task_id': task_id, 'status': 'Task completed!', 'file_url': f'/download/{filename}'})
    return file

#1. Запрос БД
#2. запрос всех страниц 
#3. В цикле кажду страницу отрисовываем и сохраняем в JSON.
#4. После формирования генерируем Anki package