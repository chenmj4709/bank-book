import asyncio
from redis.asyncio import Redis, ConnectionPool
from redis.asyncio.connection import Connection
from redis.exceptions import ConnectionError
from app.config import config
from app.utils import get_logger
from redis import Redis as SyncRedis
from redis.exceptions import ConnectionError

logger = get_logger()

class RedisConnectionListener(Connection):
    """自定义Redis连接类，用于监听连接事件"""
    def __init__(self, on_disconnect=None, **kwargs):
        super().__init__(**kwargs)
        self.on_disconnect = on_disconnect
        
    async def disconnect(self, nowait=False):
        """重写断开连接方法，添加事件回调"""
        if self.on_disconnect:
            await self.on_disconnect()
        await super().disconnect(nowait=nowait)

class _RedisClient:
    def __init__(self):
        self.redis_config = config["redis"]
        self.session_client = None
        self.business_client = None
        self.session_db = self.redis_config["db"]["session"]
        self.business_db = self.redis_config["db"]["business"]
        self.session_pool = None
        self.business_pool = None
        self._reconnect_lock = asyncio.Lock()
        self._health_check_task = None
        self._shutting_down = False  # 添加关闭标记
        # 不再在初始化时连接和启动健康检查
        
    async def initialize(self):
        """显式初始化Redis连接和健康检查"""
        if self.session_client is None or self.business_client is None:
            await self._connect()
            
            # 只有在首次初始化时才启动健康检查任务
            if self._health_check_task is None:
                self._health_check_task = asyncio.create_task(self._health_check_loop())
        return self.session_client is not None and self.business_client is not None
    
    async def shutdown(self):
        """关闭Redis连接"""
        # 设置关闭标记，防止断开连接时触发重连
        self._shutting_down = True
        
        # 取消健康检查任务
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            
        if self.session_pool:
            logger.info("正在关闭Redis会话连接...")
            await self.session_pool.disconnect()
        if self.business_pool:
            logger.info("正在关闭Redis业务连接...")
            await self.business_pool.disconnect()
        self.session_client = None
        self.business_client = None
        self.session_pool = None
        self.business_pool = None
        logger.info("Redis连接已关闭")

    async def _on_disconnect(self, db_type):
        """连接断开时的回调函数"""
        # 使用锁防止多协程同时重连
        async with self._reconnect_lock:
            # 检查程序是否正在主动关闭
            if hasattr(self, '_shutting_down') and self._shutting_down:
                return
            logger.warning(f"Redis {db_type} 连接已断开，准备重新连接")
            await self._connect()
    
    async def _connect(self):
        """创建Redis连接池和客户端"""
        try:
            # 基础连接参数
            base_connection_kwargs = {
                "host": self.redis_config["host"],
                "port": self.redis_config["port"],
                "password": self.redis_config["password"],
                "decode_responses": self.redis_config["decode_responses"],
                "socket_timeout": 5,
                "socket_connect_timeout": 5,
            }
            
            # 创建会话数据库连接
            session_connection_kwargs = base_connection_kwargs.copy()
            session_connection_kwargs["on_disconnect"] = lambda: self._on_disconnect("session")
            session_connection_kwargs["db"] = self.session_db
            
            self.session_pool = ConnectionPool(
                connection_class=RedisConnectionListener,
                health_check_interval=15,
                retry_on_timeout=True,
                max_connections=self.redis_config["max_connections"],
                **session_connection_kwargs
            )
            
            # 创建业务数据库连接
            business_connection_kwargs = base_connection_kwargs.copy()
            business_connection_kwargs["on_disconnect"] = lambda: self._on_disconnect("business")
            business_connection_kwargs["db"] = self.business_db
            
            self.business_pool = ConnectionPool(
                connection_class=RedisConnectionListener,
                health_check_interval=15,
                retry_on_timeout=True,
                max_connections=self.redis_config["max_connections"],
                **business_connection_kwargs
            )
            
            # 创建客户端实例
            self.session_client = Redis(connection_pool=self.session_pool)
            self.business_client = Redis(connection_pool=self.business_pool)
            
            # 测试连接是否成功
            await self.session_client.ping()
            await self.business_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            self.session_client = None
            self.business_client = None
            self.session_pool = None
            self.business_pool = None
    
    async def _health_check_loop(self):
        """后台任务定期检查连接状态"""
        while True:
            try:
                if self._shutting_down:
                    break
                
                if self.session_client and self.business_client:
                    await self.session_client.ping()
                    await self.business_client.ping()
                else:
                    await self._connect()
            except Exception as e:
                logger.warning(f"Redis健康检查失败，尝试重新连接: {str(e)}")
                await self._connect()
            
            # 每60秒检查一次
            await asyncio.sleep(60)
    
    def get_session_client(self):
        """获取用于会话管理的Redis客户端"""
        return self.session_client
    
    def get_business_client(self):
        """获取用于业务数据的Redis客户端"""
        return self.business_client

class AsyncRedisClientProxy:
    """异步Redis客户端代理类，实现懒加载"""
    def __init__(self, client_getter):
        self._client_getter = client_getter
        
    def __getattr__(self, name):
        # 当访问任何属性或方法时，确保先获取真实的客户端
        real_client = self._client_getter()
        if real_client is None:
            raise ConnectionError("Redis客户端未初始化")
        # 返回真实客户端的对应属性或方法
        return getattr(real_client, name)

# 创建实例但不立即初始化连接
redis_client = _RedisClient()
# 创建代理对象
session_client = AsyncRedisClientProxy(redis_client.get_session_client)
business_client = AsyncRedisClientProxy(redis_client.get_business_client)

class SyncRedisClient:
    """同步Redis客户端代理类，用于非异步环境"""
    def __init__(self, db_type):
        self._redis = None
        self._db_type = db_type
        
    def _ensure_connected(self):
        """确保Redis客户端已连接"""
        if self._redis is None:
            redis_config = config["redis"]
            
            # 确定使用哪个数据库
            if self._db_type == "session":
                db = redis_config["db"]["session"]
            else:  # business
                db = redis_config["db"]["business"]
                
            # 创建同步Redis客户端
            self._redis = SyncRedis(
                host=redis_config["host"],
                port=redis_config["port"],
                password=redis_config["password"],
                db=db,
                decode_responses=redis_config["decode_responses"],
                socket_timeout=5,
                socket_connect_timeout=5,
                health_check_interval=30,
            )
            # 测试连接
            try:
                self._redis.ping()
                logger.info(f"同步Redis {self._db_type} 客户端连接成功")
            except Exception as e:
                logger.error(f"同步Redis {self._db_type} 客户端连接失败: {str(e)}")
                self._redis = None
                raise
        return self._redis
    
    def __getattr__(self, name):
        """代理所有Redis客户端的方法和属性"""
        redis = self._ensure_connected()
        if redis is None:
            raise ConnectionError(f"同步Redis {self._db_type} 客户端未初始化")
        return getattr(redis, name)

# 创建同步业务客户端实例
sync_business_client = SyncRedisClient("business")