from fastapi import Request
from fastapi import HTTPException
from app.define import ErrorCode

async def auth_user(request: Request) -> str:
    """
    验证用户并返回用户ID
    如果未登录，则抛出异常
    """
    # 检查请求状态中是否有用户会话
    user_session = getattr(request.state, "session", None)

    if not user_session:
        raise HTTPException(status_code=401, detail={"errcode": ErrorCode.AUTH_FAILED["errcode"], "errmsg": "未登录或会话已过期"})

    user_id = request.state.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail={"errcode": ErrorCode.AUTH_FAILED["errcode"], "errmsg": "未授权"})
    return user_id
    