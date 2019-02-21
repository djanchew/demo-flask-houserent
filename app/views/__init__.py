from flask import Blueprint

view = Blueprint('view', __name__)

from app.views import index
from app.views import login
