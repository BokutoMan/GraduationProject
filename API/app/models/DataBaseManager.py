from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.exc import SQLAlchemyError
from utils import SimpleLogger
from sqlalchemy.orm import validates
import logging

from API.app import db
from API.app.models.Task import Task, TaskStatus, TaskPriority

logger = SimpleLogger.get_new_logger(name="DatabaseManager", level=logging.INFO, log_file="log/database_manager.log")


# 数据库管理类（适配 Flask-SQLAlchemy）
class DatabaseManager:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def add_task(self, task: Task) -> int:
        try:
            self.db.session.add(task)
            self.db.session.commit()
            return task.id
        except SQLAlchemyError as e:
            self.db.session.rollback()
            logger.error(f"Failed to add task: {str(e)}")
            raise

    def update_task(self, task: Task) -> bool:
        try:
            self.db.session.add(task)
            self.db.session.commit()
            return True
        except SQLAlchemyError as e:
            self.db.session.rollback()
            logger.error(f"Failed to update task: {str(e)}")
            raise

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        try:
            return Task.query.get(task_id)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get task by ID: {str(e)}")
            raise

    def search_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        keyword: Optional[str] = None,
        due_before: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Task]:
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
            paginated_query = query.offset(offset).limit(page_size)
            return paginated_query.all()
        except SQLAlchemyError as e:
            logger.error(f"Failed to search tasks: {str(e)}")
            raise

    def delete_task(self, task_id: int) -> bool:
        try:
            task = Task.query.get(task_id)
            if task:
                self.db.session.delete(task)
                self.db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete task: {str(e)}")
            raise

if __name__ == "__main__":
    # 初始化数据库表
    with app.app_context():
        db.create_all()
        
        # 初始化数据库管理器
        db_manager = DatabaseManager(db)
        
        try:
            # 创建新任务
            new_task = Task(
                title="项目需求分析",
                description="完成用户需求网页编写",
                status=TaskStatus.BLOCKED,
                priority=TaskPriority.HIGH,
                due_date=datetime(2030, 3, 25)
            )
            task_id = db_manager.add_task(new_task)
            
            # 查询任务
            task = db_manager.get_task_by_id(task_id)
            print(task.to_dict())
            
            # 高级搜索
            results = db_manager.search_tasks(
                # status=TaskStatus.BLOCKED,
                # priority=TaskPriority.HIGH,
                keyword="项目",
                page=1,
                page_size=5
            )
            print(f"找到 {len(results)} 个相关任务")
            
        except Exception as e:
            logger.error(f"Main execution failed: {str(e)}")