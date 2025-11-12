# 顶部导入
from typing import Dict, Any, List
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends
from app.middlewares.inject import auth_user
from app.services.mongodb.models.card import Card
from app.services.mongodb.models.record import Record
from app.services.mongodb.models.consumption_type import ConsumptionType
from app.utils import get_logger, handle_error
from app.define import ErrorCode
from calendar import monthrange  # 新增：用于安全计算每月天数

logger = get_logger()
router = APIRouter()

@router.get("/home/dashboard")
async def get_home_dashboard(user_id: str = Depends(auth_user)):
    try:
        now = datetime.now().astimezone()

        # 当前月范围（自然月）
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (start_of_month + timedelta(days=32)).replace(day=1)
        end_of_month = next_month.replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取激活的信用卡
        cards = await Card.find_many(
            filter={"user_id": user_id, "is_active": True},
            sort=[("payment_day", 1), ("created_at", -1)]
        )
        total_limit = sum([c.credit_limit for c in (cards or [])])

        # 全局占用（未还/部分还），不按账单周期
        pipeline_outstanding = [
            {"$project": {
                "amount": 1, "user_id": 1, "is_active": 1, "card_id": 1,
                "swipe_type_id": 1, "swipe_type_name": 1, "record_type": 1,
                "status": 1, "repayment_refs": 1
            }},
            {"$match": {
                "user_id": user_id, "is_active": True,
                "record_type": "支付",
                "status": {"$in": ["未还", "部分还"]}
            }},
            {"$addFields": {
                "repaid": {"$ifNull": [
                    {"$sum": {"$map": {
                        "input": "$repayment_refs",
                        "as": "r",
                        "in": {"$ifNull": ["$$r.amount", 0]}
                    }}},
                    0
                ]}
            }},
            {"$addFields": {
                "outstanding": {"$max": [
                    {"$subtract": ["$amount", "$repaid"]},
                    0
                ]}
            }},
            {"$group": {
                "_id": {"card_id": "$card_id", "swipe_type_id": "$swipe_type_id"},
                "card_id": {"$first": "$card_id"},
                "name": {"$first": "$swipe_type_name"},
                "total_outstanding": {"$sum": "$outstanding"}
            }},
            {"$sort": {"total_outstanding": -1}}
        ]
        outstanding_stats = await Record.aggregate(pipeline_outstanding)

        used_by_card = {}
        used_swipe_by_card = {}
        for s in outstanding_stats or []:
            cid = s.get("card_id")
            name = s.get("name") or "未知"
            amt = float(s.get("total_outstanding", 0.0))
            if cid not in used_by_card:
                used_by_card[cid] = 0.0
                used_swipe_by_card[cid] = []
            used_by_card[cid] += amt
            used_swipe_by_card[cid].append({"name": name, "amount": amt})

        # 本月账单：当月所有支付金额（按卡汇总）
        pipeline_monthly_spent = [
            {"$match": {
                "user_id": user_id, "is_active": True,
                "record_type": "支付",
                "trade_date": {"$gte": start_of_month, "$lt": end_of_month}
            }},
            {"$group": {"_id": "$card_id", "total_spent": {"$sum": "$amount"}}}
        ]
        monthly_spent_agg = await Record.aggregate(pipeline_monthly_spent)
        monthly_spent_by_card = {s["_id"]: float(s.get("total_spent", 0.0)) for s in (monthly_spent_agg or [])}

        # 本月待还：当月“支付且未还/部分还”的未还部分（按卡汇总）
        pipeline_monthly_outstanding = [
            {"$project": {
                "amount": 1, "user_id": 1, "is_active": 1, "card_id": 1,
                "record_type": 1, "status": 1, "repayment_refs": 1, "trade_date": 1
            }},
            {"$match": {
                "user_id": user_id, "is_active": True,
                "record_type": "支付",
                "status": {"$in": ["未还", "部分还"]},
                "trade_date": {"$gte": start_of_month, "$lt": end_of_month}
            }},
            {"$addFields": {
                "repaid": {"$ifNull": [
                    {"$sum": {"$map": {
                        "input": "$repayment_refs",
                        "as": "r",
                        "in": {"$ifNull": ["$$r.amount", 0]}
                    }}},
                    0
                ]}
            }},
            {"$addFields": {
                "outstanding": {"$max": [
                    {"$subtract": ["$amount", "$repaid"]},
                    0
                ]}
            }},
            {"$group": {
                "_id": "$card_id",
                "total_outstanding": {"$sum": "$outstanding"}
            }}
        ]
        monthly_outstanding_agg = await Record.aggregate(pipeline_monthly_outstanding)
        monthly_outstanding_by_card = {s["_id"]: float(s.get("total_outstanding", 0.0)) for s in (monthly_outstanding_agg or [])}

        # 还款剩余天数：到下一次 payment_day 的天数（始终非负）
        def compute_days_to_payment(payment_day: int) -> int | None:
            if not payment_day:
                return None
            try:
                pd = int(payment_day)
            except Exception:
                return None
            if pd <= 0:
                return None
            y, m = now.year, now.month
            # 当月的还款日（处理大小月）
            pd_cur = min(pd, monthrange(y, m)[1])
            today = now.date()
            cur_due = date(y, m, pd_cur)
            if today <= cur_due:
                target = cur_due
            else:
                ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
                pd_next = min(pd, monthrange(ny, nm)[1])
                target = date(ny, nm, pd_next)
            return max((target - today).days, 0)

        # 消费分析（跨卡）
        pipeline_spent = [
            {"$project": {
                "amount": 1, "user_id": 1, "is_active": 1, "record_type": 1,
                "swipe_type_id": 1, "swipe_type_name": 1
            }},
            {"$match": {
                "user_id": user_id, "is_active": True, "record_type": "支付"
            }},
            {"$group": {
                "_id": "$swipe_type_id",
                "name": {"$first": "$swipe_type_name"},
                "total_amount": {"$sum": "$amount"}
            }}
        ]
        spent_stats = await Record.aggregate(pipeline_spent)
        swipe_type_totals = {}
        for s in spent_stats or []:
            name = s.get("name") or "未知"
            amount = float(s.get("total_amount", 0.0))
            swipe_type_totals[name] = swipe_type_totals.get(name, 0.0) + amount

        # 类型统计（全量）
        pipeline_type = [
            {"$project": {
                "amount": 1, "user_id": 1, "is_active": 1, "record_type": 1
            }},
            {"$match": {"user_id": user_id, "is_active": True}},
            {"$group": {"_id": "$record_type", "total_amount": {"$sum": "$amount"}}}
        ]
        type_stats_agg = await Record.aggregate(pipeline_type)
        type_stats_global = {"支付": 0.0, "还款": 0.0}
        for t in type_stats_agg or []:
            rt = t.get("_id")
            if rt in type_stats_global:
                type_stats_global[rt] += float(t.get("total_amount", 0.0))

        # 组装卡片数据（新增：monthlyBill、monthlyOutstanding、daysToPayment）
        cards_payload = []
        for c in cards or []:
            card_used_sum = used_by_card.get(c.id, 0.0)
            used_by_swipe = sorted(used_swipe_by_card.get(c.id, []), key=lambda x: x["amount"], reverse=True)
            cards_payload.append({
                "id": c.id,
                "bank": c.bank,
                "color": c.color,
                "lastFour": str(c.card_number)[-4:] if c.card_number else "",
                "limit": c.credit_limit,
                "used": card_used_sum,
                "billDate": c.bill_day,
                "paymentDate": c.payment_day,
                "lastPaymentDate": c.last_payment_day,
                "usedBySwipeTypes": used_by_swipe,
                "monthlyBill": monthly_spent_by_card.get(c.id, 0.0),
                "monthlyOutstanding": monthly_outstanding_by_card.get(c.id, 0.0),
                "daysToPayment": compute_days_to_payment(c.payment_day)
            })

        total_outstanding_used = sum([item["used"] for item in cards_payload])
        total_available = total_limit - total_outstanding_used

        consumption_payload = []
        for name, amount in sorted(swipe_type_totals.items(), key=lambda x: x[1], reverse=True):
            consumption_payload.append({
                "name": name,
                "amount": amount,
                "color": "#5751D5" if name == "消费" else "#3B82F6"
            })

        return {
            "cards": cards_payload,
            "totals": {"limit": total_limit, "used": total_outstanding_used, "available": total_available},
            "consumption": consumption_payload,
            "typeStats": type_stats_global,
            "timeRange": {
                "start": start_of_month.isoformat(),
                "end": end_of_month.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"获取首页数据失败: {str(e)}")
        return handle_error(ErrorCode.UNKNOWN_ERROR, "获取首页数据失败")