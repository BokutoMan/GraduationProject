import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from enum import Enum
from datetime import datetime
from typing import Any, Dict, Optional

from API.app import db


# 定义枚举类型（Flask-SQLAlchemy 支持的 Enum 方式）
class TaskStatus(Enum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    BLOCKED = 3

class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    URGENT = 3

# 定义数据模型（继承 db.Model）
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = db.Column(db.DateTime)
    custom_field = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 验证方法（保留原有逻辑）
    @validates('status')
    def validate_status(self, key, value):
        if not isinstance(value, TaskStatus):
            raise ValueError("Invalid task status")
        return value

    @validates('priority')
    def validate_priority(self, key, value):
        if not isinstance(value, TaskPriority):
            raise ValueError("Invalid task priority")
        return value

    # 转换为字典（保留原有逻辑）
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "custom_field": self.custom_field,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", 0)),
            priority=TaskPriority(data.get("priority", 1)),
            due_date=data.get("due_date"),
            custom_field=data.get("custom_field"),
        )
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        self.title = data.get("title", self.title)
        self.description = data.get("description", self.description)
        self.status = TaskStatus(data.get("status", self.status.value))
        self.priority = TaskPriority(data.get("priority", self.priority.value))
        self.due_date = data.get("due_date", self.due_date)
        self.custom_field = data.get("custom_field", self.custom_field)

# 创建表（在应用上下文中执行）
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()