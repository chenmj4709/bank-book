from fastapi import APIRouter, Request
from app.services.redis import business_client
from app.services import user as user_service
from app.services.mongodb.models.user import User
from app.utils import get_logger

logger = get_logger()

router = APIRouter()

@router.get("/example")
async def example(request: Request):
    return {
        "ret": "example_response",
        "session_id": request.state.session_id,
        "session_data": request.state.session
    }

@router.get("/base/health")
async def health(request: Request):
    return {
        "ret": "health_response"
    }

@router.get("/redis-test")
async def test_redis():
    logger.debug("test_redis")

    # 设置测试数据
    test_key = "test:key"
    test_value = "Hello Redis!"
    await business_client.set(test_key, test_value)

    # 读取测试数据
    retrieved_value = await business_client.get(test_key)

    # 返回测试结果
    return {
        "key": test_key,
        "set_value": test_value,
        "retrieved_value": retrieved_value,
        "success": test_value == retrieved_value
    }

@router.get("/mongodb-test")
async def test_mongodb():
    logger.debug("test_mongodb")
    mobile = "4709"
    password = "111111"

    # 查询
    user = await User.find_one({
        "mobile": mobile
    })

    # 如果不存在，则创建
    if not user:
        user = await user_service.create_user(mobile, password)
        logger.info("Created new user with mobile=%s", mobile)
    else:
        logger.info("Found existing user with mobile=%s", mobile)

    # 返回
    return user
