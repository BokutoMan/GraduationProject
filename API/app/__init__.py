# app/__init__.py
from utils import failsafe

from flask import Flask
from flask_cors import CORS
from celery import Celery
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

@failsafe
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://yang:yang@127.0.0.1:3306/tasks_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭警告
    from API.config import Config
    app.config.from_object(Config)
    CORS(app)  # 允许所有域名访问

    # 注册蓝图
    db.init_app(app)
    from API.app.routes import home_bp, task_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(task_bp)

    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    
    # 将Celery对象挂载到app
    app.celery = celery

    return app
