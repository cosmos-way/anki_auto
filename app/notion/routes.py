from html import unescape
from flask import jsonify, make_response, request, current_app
import markdown
import requests
from requests_oauthlib import OAuth2Session
from . import notion
import markdown2
from app import db
# import HtmlFormatter

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
        md_content = response.text
        html_content = markdown2.markdown(md_content)

        html = markdown.markdown(md_content, extensions=['fenced_code'])

        # Unescape HTML entities
        html = unescape(html)

        formatter = HtmlFormatter(noclasses=True)  # Generate styles directly in the tags
        # def highlight_code_block(match):
        #     language, code = match.groups()
        #     lexer = get_lexer_by_name(language, stripall=True)
        #     return highlight(code, lexer, formatter)

        import re
        # Use regex to find <code> blocks and add syntax highlighting
        pattern = re.compile(r'<code class="language-(\w+)">(.*?)</code>', re.DOTALL)
        # html = pattern.sub(highlight_code_block, html)

        return jsonify({"markdown": md_content, "html":html_content})
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