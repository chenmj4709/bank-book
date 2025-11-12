import asyncio
import functools
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from app.utils import get_logger

logger = get_logger()

# 用于存储主事件循环
main_event_loop = None

# 创建调度器
jobstores = {
    'default': MemoryJobStore()
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone='Asia/Shanghai'
)

def run_async_job(func):
    """
    包装异步函数以便在APScheduler中使用，确保在主事件循环中运行
    
    Args:
        func: 异步函数
    
    Returns:
        包装后的函数
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if main_event_loop is None:
            logger.error("主事件循环未设置，无法调度异步任务 %s", func.__name__)
            # 在没有主循环的情况下，可以选择抛出错误或尝试回退（但不推荐）
            # 这里我们选择记录错误并返回，防止任务执行
            return
            # raise RuntimeError("Main event loop is not set for scheduler.")

        if not main_event_loop.is_running():
             logger.warning("主事件循环未运行，无法调度异步任务 %s", func.__name__)
             return # 或者抛出错误

        # 使用 run_coroutine_threadsafe 在主事件循环中安全地运行协程
        # 这会返回一个 concurrent.futures.Future 对象
        future = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), main_event_loop)
        try:
            # 等待协程在主循环中完成并获取结果
            # future.result() 会阻塞当前线程（APScheduler的工作线程）直到协程完成
            return future.result()
        except Exception as e:
            # 捕获并记录在主循环中执行协程时发生的异常
            logger.error(f"在主循环中执行任务 {func.__name__} 时出错: {e}", exc_info=True)
            # 根据需要决定是否重新抛出异常，让APScheduler知道任务失败
            raise
    return wrapper

def scheduled_job(trigger, **trigger_args):
    """
    自定义装饰器，支持异步和同步函数
    
    Args:
        trigger: 触发器类型
        **trigger_args: 触发器参数
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        job_func = func
        if asyncio.iscoroutinefunction(func):
            # 如果是异步函数，使用包装器确保在主循环运行
            job_func = run_async_job(func)
        
        # 添加任务到调度器
        # 确保传递的是包装后的函数（如果是异步的）
        scheduler.add_job(job_func, trigger, **trigger_args)
        logger.info(f"已注册定时任务: {func.__name__} (ID: {trigger_args.get('id', '默认')}), Trigger: {trigger}, Args: {trigger_args}")
        # 返回原始函数，以便它仍然可以被其他方式调用（如果需要）
        return func
    return decorator

async def init_scheduler():
    """初始化并启动调度器"""
    global main_event_loop
    try:
        # 获取当前正在运行的事件循环作为主循环
        # 这假设 init_scheduler 是在主应用的异步上下文中调用的
        main_event_loop = asyncio.get_running_loop()
        logger.info(f"捕获主事件循环: {main_event_loop}")

        # 导入所有任务模块，这将触发 @scheduled_job 装饰器注册任务
        from app.services.scheduler import tasks
        logger.info("正在加载并注册定时任务...")
        
        if not scheduler.running:
            scheduler.start()
            logger.info("定时任务调度器已启动")
            
            # 打印所有已注册的任务
            jobs = scheduler.get_jobs()
            if jobs:
                logger.info(f"当前已注册 {len(jobs)} 个定时任务:")
                # for job in jobs: # 可以取消注释以打印详细信息
                #     logger.info(f" - ID: {job.id}, Name: {job.name}, Trigger: {job.trigger}")
            else:
                logger.warning("没有注册任何定时任务")
                
        return True
    except Exception as e:
        logger.error(f"定时任务调度器启动失败: {str(e)}", exc_info=True)
        # 如果启动失败，重置主循环变量
        main_event_loop = None 
        return False

async def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        # 等待当前正在运行的任务完成（可选，graceful shutdown）
        scheduler.shutdown() 
        logger.info("定时任务调度器已关闭")
