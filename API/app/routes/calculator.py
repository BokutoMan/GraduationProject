# app/auth/routes.py
from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth')  # 统一前缀 /auth

@bp.route('/login')
def login():
    return 'Login Page'

@bp.route('/logout')
def logout():
    return 'Logout'