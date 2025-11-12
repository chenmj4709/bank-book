from typing import Dict, Any, List
from fastapi import APIRouter, Request, Body, Depends, Query
from app.middlewares.inject import auth_user
from app.services.mongodb.models.card import Card
from app.utils import get_logger, handle_error, dict_to_sort_list
from app.define import ErrorCode

logger = get_logger()

router = APIRouter()

@router.get("/card/list")
async def get_cards(
    user_id: str = Depends(auth_user),
    sort: str = Query(f"{{'bill_day': 1, 'created_at': -1}}", description="排序字段"),
    is_active: bool = Query(True, description="是否只获取激活的卡片")
):
    """获取用户的信用卡列表"""
    try:
        # sort 转换为字典
        sort = eval(sort)
        filter_dict = {"user_id": user_id}
        if is_active is not None:
            filter_dict["is_active"] = is_active
            
        cards = await Card.find_many(
            filter=filter_dict,
            sort=dict_to_sort_list(sort)
        )
        
        return cards
    except Exception as e:
        logger.error(f"获取信用卡列表失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "获取信用卡列表失败")

@router.post("/card/add")
async def add_card(
    user_id: str = Depends(auth_user),
    body: Dict[str, Any] = Body(...)
):
    """添加信用卡"""
    try:
        name = body.get("name")
        bank = body.get("bank")
        card_number = body.get("card_number")
        credit_limit = body.get("credit_limit")
        bill_day = body.get("bill_day")
        payment_day = body.get("payment_day")
        last_payment_day = body.get("last_payment_day")
        
        if not all([bank, card_number, credit_limit, bill_day, payment_day, last_payment_day]):
            return handle_error(ErrorCode.INVALID_PARAMS, "缺少必要参数")
        
        # 检查是否已存在同名卡片
        existing_card = await Card.find_one({
            "user_id": user_id,
            "bank": bank,
            "card_number": card_number,
            "is_active": True
        })
        
        if existing_card:
            return handle_error(ErrorCode.INVALID_PARAMS, "已存在同名信用卡")
        
        # 创建新卡片
        card = Card(
            user_id=user_id,
            name=name,
            bank=bank,
            card_number=card_number,
            credit_limit=float(credit_limit),
            bill_day=bill_day,
            payment_day=payment_day,
            last_payment_day=last_payment_day,
            color=body.get("color", "#3B82F6"),
            description=body.get("description")
        )
        
        await card.save()
        return card
        
    except Exception as e:
        logger.error(f"添加信用卡失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "添加信用卡失败")

@router.put("/card/update/{card_id}")
async def update_card(
    card_id: str,
    user_id: str = Depends(auth_user),
    body: Dict[str, Any] = Body(...)
):
    """更新信用卡信息"""
    try:
        # 查找卡片
        card = await Card.find_one({
            "_id": card_id,
            "user_id": user_id
        })
        
        if not card:
            return handle_error(ErrorCode.INVALID_PARAMS, "信用卡不存在")
        
        # 更新字段
        update_fields = {}
        for field in ["name", "bank", "card_number", "credit_limit", "bill_day", "payment_day", "last_payment_day", "color", "description", "is_active"]:
            if field in body:
                if field == "credit_limit":
                    update_fields[field] = float(body[field])
                else:
                    update_fields[field] = body[field]
        
        if update_fields:
            updated_card = await Card.find_one_and_update(
                {"_id": card_id, "user_id": user_id},
                {"$set": update_fields}
            )
            return updated_card
        
        return card
        
    except Exception as e:
        logger.error(f"更新信用卡失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "更新信用卡失败")

@router.delete("/card/delete/{card_id}")
async def delete_card(
    card_id: str,
    user_id: str = Depends(auth_user)
):
    """删除信用卡（软删除）"""
    try:
        # 软删除：设置为非激活状态
        updated_card = await Card.find_one_and_update(
            {"_id": card_id, "user_id": user_id},
            {"$set": {"is_active": False}}
        )
        
        if not updated_card:
            return handle_error(ErrorCode.INVALID_PARAMS, "信用卡不存在")
        
        return {}
        
    except Exception as e:
        logger.error(f"删除信用卡失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "删除信用卡失败")

@router.get("/card/detail/{card_id}")
async def get_card_detail(
    card_id: str,
    user_id: str = Depends(auth_user)
):
    """获取信用卡详情"""
    try:
        card = await Card.find_one({
            "_id": card_id,
            "user_id": user_id
        })
        
        if not card:
            return handle_error(ErrorCode.INVALID_PARAMS, "信用卡不存在")
        
        return card
        
    except Exception as e:
        logger.error(f"获取信用卡详情失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "获取信用卡详情失败")