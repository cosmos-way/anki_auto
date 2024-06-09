import atexit
import json
import genanki
from flask import Flask, render_template, request, jsonify, send_from_directory, current_app
from flask_socketio import SocketIO, emit
import time
import threading
import os
import uuid
from . import anki
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta


socketio = SocketIO(current_app)


def main(data):
    deck_data = data

    # Получение идентификаторов модели и колоды
    model_id = 10 
    # 
    deck_id = 1123 
    # deck_data['deck_id']
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
    # print (qa_list)
    # Добавление карточек в колоду
    for qa in qa_list:
        question = qa['question']
        print('>>>>>',question)
        answer_html = qa['answer_html']
        # print(answer_html)
        
        note = genanki.Note(
            model=model,
            fields=[question, answer_html]
        )
        deck.add_note(note)
    # Сохранение колоды в файл
    # output_file = deck_data['title']+'.apkg'
    output_file = f"{uuid.uuid4()}.apkg"
    filepath = os.path.join(current_app.config['GENERATED_FILES'], output_file)
    print(filepath)


    genanki.Package(deck).write_to_file(filepath)
    print(f"Deck has been written to {filepath}")
    return filepath
    

def delete_old_files():
    now = datetime.now()
    for filename in os.listdir(current_app.config['GENERATED_FILES']):
        filepath = os.path.join(current_app.config['GENERATED_FILES'], filename)
        file_creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
        if now - file_creation_time > timedelta(minutes=1):
            try:
                os.remove(filepath)
                print(f"Deleted {filename}")
            except Exception as e:
                print(f"Error deleting file {filename}: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(func=delete_old_files, trigger="interval", minutes=1)
scheduler.start()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())