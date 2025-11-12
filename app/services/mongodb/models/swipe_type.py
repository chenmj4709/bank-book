from typing import Optional
from app.services.mongodb.models import MongoBaseModel

class SwipeType(MongoBaseModel):
    """刷卡类型模型"""
    
    user_id: str  # 用户ID（支持用户自定义分类）
    name: str  # 类型名称，如：线上支付、线下刷卡、取现等
    description: Optional[str] = None  # 描述
    is_active: bool = True  # 是否激活
    sort_order: int = 0  # 排序
    
    class Config:
        collection = "swipe_types"
        indexes = [
            "user_id",
            ("user_id", "name"),
            ("user_id", "is_active"),
            "sort_order"
        ]