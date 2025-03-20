# app/auth/routes.py
from flask import Blueprint

bp = Blueprint('calculator', __name__, url_prefix='/auth')  # 统一前缀 /auth

@app.route('/status/<task_id>')
def get_status(task_id):
    status = task_status.get(task_id, {'error': 'Invalid task ID'})
    return jsonify({
        'status': status.get('status'),
        'progress': status.get('progress', 0),  # 新增进度字段
        'result': status.get('result')
    })

@bp.route('/logout')
def logout():
    return 'Logout'