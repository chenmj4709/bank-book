import asyncio
import time
import uuid
from typing import Optional
from app.services.redis.client import business_client
from app.utils.logger import get_logger

logger = get_logger()

class DynamicRedisLock:
    """动态Redis锁，支持基于动态key的分布式锁"""
    
    def __init__(self, key: str, timeout: int = 30, retry_interval: float = 0.1):
        """
        初始化动态Redis锁
        
        Args:
            key: 锁的唯一标识
            timeout: 锁的超时时间（秒）
            retry_interval: 获取锁失败时的重试间隔（秒）
        """
        self.key = f"dynamic_lock:{key}"
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.lock_value = None
        self.acquired = False
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.release()
    
    async def acquire(self):
        """
        获取锁，成功则返回，失败则抛出TimeoutError异常
        """
        if self.acquired:
            return
        
        # 生成唯一的锁值，用于安全释放
        self.lock_value = f"{uuid.uuid4().hex}_{int(time.time())}"
        start_time = time.time()
        
        try:
            while True:
                # 使用 SET 命令的 NX 和 EX 选项实现原子操作
                result = await business_client.set(
                    self.key, 
                    self.lock_value, 
                    nx=True,  # 只在key不存在时设置
                    ex=self.timeout  # 设置过期时间
                )
                
                if result:
                    self.acquired = True
                    logger.debug(f"获取动态锁成功: {self.key}")
                    return
                
                # 检查超时
                if time.time() - start_time > self.timeout:
                    raise TimeoutError(f"获取动态锁超时: {self.key}, 超时时间: {self.timeout}秒")
                
                # 等待重试
                await asyncio.sleep(self.retry_interval)
                
        except TimeoutError:
            # 超时异常直接抛出
            raise
        except Exception as e:
            # 其他异常包装后抛出
            logger.error(f"获取动态锁异常: {self.key}, 错误: {str(e)}")
            raise RuntimeError(f"获取锁时发生异常: {str(e)}")
    
    async def release(self):
        """
        释放锁
        """
        if not self.acquired or not self.lock_value:
            return
        
        try:
            # 使用 Lua 脚本确保只有锁的持有者才能释放锁
            lua_script = """
            if redis.call("GET", KEYS[1]) == ARGV[1] then
                return redis.call("DEL", KEYS[1])
            else
                return 0
            end
            """
            
            result = await business_client.eval(
                lua_script, 1, self.key, self.lock_value
            )
            
            if result == 1:
                logger.debug(f"释放动态锁成功: {self.key}")
            else:
                logger.warning(f"释放动态锁失败，锁可能已被其他进程持有或已过期: {self.key}")
                
        except Exception as e:
            logger.error(f"释放动态锁异常: {self.key}, 错误: {str(e)}")
        finally:
            # 无论如何都要重置状态
            self.acquired = False
            self.lock_value = None
    
    async def extend_lock(self, additional_time: int = None):
        """
        延长锁的过期时间
        
        Args:
            additional_time: 额外的时间（秒），如果不提供则使用原始timeout
        """
        if not self.acquired or not self.lock_value:
            raise RuntimeError("锁未获取，无法延长")
        
        extend_time = additional_time or self.timeout
        
        try:
            # 使用 Lua 脚本确保只有锁的持有者才能延长锁
            lua_script = """
            if redis.call("GET", KEYS[1]) == ARGV[1] then
                return redis.call("EXPIRE", KEYS[1], ARGV[2])
            else
                return 0
            end
            """
            
            result = await business_client.eval(
                lua_script, 1, self.key, self.lock_value, str(extend_time)
            )
            
            if result == 1:
                logger.debug(f"延长动态锁成功: {self.key}, 延长时间: {extend_time}秒")
            else:
                raise RuntimeError(f"延长锁失败，锁可能已被其他进程持有或已过期: {self.key}")
                
        except Exception as e:
            logger.error(f"延长动态锁异常: {self.key}, 错误: {str(e)}")
            raise
    
    def is_acquired(self) -> bool:
        """检查锁是否已获取"""
        return self.acquired

def create_user_update_lock(user_id: str, timeout: int = 10) -> DynamicRedisLock:
    """
    为特定的 user_id 创建锁
    
    Args:
        user_id: 用户ID
        timeout: 锁超时时间（秒）
        
    Returns:
        DynamicRedisLock: 动态Redis锁实例
    """
    return DynamicRedisLock(
        key=f"user_update_lock:{user_id}",
        timeout=timeout,
        retry_interval=1
    )
