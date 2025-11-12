from typing import Dict, Any, List
from fastapi import APIRouter, Request, Body, Depends, Query
from app.middlewares.inject import auth_user
from app.services.mongodb.models.swipe_type import SwipeType
from app.services.mongodb.models.consumption_type import ConsumptionType
from app.utils import get_logger, handle_error, dict_to_sort_list
from app.define import ErrorCode

logger = get_logger()

router = APIRouter()

# ==================== 刷卡类型管理 ====================

@router.get("/category/swipe-types")
async def get_swipe_types(
    user_id: str = Depends(auth_user),
    is_active: bool = Query(True, description="是否只获取激活的类型")
):
    """获取刷卡类型列表"""
    try:
        sort = {"sort_order": 1, "created_at": 1}
        filter_dict = {"user_id": user_id}
        if is_active is not None:
            filter_dict["is_active"] = is_active
            
        swipe_types = await SwipeType.find_many(
            filter=filter_dict,
            sort=dict_to_sort_list(sort)
        )
        
        return swipe_types
    except Exception as e:
        logger.error(f"获取刷卡类型列表失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "获取刷卡类型列表失败")

@router.post("/category/swipe-type")
async def add_swipe_type(
    user_id: str = Depends(auth_user),
    body: Dict[str, Any] = Body(...)
):
    """添加刷卡类型"""
    try:
        name = body.get("name")
        
        if not name:
            return handle_error(ErrorCode.INVALID_PARAMS, "类型名称不能为空")
        
        # 检查是否已存在同名类型
        existing_type = await SwipeType.find_one({
            "user_id": user_id,
            "name": name,
            "is_active": True
        })
        
        if existing_type:
            return handle_error(ErrorCode.INVALID_PARAMS, "已存在同名刷卡类型")
        
        # 创建新类型
        swipe_type = SwipeType(
            user_id=user_id,
            name=name,
            description=body.get("description"),
            sort_order=body.get("sort_order", 0)
        )
        
        await swipe_type.save()
        return swipe_type
        
    except Exception as e:
        logger.error(f"添加刷卡类型失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "添加刷卡类型失败")

@router.put("/category/swipe-type/{type_id}")
async def update_swipe_type(
    type_id: str,
    user_id: str = Depends(auth_user),
    body: Dict[str, Any] = Body(...)
):
    """更新刷卡类型"""
    try:
        # 查找类型
        swipe_type = await SwipeType.find_one({
            "_id": type_id,
            "user_id": user_id
        })
        
        if not swipe_type:
            return handle_error(ErrorCode.INVALID_PARAMS, "刷卡类型不存在")
        
        # 更新字段
        update_fields = {}
        for field in ["name", "description", "is_active", "sort_order"]:
            if field in body:
                update_fields[field] = body[field]
        
        if update_fields:
            updated_type = await SwipeType.find_one_and_update(
                {"_id": type_id, "user_id": user_id},
                {"$set": update_fields}
            )
            return updated_type
        
        return swipe_type
        
    except Exception as e:
        logger.error(f"更新刷卡类型失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "更新刷卡类型失败")

@router.delete("/category/swipe-type/{type_id}")
async def delete_swipe_type(
    type_id: str,
    user_id: str = Depends(auth_user)
):
    """删除刷卡类型（软删除）"""
    try:
        # 软删除：设置为非激活状态
        updated_type = await SwipeType.find_one_and_update(
            {"_id": type_id, "user_id": user_id},
            {"$set": {"is_active": False}}
        )
        
        if not updated_type:
            return handle_error(ErrorCode.INVALID_PARAMS, "刷卡类型不存在")
        
        return {}
        
    except Exception as e:
        logger.error(f"删除刷卡类型失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "删除刷卡类型失败")

# ==================== 消费类型管理 ====================

@router.get("/category/consumption-types")
async def get_consumption_types(
    user_id: str = Depends(auth_user),
    is_active: bool = Query(True, description="是否只获取激活的类型")
):
    """获取消费类型列表"""
    try:
        sort = {"sort_order": 1, "created_at": 1}
        filter_dict = {"user_id": user_id}
        if is_active is not None:
            filter_dict["is_active"] = is_active
            
        consumption_types = await ConsumptionType.find_many(
            filter=filter_dict,
            sort=dict_to_sort_list(sort)
        )
        
        return consumption_types
    except Exception as e:
        logger.error(f"获取消费类型列表失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "获取消费类型列表失败")

@router.post("/category/consumption-type")
async def add_consumption_type(
    user_id: str = Depends(auth_user),
    body: Dict[str, Any] = Body(...)
):
    """添加消费类型"""
    try:
        name = body.get("name")
        
        if not name:
            return handle_error(ErrorCode.INVALID_PARAMS, "类型名称不能为空")
        
        # 检查是否已存在同名类型
        existing_type = await ConsumptionType.find_one({
            "user_id": user_id,
            "name": name,
            "is_active": True
        })
        
        if existing_type:
            return handle_error(ErrorCode.INVALID_PARAMS, "已存在同名消费类型")
        
        # 创建新类型
        consumption_type = ConsumptionType(
            user_id=user_id,
            name=name,
            icon=body.get("icon"),
            color=body.get("color", "#3B82F6"),
            description=body.get("description"),
            sort_order=body.get("sort_order", 0)
        )
        
        await consumption_type.save()
        return consumption_type
        
    except Exception as e:
        logger.error(f"添加消费类型失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "添加消费类型失败")

@router.put("/category/consumption-type/{type_id}")
async def update_consumption_type(
    type_id: str,
    user_id: str = Depends(auth_user),
    body: Dict[str, Any] = Body(...)
):
    """更新消费类型"""
    try:
        # 查找类型
        consumption_type = await ConsumptionType.find_one({
            "_id": type_id,
            "user_id": user_id
        })
        
        if not consumption_type:
            return handle_error(ErrorCode.INVALID_PARAMS, "消费类型不存在")
        
        # 更新字段
        update_fields = {}
        for field in ["name", "icon", "color", "description", "is_active", "sort_order"]:
            if field in body:
                update_fields[field] = body[field]
        
        if update_fields:
            updated_type = await ConsumptionType.find_one_and_update(
                {"_id": type_id, "user_id": user_id},
                {"$set": update_fields}
            )
            return updated_type
        
        return consumption_type
        
    except Exception as e:
        logger.error(f"更新消费类型失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "更新消费类型失败")

@router.delete("/category/consumption-type/{type_id}")
async def delete_consumption_type(
    type_id: str,
    user_id: str = Depends(auth_user)
):
    """删除消费类型（软删除）"""
    try:
        # 软删除：设置为非激活状态
        updated_type = await ConsumptionType.find_one_and_update(
            {"_id": type_id, "user_id": user_id},
            {"$set": {"is_active": False}}
        )
        
        if not updated_type:
            return handle_error(ErrorCode.INVALID_PARAMS, "消费类型不存在")
        
        return {}
        
    except Exception as e:
        logger.error(f"删除消费类型失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "删除消费类型失败")