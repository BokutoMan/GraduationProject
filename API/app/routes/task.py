import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from API.app import db
from API.app.models.Task import Task, TaskStatus, TaskPriority
from API.app.models import DatabaseManager
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from utils.log import SimpleLogger

logger = SimpleLogger.get_new_logger(name="route", level=logging.INFO, log_file="log/route.log")
tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('/')
def index():
    # 初始化数据库管理器
    db_manager = DatabaseManager(db)
    try:
        # 高级搜索
        results = db_manager.search_tasks(
            # status=TaskStatus.BLOCKED,
            # priority=TaskPriority.HIGH,
            # keyword="项目",
            page=1,
            page_size=5
        )
        print(f"找到 {len(results)} 个相关任务")
        re = [task.to_dict() for task in results]
        return json.dumps(re)
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")

@tasks_bp.route('/add', methods=['POST'])
def add_task():
    task = request.get_json()
    task_ = Task.from_dict(task)
    db.session.add(task_)
    db.session.commit()
    return task

@tasks_bp.route('/delete', methods=['get'])
def delete_task():
    task_id = request.args.get('id')
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return {"code": 0 , "message" :f"Task {task_id} deleted successfully"}
    else:
        return {"code": 111 , "message" :f"Task {task_id} not found"}
    
@tasks_bp.route('/update', methods=['POST'])
def update_task():
    task = request.get_json()
    task_ = Task.query.get(task["id"])
    if task_:
        task_.update_from_dict(task)
    db.session.merge(task_)
    db.session.commit()
    return task_.to_dict()

def update_status(taskDict):
    if taskDict["status"] == TaskStatus.BLOCKED.value:
        taskDict["status"] = "BLOCKED"
    elif taskDict["status"] == TaskStatus.COMPLETED.value:
        taskDict["status"] = "COMPLETED"
    elif taskDict["status"] == TaskStatus.IN_PROGRESS.value:
        taskDict["status"] = "IN_PROGRESS"
    elif taskDict["status"] == TaskStatus.PENDING.value:
        taskDict["status"] = "PENDING"
    return taskDict

@tasks_bp.route('/search', methods=['POST'])
def search_task():
    search_json = request.get_json()
    status = search_json.get('status')
    priority = search_json.get('priority')
    keyword = search_json.get('keyword')
    due_before = search_json.get('due_before')
    page = search_json.get('page', 1)
    page_size = search_json.get('page_size', 20)
    try:
        query = Task.query
        if status is not None:
            query = query.filter(Task.status == status)
        if priority is not None:
            query = query.filter(Task.priority == priority)
        if keyword:
            query = query.filter(
                Task.title.ilike(f"%{keyword}%") |
                Task.description.ilike(f"%{keyword}%")
            )
        if due_before is not None:
            query = query.filter(Task.due_date < due_before)
        query = query.order_by(Task.priority.desc(), Task.due_date.asc())
        
        # 使用 offset 和 limit 实现分页
        offset = (page - 1) * page_size
        print(offset, page_size)
        paginated_query = query.offset(offset).limit(page_size)
        print(paginated_query)
        results = paginated_query.all()
        re = [task.to_dict() for task in results]
        re = [update_status(task) for task in re]
        response = {
            "code": 0,
            "message": "Success",
            "data": {
                "items": re,
                "total": len(re)
            }
        }
        return json.dumps(response)
    except SQLAlchemyError as e:
        logger.error(f"Failed to search tasks: {str(e)}")
        raise
