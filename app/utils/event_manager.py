from typing import Dict, List, Callable
import asyncio

class EVENTS:
    SEND_RESPONSE = "send_response"             # 发送回复
    
class EventManager:
    """基于装饰器的事件管理器"""
    
    _instance = None
    _events: Dict[str, List[Callable]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def on(cls, event_name: str):
        """事件监听装饰器"""
        def decorator(func):
            if event_name not in cls._events:
                cls._events[event_name] = []
            cls._events[event_name].append(func)
            return func
        return decorator
    
    @classmethod
    async def emit(cls, event_name: str, *args, **kwargs):
        """触发事件"""
        if event_name not in cls._events:
            return
            
        tasks = []
        for handler in cls._events[event_name]:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(asyncio.create_task(handler(*args, **kwargs)))
            else:
                handler(*args, **kwargs)
                
        if tasks:
            await asyncio.gather(*tasks)

# 创建事件管理器实例
event_manager = EventManager()