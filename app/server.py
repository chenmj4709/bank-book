import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse, HTMLResponse
import app.api as api_routers
from app.utils import get_logger
from app.services.redis import redis_client
from app.services.mongodb import mongodb_client
from app.services.scheduler import init_scheduler, shutdown_scheduler

from app.middlewares import SessionMiddleware, ApiResponseMiddleware

logger = get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("正在初始化应用...")
    # 初始化Redis连接
    if await redis_client.initialize():
        logger.info("Redis初始化成功")
    else:
        logger.error("Redis初始化失败")
    # 初始化MongoDB连接
    if mongodb_client.initialize():
        logger.info("MongoDB初始化成功")
    else:
        logger.error("MongoDB初始化失败")
    # 初始化定时任务调度器
    if await init_scheduler():
        logger.info("定时任务调度器初始化成功")
    else:
        logger.error("定时任务调度器初始化失败")
    
    yield  # FastAPI serves requests
    
    # Shutdown
    logger.info("正在关闭应用...")
    # 关闭定时任务调度器
    await shutdown_scheduler()
    # 关闭Redis连接
    await redis_client.shutdown()
    # 关闭MongoDB连接
    mongodb_client.shutdown()

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# 添加会话中间件 - 所有路由都会经过这个中间件
app.add_middleware(SessionMiddleware)
# 添加响应中间件 - 统一处理API返回格式, 只拦截/api开头的路由
app.add_middleware(ApiResponseMiddleware)

# 创建api路由并设置前缀
api_router = APIRouter(prefix="/api")
# 添加api路由
# 简化路由添加，通过循环自动添加所有路由
for router_name in api_routers.__all__:
    router = getattr(api_routers, router_name)
    api_router.include_router(router)

# 将api路由包含到 FastAPI 应用中
app.include_router(api_router)

# 定义静态文件扩展名列表
STATIC_FILE_EXTENSIONS = ['.js', '.css', '.svg', '.png', '.jpg', '.gif', 
                         '.woff', '.woff2', '.eot', '.ttf', '.ico', '.html', 'txt']

# 处理前端路由和静态文件
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # 静态文件目录路径
    static_dir = Path("app/static")
    # 请求的文件路径
    file_path = static_dir / full_path if full_path else static_dir / "index.html"
    
    # 检查是否为静态文件
    is_static_file = any(full_path.endswith(ext) for ext in STATIC_FILE_EXTENSIONS)
    
    # 如果是静态文件且文件存在，直接返回文件
    if is_static_file and file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # 对于其他所有路径，返回index.html以支持Vue路由
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return HTMLResponse(content="找不到前端文件", status_code=404)

if __name__ == "__main__":
    import uvicorn
    import threading
    
    # 使用Path模块处理证书路径
    parent_dir = Path(__file__).parent
    cert_path = os.path.join(parent_dir, "certs", "fullchain.pem")
    key_path = os.path.join(parent_dir, "certs", "privkey.pem")
    
    # 定义启动HTTPS服务器的函数
    def start_https_server():
        logger.info("启动HTTPS服务器在端口8301...")
        uvicorn.run(
            "app.server:app", 
            host="0.0.0.0", 
            port=8301, 
            ssl_keyfile=key_path,
            ssl_certfile=cert_path,
            reload=False  # HTTPS服务器不使用reload，避免与HTTP服务器冲突
        )
    
    # 在新线程中启动HTTPS服务器
    https_thread = threading.Thread(target=start_https_server)
    https_thread.daemon = True  # 设置为守护线程，主线程结束时自动结束
    https_thread.start()
    
    # 在主线程中启动HTTP服务器
    logger.info("启动HTTP服务器在端口8300...")
    uvicorn.run("app.server:app", host="0.0.0.0", port=8300, reload=True, reload_dirs=["app"])
