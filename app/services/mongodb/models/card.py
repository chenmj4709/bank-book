from datetime import datetime
from typing import Optional
from app.services.mongodb.models import MongoBaseModel

class Card(MongoBaseModel):
    """信用卡模型"""
    
    # 基本信息
    user_id: str  # 用户ID
    name: Optional[str] = None  # 信用卡名称
    bank: str  # 银行名称
    card_number: str  # 卡号（后四位）
    credit_limit: float  # 信用额度

    bill_day: int  # 账单日
    payment_day: int  # 还款日
    last_payment_day: int  # 最迟还款日
    
    # 可选信息
    color: Optional[str] = "#3B82F6"  # 卡片颜色
    description: Optional[str] = None  # 描述
    is_active: bool = True  # 是否激活
    
    class Config:
        collection = "cards"
        indexes = [
            "user_id",
            ("user_id", "bank"),
            ("user_id", "card_number"),
            ("user_id", "is_active")
        ]