import asyncio
import functools
from datetime import datetime, timedelta
from typing import Callable, Any
from app.services.mongodb.models import Schedule
from app.utils import get_logger

logger = get_logger()

class TaskLockManager:
    """定时任务锁管理器"""
    
    @staticmethod
    async def try_acquire_lock(task_name: str, lock_seconds: int = 2) -> bool:
        # 计算锁定时间阈值
        lock_threshold = datetime.now().astimezone() - timedelta(seconds=lock_seconds)

        # 尝试更新：条件是任务名称匹配且(上次执行时间超过锁定时长 或 executed_at字段不存在)
        result = await Schedule.find_one_and_update(
            {
                "task_name": task_name,
                "$or": [
                    {"executed_at": {"$lt": lock_threshold}},
                    {"executed_at": {"$exists": False}}
                ]
            },
            {
                "$set": {
                    "executed_at": datetime.now().astimezone()
                }
            }
        )
        
        # 如果更新了文档，说明获取锁成功
        return result is not None

def task_execution(task_name: str, lock_seconds: int = 2):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # 尝试获取锁
            if not await TaskLockManager.try_acquire_lock(task_name, lock_seconds):
                # logger.info(f"任务 {task_name} 正在执行中或锁定期内，跳过本次执行")
                return None
            
            # logger.info(f"任务 {task_name} 获取锁成功，开始执行")
            
            try:
                # 执行原函数
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                return result
                
            except Exception as e:
                logger.error(f"任务 {task_name} 执行失败: {e}", exc_info=True)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # 对于同步函数，需要在异步环境中运行
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        # 根据原函数类型返回对应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
