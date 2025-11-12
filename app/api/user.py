from typing import Dict, Any
from fastapi import APIRouter, Request, Body, Depends
from app.middlewares.inject import auth_user
from app.services import user as user_service
from app.utils import get_logger, handle_error
from app.define import ErrorCode

logger = get_logger()

router = APIRouter()

@router.post("/user/login")
async def login_user(
    request: Request,
    body: Dict[str, Any] = Body(...)
):
    mobile = body.get("mobile")
    password = body.get("password")

    if not mobile or not password:
        return handle_error(ErrorCode.INVALID_PARAMS)

    user = await user_service.get_user_by_mobile(mobile)
    if not user:
        return handle_error(ErrorCode.AUTH_FAILED, "用户不存在")
    
    # 校验密码
    if not await user_service.verify_password(user, password):
        return handle_error(ErrorCode.AUTH_FAILED, "密码错误")

    session_id, session_data = await user_service.login_user(user)

    # 将会会话ID存储到请求状态中
    request.state.session_id = session_id
    request.state.session = session_data

    return {
        "id": user.id,
        "name": user.name,
        "mobile": user.mobile
    }

@router.post("/user/logout")
async def logout_user(
    request: Request,
    user_id: str = Depends(auth_user),
):
    await user_service.logout_user(user_id=user_id, session_id=request.state.session_id)

    return {}

@router.post("/user/get")
async def get_user(
    user_id: str = Depends(auth_user),
):
    result = await user_service.get_user_profile(user_id=user_id)

    return result