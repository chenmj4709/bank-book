import bcrypt
import os
from typing import Optional
from datetime import datetime
from app.services.mongodb import User
from app.utils import get_logger, session_manager

logger = get_logger()

async def get_user_by_mobile(mobile: str) -> Optional[User]:
    return await User.find_one({"mobile": mobile})

async def login_user(user: User):
    now = datetime.now().astimezone()
    user.last_login_date = now
    await user.save()

    session_id, session_data = await session_manager.create_session(user_id=user.id, mobile=user.mobile)

    return session_id, session_data

async def logout_user(user_id: str, session_id: str):
    now = datetime.now().astimezone()
    await User.find_one_and_update({"_id": user_id}, {"$set": {"last_logout_date": now}})
    await session_manager.delete_session(session_id)

async def get_user_profile(user_id: str) -> Optional[dict]:
    user = await User.find_one({"_id": user_id})
    if not user:
        logger.warning(f"获取用户失败: 用户ID '{user_id}' 不存在")
        return None

    return {
        "id": user.id,
        "name": user.name,
        "mobile": user.mobile
    }

async def create_user(mobile: str, password: str):
    # 检查用户是否已存在
    existing = await User.find_one({"mobile": mobile})
    if existing:
        logger.warning(f"创建用户失败: 手机号 '{mobile}' 已存在")
        raise ValueError(f"手机号 '{mobile}' 已存在")

    # 创建密码哈希和盐
    password_hash, salt = _create_password_hash(password)
    
    user = User(mobile=mobile, password_hash=password_hash, salt=salt)
    await user.save()

    return user

def _create_password_hash(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = os.urandom(16).hex()  # 生成随机盐
    
    # 使用bcrypt加密密码
    password_bytes = (password + salt).encode('utf-8')
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    return password_hash, salt

async def verify_password(user: User, password: str) -> bool:
    password_bytes = (password + user.salt).encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, user.password_hash.encode('utf-8')).decode('utf-8')
    
    return hashed == user.password_hash 