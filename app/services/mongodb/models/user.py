from datetime import datetime
from typing import Optional
from app.services.mongodb.models import MongoBaseModel

class User(MongoBaseModel):
    """用户模型，用于与MongoDB交互"""

    # 基本信息
    name: Optional[str] = None # 用户名
    mobile: str
    password_hash: str
    salt: str

    last_login_date: Optional[datetime] = None # 最后登录时间
    last_logout_date: Optional[datetime] = None # 最后退出时间
    
    class Config:
        collection = "users"
        indexes = []