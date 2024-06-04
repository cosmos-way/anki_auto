from flask import Blueprint

notion = Blueprint('notion', __name__)

from . import routes