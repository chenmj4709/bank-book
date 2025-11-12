import uuid
import json
from datetime import datetime
from typing import Any, Dict, Optional
from app.utils import get_logger

logger = get_logger()

class SessionManager:
    def __init__(self, prefix: str = "BB:s:", expire_days: int = 180):
        self.prefix = prefix
        self.expire_seconds = expire_days * 24 * 60 * 60
        self._session_client = None
    
    @property # 使用装饰器
    def session_client(self):
        """懒加载 session_client，避免循环依赖"""
        if self._session_client is None:
            from app.services.redis import session_client
            self._session_client = session_client
        return self._session_client
    
    def _get_key(self, session_id: str) -> str:
        """获取完整的Redis键名"""
        return f"{self.prefix}{session_id}"
    
    async def create_session(self, **kwargs) -> tuple[str, dict]:
        """创建新会话并返回会话ID及内容"""
        session_id = str(uuid.uuid4())
        key = self._get_key(session_id)
        
        # 初始化会话数据
        session_data = {
            "created_at": datetime.now().astimezone().isoformat()
        }
        # 添加额外的关键字参数到会话数据中
        if kwargs:
            session_data.update(kwargs)

        # 存储到Redis
        await self.session_client.set(key, json.dumps(session_data), ex=self.expire_seconds)
        logger.info(f"创建新会话: {session_id}")
        return session_id, session_data
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话数据"""
        key = self._get_key(session_id)
        data = await self.session_client.get(key)
        
        if not data:
            logger.warning(f"会话不存在: {session_id}")
            return None

        # 更新过期时间
        await self.session_client.expire(key, self.expire_seconds)
        
        try:
            return json.loads(data)
        except Exception as e:
            logger.error(f"解析会话数据失败: {e}")
            return None
    
    async def update_session(self, session_id: str, **kwargs) -> bool:
        """更新会话数据，使用关键字参数更新会话"""
            
        key = self._get_key(session_id)
        data = await self.session_client.get(key)
        
        if not data:
            return False

        current_data = json.loads(data)
        
        # 直接使用kwargs更新会话数据
        current_data.update(kwargs)
        current_data["updated_at"] = datetime.now().astimezone().isoformat()
        
        # 保存回Redis
        await self.session_client.set(key, json.dumps(current_data), ex=self.expire_seconds)
        logger.info(f"更新会话: {session_id}")
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        key = self._get_key(session_id)
        result = await self.session_client.delete(key)
        return result > 0

# 创建全局会话管理器实例
session_manager = SessionManager()