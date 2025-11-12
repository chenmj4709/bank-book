# 顶层导入与模型补充
from datetime import datetime
from typing import Optional, List
from pydantic import Field, BaseModel
from app.services.mongodb.models import MongoBaseModel

class RepaymentRef(BaseModel):
    repayment_id: str  # 关联还款记录ID
    amount: float      # 该还款分配金额

class Record(MongoBaseModel):
    """消费记录模型"""
    
    # 基本信息
    user_id: str  # 用户ID
    card_id: str  # 信用卡ID
    card_name: Optional[str] = None  # 信用卡名称
    card_bank: Optional[str] = None  # 信用卡银行名称
    card_number: Optional[str] = None  # 信用卡后四位
    swipe_type_id: Optional[str] = None  # 刷卡类型ID
    swipe_type_name: Optional[str] = None  # 刷卡类型名称
    consumption_type_id: Optional[str] = None  # 消费类型ID
    consumption_type_name: Optional[str] = None  # 消费类型名称
    
    # 消费详情
    amount: float  # 消费金额
    description: Optional[str] = None  # 消费描述
    
    # 时间信息
    trade_date: datetime = Field(default_factory=lambda: datetime.now().astimezone())  # 交易日期
    
    # 类型与状态（新增）
    record_type: str = "支付"  # 记录类型：支付/还款
    status: Optional[str] = None  # 状态：未还/已还/部分还（支付表示还款状态，还款表示分配状态）
    repayment_refs: List[RepaymentRef] = Field(default_factory=list)  # 支付记录的关联还款明细
    
    # 状态
    is_active: bool = True  # 是否有效
    
    class Config:
        collection = "records"
        indexes = [
            "user_id",
            "card_id",
            "swipe_type_id",
            "consumption_type_id",
            "trade_date",
            ("user_id", "trade_date"),
            ("user_id", "is_active"),
            # 新增索引，便于按类型/状态查询
            "record_type",
            "status",
            ("user_id", "record_type"),
            ("user_id", "status"),
        ]