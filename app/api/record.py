from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Body, Depends, Query
from app.middlewares.inject import auth_user
from app.services.mongodb.models.record import Record
from app.services.mongodb.models.card import Card
from app.services.mongodb.models.swipe_type import SwipeType
from app.services.mongodb.models.consumption_type import ConsumptionType
from app.utils import get_logger, handle_error, dict_to_sort_list, to_local_timezone
from app.define import ErrorCode

logger = get_logger()

router = APIRouter()

@router.get("/record/list")
async def get_records(
    user_id: str = Depends(auth_user),
    card_id: str = Query(None, description="信用卡ID"),
    consumption_type_id: str = Query(None, description="消费类型ID"),
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    sort: str = Query(f"{{'trade_date': -1}}", description="排序字段"),
):
    """获取消费记录列表"""
    try:
        # sort 转换为字典
        sort = eval(sort)
        # 构建查询条件
        filter_dict = {"user_id": user_id, "is_active": True}
        
        if card_id:
            filter_dict["card_id"] = card_id
        
        if consumption_type_id:
            filter_dict["consumption_type_id"] = consumption_type_id
        
        # 日期范围查询
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                # 结束日期包含当天，所以加一天
                end_datetime = datetime.fromisoformat(end_date) + timedelta(days=1)
                date_filter["$lt"] = end_datetime
            filter_dict["trade_date"] = date_filter
        
        # 分页计算
        skip = (page - 1) * page_size
        
        # 查询记录
        records = await Record.find_many(
            filter=filter_dict,
            sort=dict_to_sort_list(sort),
            skip=skip,
            limit=page_size
        )
        
        # 获取总数
        total = await Record.count(filter_dict)
        
        return {
            "list": records,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
        
    except Exception as e:
        logger.error(f"获取消费记录列表失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "获取消费记录列表失败")

@router.post("/record/add")
async def add_record(
    user_id: str = Depends(auth_user),
    body: Dict[str, Any] = Body(...)
):
    """添加消费/还款记录"""
    try:
        card_id = body.get("card_id")
        swipe_type_id = body.get("swipe_type_id")
        consumption_type_id = body.get("consumption_type_id")
        amount = body.get("amount")
        trade_date = body.get("trade_date")
        record_type = body.get("record_type", "支付")  # 新增类型

        if record_type not in ["支付", "还款"]:
            return handle_error(ErrorCode.INVALID_PARAMS, "记录类型不合法")
        
        if not all([card_id, amount]):
            return handle_error(ErrorCode.INVALID_PARAMS, "缺少必要参数")
        
        if record_type == "支付" and not all([swipe_type_id, consumption_type_id]):
            return handle_error(ErrorCode.INVALID_PARAMS, "缺少必要参数")
        
        # 验证信用卡、类型
        card = await Card.find_one({
            "_id": card_id,
            "user_id": user_id,
            "is_active": True
        })
        
        if not card:
            return handle_error(ErrorCode.INVALID_PARAMS, "信用卡不存在或不可用")

        consumption_type_name = None
        if consumption_type_id:      
            consumption_type = await ConsumptionType.find_one({
                "_id": consumption_type_id,
                "user_id": user_id,
                "is_active": True
            })
            if not consumption_type:
                return handle_error(ErrorCode.INVALID_PARAMS, "消费类型不存在或不可用")
            consumption_type_name = consumption_type.name
        
        swipe_type_name = None
        if swipe_type_id: 
            swipe_type = await SwipeType.find_one({
                "_id": swipe_type_id,
                "is_active": True
            })
            if not swipe_type:
                return handle_error(ErrorCode.INVALID_PARAMS, "刷卡类型不存在或不可用")
            swipe_type_name = swipe_type.name
        
        # 时间
        if trade_date:
            trade_date = to_local_timezone(datetime.fromisoformat(trade_date))
        else:
            trade_date = datetime.now().astimezone()
        
        # 构造记录
        record = Record(
            user_id=user_id,
            card_id=card_id,
            card_name=card.name,
            card_bank=card.bank,
            card_number=card.card_number,
            swipe_type_id=swipe_type_id,
            swipe_type_name=swipe_type_name,
            consumption_type_id=consumption_type_id,
            consumption_type_name=consumption_type_name,
            amount=float(amount),
            description=body.get("description"),
            trade_date=trade_date,
            record_type=record_type,
            status="未还"
        )
        
        await record.save()
        
        # ========== 新增还款：分配到未还/部分还的支付记录，并更新还款状态 ==========
        if record_type == "还款":
            remaining_repay = float(amount)
            applied_total = 0.0
            
            payments = await Record.find_many(
                filter={
                    "user_id": user_id,
                    "card_id": card_id,
                    "record_type": "支付",
                    "status": {"$in": ["未还", "部分还"]},
                    "is_active": True
                },
                sort=[("trade_date", 1)]
            )
            
            for payment in payments:
                if remaining_repay <= 0:
                    break
                repaid_amount = sum((ref.amount for ref in (payment.repayment_refs or [])))
                remaining_payment = max(payment.amount - repaid_amount, 0.0)
                if remaining_payment <= 0:
                    continue
                
                applied = min(remaining_payment, remaining_repay)
                
                # 更新支付记录：追加还款引用并更新状态
                new_payment_status = "已还" if (repaid_amount + applied) >= payment.amount else \
                                     ("部分还" if (repaid_amount + applied) > 0 else "未还")
                await Record.update_one(
                    {"_id": payment.id, "user_id": user_id},
                    {
                        "$push": {"repayment_refs": {"repayment_id": record.id, "amount": applied}},
                        "$set": {"status": new_payment_status, "updated_at": datetime.now().astimezone()}
                    }
                )
                
                remaining_repay -= applied
                applied_total += applied
            
            # 更新还款记录状态（已全部分配/部分分配/未分配）
            new_repayment_status = "已还" if applied_total >= float(amount) else \
                                   ("部分还" if applied_total > 0 else "未还")
            await Record.update_one(
                {"_id": record.id, "user_id": user_id},
                {"$set": {"status": new_repayment_status, "updated_at": datetime.now().astimezone()}}
            )
        
        # ========== 新增支付：消耗未还/部分还的还款记录，更新双方状态 ==========
        if record_type == "支付":
            remaining_payment = float(amount)
            repaid_total_for_this_payment = 0.0
            
            repayments = await Record.find_many(
                filter={
                    "user_id": user_id,
                    "card_id": card_id,
                    "record_type": "还款",
                    "status": {"$in": ["未还", "部分还"]},
                    "is_active": True
                },
                sort=[("trade_date", 1)]
            )
            
            for repayment in repayments:
                if remaining_payment <= 0:
                    break
                
                # 计算该还款已被分配的总额（聚合统计所有支付记录的repayment_refs）
                pipeline = [
                    {"$match": {
                        "user_id": user_id,
                        "card_id": card_id,
                        "record_type": "支付",
                        "is_active": True,
                        "repayment_refs": {"$elemMatch": {"repayment_id": repayment.id}}
                    }},
                    {"$unwind": "$repayment_refs"},
                    {"$match": {"repayment_refs.repayment_id": repayment.id}},
                    {"$group": {"_id": None, "applied": {"$sum": "$repayment_refs.amount"}}}
                ]
                agg = await Record.aggregate(pipeline)
                applied_so_far = (agg[0]["applied"] if agg else 0.0)
                
                remaining_repay = max(repayment.amount - applied_so_far, 0.0)
                if remaining_repay <= 0:
                    # 已完全分配的还款，状态应为已还（兜底修正）
                    await Record.update_one(
                        {"_id": repayment.id, "user_id": user_id},
                        {"$set": {"status": "已还", "updated_at": datetime.now().astimezone()}}
                    )
                    continue
                
                applied = min(remaining_repay, remaining_payment)
                
                # 更新当前支付记录的还款引用
                await Record.update_one(
                    {"_id": record.id, "user_id": user_id},
                    {
                        "$push": {"repayment_refs": {"repayment_id": repayment.id, "amount": applied}},
                        "$set": {"updated_at": datetime.now().astimezone()}
                    }
                )
                repaid_total_for_this_payment += applied
                remaining_payment -= applied
                
                # 更新还款记录状态
                new_repayment_status = "已还" if (applied_so_far + applied) >= repayment.amount else \
                                       ("部分还" if (applied_so_far + applied) > 0 else "未还")
                await Record.update_one(
                    {"_id": repayment.id, "user_id": user_id},
                    {"$set": {"status": new_repayment_status, "updated_at": datetime.now().astimezone()}}
                )
            
            # 最后更新当前支付记录的状态
            new_payment_status = "已还" if repaid_total_for_this_payment >= float(amount) else \
                                 ("部分还" if repaid_total_for_this_payment > 0 else "未还")
            await Record.update_one(
                {"_id": record.id, "user_id": user_id},
                {"$set": {"status": new_payment_status, "updated_at": datetime.now().astimezone()}}
            )
        
        return await Record.find_by_id(record.id)
        
    except Exception as e:
        logger.error(f"添加消费记录失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "添加消费记录失败")

@router.put("/record/update/{record_id}")
async def update_record(
    record_id: str,
    user_id: str = Depends(auth_user),
    body: Dict[str, Any] = Body(...)
):
    """更新消费记录"""
    try:
        # 查找记录
        record = await Record.find_one({
            "_id": record_id,
            "user_id": user_id
        })
        
        if not record:
            return handle_error(ErrorCode.INVALID_PARAMS, "消费记录不存在")
        
        # 更新字段
        update_fields = {}
        for field in ["card_id", "swipe_type_id", "consumption_type_id", "amount", 
                     "description", "trade_date", "is_active"]:
            if field in body:
                if field == "amount":
                    update_fields[field] = float(body[field])
                elif field == "trade_date":
                    update_fields[field] = datetime.fromisoformat(body[field])
                else:
                    update_fields[field] = body[field]
        
        if update_fields:
            updated_record = await Record.find_one_and_update(
                {"_id": record_id, "user_id": user_id},
                {"$set": update_fields}
            )
            return updated_record
        
        return record
        
    except Exception as e:
        logger.error(f"更新消费记录失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "更新消费记录失败")

@router.delete("/record/delete/{record_id}")
async def delete_record(
    record_id: str,
    user_id: str = Depends(auth_user)
):
    """删除消费记录（软删除）"""
    try:
        # 软删除：设置为非激活状态
        updated_record = await Record.find_one_and_update(
            {"_id": record_id, "user_id": user_id},
            {"$set": {"is_active": False}}
        )
        
        if not updated_record:
            return handle_error(ErrorCode.INVALID_PARAMS, "消费记录不存在")
        
        return {}
        
    except Exception as e:
        logger.error(f"删除消费记录失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "删除消费记录失败")

@router.get("/record/stats")
async def get_record_stats(
    user_id: str = Depends(auth_user),
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    card_id: str = Query(None, description="信用卡ID")
):
    """获取消费统计"""
    try:
        # 构建查询条件
        match_filter = {"user_id": user_id, "is_active": True}
        
        if card_id:
            match_filter["card_id"] = card_id
        
        # 日期范围查询
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                end_datetime = datetime.fromisoformat(end_date) + timedelta(days=1)
                date_filter["$lt"] = end_datetime
            match_filter["trade_date"] = date_filter
        
        # 聚合查询
        pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": "$consumption_type_id",
                    "total_amount": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"total_amount": -1}}
        ]
        
        stats = await Record.aggregate(pipeline)
        
        # 获取消费类型信息
        consumption_types = {}
        if stats:
            type_ids = [stat["_id"] for stat in stats]
            types = await ConsumptionType.find_many({
                "_id": {"$in": type_ids},
                "user_id": user_id
            })
            consumption_types = {t.id: t for t in types}
        
        # 组装结果
        result = []
        total_amount = 0
        for stat in stats:
            type_info = consumption_types.get(stat["_id"], {})
            result.append({
                "consumption_type_id": stat["_id"],
                "consumption_type_name": type_info.get("name", "未知"),
                "consumption_type_color": type_info.get("color", "#3B82F6"),
                "total_amount": stat["total_amount"],
                "count": stat["count"]
            })
            total_amount += stat["total_amount"]
        
        return {
            "stats": result,
            "total_amount": total_amount
        }
        
    except Exception as e:
        logger.error(f"获取消费统计失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "获取消费统计失败")