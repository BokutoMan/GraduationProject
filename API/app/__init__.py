# app/__init__.py
from flask import Flask
from flask_cors import CORS

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://yang:yang@127.0.0.1:3306/tasks_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭警告
    CORS(app)  # 允许所有域名访问

    # 注册蓝图
    db.init_app(app)
    from API.app.routes import home_bp, task_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(task_bp)

    return app
