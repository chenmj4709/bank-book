from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils import get_logger, session_manager

logger = get_logger()

class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cookie_name: str = "bb_session", cookie_max_age: int = 180):
        super().__init__(app)
        self.cookie_name = cookie_name
        # cookie过期时间（天）
        self.cookie_max_age = cookie_max_age * 24 * 60 * 60
    
    async def dispatch(self, request: Request, call_next):
        # 尝试从cookie中获取会话ID
        session_id = request.cookies.get(self.cookie_name)

        # 如果有会话ID，尝试获取会话数据
        session_data = None
        if session_id:
            session_data = await session_manager.get_session(session_id)
            logger.info(f"获取到的会话数据: {session_data}")
        
        # 将会话ID添加到请求状态中，以便路由处理函数使用
        request.state.session_id = session_id
        request.state.session = session_data

        # 处理请求
        response = await call_next(request)
        
        # 如果有管理员会话ID，在响应中设置cookie
        if getattr(request.state, "session_id", None):
            # 在响应中设置cookie
            response.set_cookie(
                key=self.cookie_name,
                value=request.state.session_id,
                max_age=self.cookie_max_age,
                httponly=True,  # 防止JavaScript访问
                samesite="lax",  # 防止CSRF攻击
                path="/",        # 适用于整个网站
            )
        
        return response
