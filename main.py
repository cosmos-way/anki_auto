import json
import genanki
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from html import unescape
import argparse

def markdown_to_html_with_syntax_highlighting(md_text):
    # Convert markdown to HTML
    html = markdown.markdown(md_text, extensions=['fenced_code'])

    # Unescape HTML entities
    html = unescape(html)

    formatter = HtmlFormatter(noclasses=True)  # Generate styles directly in the tags

    def highlight_code_block(match):
        language, code = match.groups()
        lexer = get_lexer_by_name(language, stripall=True)
        return highlight(code, lexer, formatter)

    import re
    # Use regex to find <code> blocks and add syntax highlighting
    pattern = re.compile(r'<code class="language-(\w+)">(.*?)</code>', re.DOTALL)
    html = pattern.sub(highlight_code_block, html)
    return html

def load_deck_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Create Anki deck from JSON file.')
    parser.add_argument('json_file', type=str, help='Path to the JSON file containing deck data')

    args = parser.parse_args()

    # Загрузка данных из JSON файла
    deck_data = load_deck_from_json(args.json_file)

    # Получение идентификаторов модели и колоды
    model_id = deck_data['model_id']
    deck_id = deck_data['deck_id']

    # Пример использования с genanki
    model = genanki.Model(
        model_id,
        'Simple Model with Syntax Highlighting',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ])

    deck = genanki.Deck(
        deck_id,
        deck_data['title'])

    # Загрузка вопросов и ответов из данных JSON
    qa_list = deck_data['cards']

    # Добавление карточек в колоду
    for qa in qa_list:
        question_md = qa['question']
        answer_md = qa['answer']
        question_html = markdown_to_html_with_syntax_highlighting(question_md)
        answer_html = markdown_to_html_with_syntax_highlighting(answer_md)
        
        note = genanki.Note(
            model=model,
            fields=[question_html, answer_html]
        )
        deck.add_note(note)

    # Сохранение колоды в файл
    output_file = deck_data['title']+'.apkg'
    genanki.Package(deck).write_to_file(output_file)
    print(f"Deck has been written to {output_file}")

if __name__ == '__main__':
    main()
