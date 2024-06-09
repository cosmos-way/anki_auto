from flask import Flask, render_template, request, jsonify, send_from_directory, current_app
from flask_socketio import SocketIO, emit
import time
import threading
import os
import uuid
from . import anki

current_app.config['GENERATED_FILES'] = 'generated_files'
socketio = SocketIO(current_app)

if not os.path.exists(current_app.config['GENERATED_FILES']):
    os.makedirs(current_app.config['GENERATED_FILES'])

@anki.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(current_app.config['GENERATED_FILES'], filename)