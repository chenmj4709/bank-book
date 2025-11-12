"""
示例定时任务
每10秒执行一次，记录当前时间
"""
import datetime
from app.utils import get_logger
from app.services.scheduler.scheduler import scheduled_job
from app.services.scheduler.task_lock import task_execution

logger = get_logger()

# 使用自定义装饰器替代原来的scheduler.scheduled_job
@scheduled_job('interval', seconds=60, id='example_task')
@task_execution('example_task', lock_seconds=10)
async def example_task():
    """示例定时任务，每10秒执行一次"""
    current_time = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
    # logger.info(f"示例定时任务执行 - 当前时间: {current_time}")
