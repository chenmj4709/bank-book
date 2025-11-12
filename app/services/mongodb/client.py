import asyncio
import threading
from datetime import datetime
import time
# 添加兼容层，为 Python 3.11 提供 coroutine 函数，兼容motor=2.5.1
import sys
if sys.version_info >= (3, 11):
    if not hasattr(asyncio, 'coroutine'):
        asyncio.coroutine = lambda f: f

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from pymongo import MongoClient
import pymongo
from pymongo.monitoring import ServerListener
from urllib.parse import quote_plus
from app.config import config
from app.utils import get_logger

logger = get_logger()

class _MongoDBClient:
    def __init__(self):
        self.mongodb_config = config["mongodb"]
        self.client = None
        self.async_client = None
        self._reconnect_lock = threading.Lock()
        self._health_check_thread = None
        self._shutting_down = False  # 添加关闭标记
        # 不再在初始化时连接和启动健康检查
        
    def initialize(self):
        """显式初始化MongoDB连接和健康检查"""
        if self.client is None:
            self._connect()
            
            # 只有在首次初始化时才启动健康检查线程
            if self._health_check_thread is None:
                self._health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
                self._health_check_thread.start()
        return self.client is not None
    
    def shutdown(self):
        """关闭MongoDB连接"""
        # 设置关闭标记，防止断开连接时触发重连
        self._shutting_down = True
        if self.client:
            logger.info("正在关闭MongoDB连接...")
            self.client.close()
        if self.async_client:
            logger.info("正在关闭MongoDB异步连接...")
            self.async_client.close()
        self.client = None
        self.async_client = None
        logger.info("MongoDB连接已关闭")

    def _connect(self):
        """连接到MongoDB数据库"""
        try:
            # 连接池配置
            max_pool_size = self.mongodb_config.get("max_pool_size", 100)
            min_pool_size = self.mongodb_config.get("min_pool_size", 10)
            max_idle_time_ms = self.mongodb_config.get("max_idle_time_ms", 60000)
            
            # 构建连接URI
            uri = self._build_connection_uri()
            
            # 注册事件监听器
            event_listener = self._get_event_listeners()
            pymongo.monitoring.register(event_listener)
            
            # 获取系统当前时区
            tz_info = datetime.now().astimezone().tzinfo
            
            # 创建同步客户端（用于健康检查）
            self.client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=max_pool_size,
                minPoolSize=min_pool_size,
                maxIdleTimeMS=max_idle_time_ms,
                tz_aware=True,
                tzinfo=tz_info,
            )
            
            # 创建异步客户端
            self.async_client = AsyncIOMotorClient(
                uri,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=max_pool_size,
                minPoolSize=min_pool_size,
                maxIdleTimeMS=max_idle_time_ms,
                tz_aware=True,
                tzinfo=tz_info,
            )
            
            # 获取默认数据库
            self.db = self.client[self.mongodb_config["db"]]
            self.async_db = self.async_client[self.mongodb_config["db"]]
            
            logger.info("MongoDB连接成功")
        except Exception as e:
            logger.error(f"MongoDB连接失败: {str(e)}")
            self.client = None
            self.async_client = None
    
    def _build_connection_uri(self):
        """构建MongoDB连接URI"""
        host = self.mongodb_config["host"]
        port = self.mongodb_config["port"]
        db = self.mongodb_config["db"]
        username = self.mongodb_config.get("username")
        password = self.mongodb_config.get("password")
        
        if username and password:
            return f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{host}:{port}/{db}"
        else:
            return f"mongodb://{host}:{port}/{db}"
    
    def _get_event_listeners(self):
        """创建MongoDB事件监听器"""
        class CustomServerListener(ServerListener):
            def __init__(self, client_instance):
                self.client_instance = client_instance
                
            def server_closed(self, event):
                logger.warning(f"MongoDB服务器连接关闭: {event.server_address}")
                self.client_instance._handle_connection_failure()
                
            def description_changed(self, event):
                if event.new_description.error is not None:
                    logger.warning(f"MongoDB服务器连接状态变更: {event.server_address}")
                    self.client_instance._handle_connection_failure()
            
            def opened(self, event):
                # logger.info(f"MongoDB服务器连接已打开: {event.server_address}")
                pass
                
            def topology_opened(self, event):
                logger.info(f"MongoDB拓扑已打开: {event.topology_id}")
                
            def topology_closed(self, event):
                logger.info(f"MongoDB拓扑已关闭: {event.topology_id}")
                
            def topology_description_changed(self, event):
                logger.debug(f"MongoDB拓扑描述已更改: {event.topology_id}")
                
        return CustomServerListener(self)
        
    def _handle_connection_failure(self):
        """处理连接失败事件"""
        # 使用锁防止多线程同时重连
        if self._reconnect_lock.acquire(blocking=False):
            try:
                # 检查程序是否正在主动关闭
                if hasattr(self, '_shutting_down') and self._shutting_down:
                    return
                
                if self.client:
                    try:
                        # 尝试ping服务器，检查连接是否真的断开
                        self.client.admin.command('ping')
                        return  # 连接仍然有效
                    except (ServerSelectionTimeoutError, ConnectionFailure):
                        logger.info("检测到MongoDB连接断开，尝试重新连接")
                        self._connect()
            finally:
                self._reconnect_lock.release()
    
    def _health_check_loop(self):
        """后台线程定期检查连接状态"""
        while True:
            try:
                if self._shutting_down:
                    break
                    
                if self.client:
                    # 使用admin命令检查连接状态
                    self.client.admin.command('ping')
                else:
                    self._connect()
            except Exception as e:
                logger.warning(f"MongoDB健康检查失败，尝试重新连接: {str(e)}")
                if not self._shutting_down:
                    self._connect()
            
            # 每60秒检查一次
            time.sleep(60)
    
    async def ping(self):
        """异步检查连接状态"""
        if not self.async_client:
            return False
        try:
            await self.async_client.admin.command('ping')
            return True
        except Exception:
            return False
    
    def get_collection(self, collection_name):
        """获取同步集合对象"""
        if not self.client:
            self._connect()
        return self.db[collection_name]
    
    def get_async_collection(self, collection_name):
        """获取异步集合对象"""
        if not self.async_client:
            self._connect()
        return self.async_db[collection_name]

class MongoDBProxy:
    """MongoDB客户端代理类，实现懒加载"""
    def __init__(self, client_getter):
        self._client_getter = client_getter
        
    def __getattr__(self, name):
        # 当访问任何属性或方法时，确保先获取真实的客户端
        real_client = self._client_getter()
        if real_client is None:
            raise ConnectionError("MongoDB客户端未初始化")
        # 返回真实客户端的对应属性或方法
        return getattr(real_client, name)

# 创建实例但不立即初始化连接
mongodb_client = _MongoDBClient()
# 创建代理对象
db = MongoDBProxy(lambda: mongodb_client.db)
async_db = MongoDBProxy(lambda: mongodb_client.async_db)