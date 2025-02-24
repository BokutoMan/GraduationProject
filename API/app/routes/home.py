# app/routes/home.py
from flask import Blueprint

bp = Blueprint('home', __name__, url_prefix='/home')  # 统一前缀 /home

@bp.route('/index')
def index():
    return 'Login Page'
