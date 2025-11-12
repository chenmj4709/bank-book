from fastapi import WebSocket
from app.utils import get_logger, session_manager

logger = get_logger()

async def update_session(
    websocket: WebSocket, 
    **kwargs
) -> None:
    try:
        session_id = websocket.state.session_id
        
        await session_manager.update_session(
            session_id=session_id,
            **kwargs
        )
        
        websocket.state.session = await session_manager.get_session(session_id)
        logger.debug(f"已更新会话 {session_id} 并刷新WebSocket状态")

    except Exception as e:
        logger.error(f"更新会话和状态时出错: {str(e)}")
        raise