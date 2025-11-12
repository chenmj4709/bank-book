from typing import Optional
from app.services.mongodb.models import MongoBaseModel

class ConsumptionType(MongoBaseModel):
    """消费类型模型"""
    
    user_id: str  # 用户ID（支持用户自定义分类）
    name: str  # 类型名称，如：餐饮、购物、交通等
    icon: Optional[str] = None  # 图标
    color: Optional[str] = "#3B82F6"  # 颜色
    description: Optional[str] = None  # 描述
    is_active: bool = True  # 是否激活
    sort_order: int = 0  # 排序
    
    class Config:
        collection = "consumption_types"
        indexes = [
            "user_id",
            ("user_id", "name"),
            ("user_id", "is_active"),
            "sort_order"
        ]