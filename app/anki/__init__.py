from flask import Blueprint

anki = Blueprint('anki', __name__)

from . import routes