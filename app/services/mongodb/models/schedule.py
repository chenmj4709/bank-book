from datetime import datetime
from app.services.mongodb.models import MongoBaseModel

class Schedule(MongoBaseModel):
    """定时任务执行记录模型"""

    # 任务名称
    task_name: str
    
    # 执行时间
    executed_at: datetime = None

    class Config:
        collection = "schedules"
        indexes = [
            "task_name"
        ]
