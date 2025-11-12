import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional
import inspect
from app.config import config

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 日志目录
LOG_DIR = os.path.join(ROOT_DIR, "logs")
# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)
# 统一的日志文件名
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# 创建全局文件处理器和控制台处理器
file_handler = None
console_handler = None

def get_logger(name: Optional[str] = None, level: int = config["log"]["level"]) -> logging.Logger:
    """
    设置并返回一个配置好的日志记录器
    
    Args:
        name: 日志记录器名称，默认为None（自动获取调用者的模块名称）
        level: 日志级别，默认为INFO
        
    Returns:
        配置好的日志记录器实例
    """
    global file_handler, console_handler
    
    # 如果没有提供名称，自动获取调用者的模块名称
    if name is None:
        # 获取调用者的帧
        caller_frame = inspect.stack()[1]
        # 获取调用者的模块
        caller_module = inspect.getmodule(caller_frame[0])
        # 获取调用者的模块名称
        name = caller_module.__name__ if caller_module else None
    
    # 获取指定名称的日志记录器
    logger = logging.getLogger(name)
    
    # 如果logger已经有处理器，说明已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 如果控制台处理器还没有创建，则创建它
    if console_handler is None:
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
    
    # 添加控制台处理器到logger
    logger.addHandler(console_handler)
    
    # 如果文件处理器还没有创建，则创建它
    if file_handler is None:
        # 创建按天切分的文件处理器
        file_handler = TimedRotatingFileHandler(
            filename=LOG_FILE,
            when='midnight',  # 每天午夜切分
            interval=1,       # 每1天切分一次
            backupCount=30,   # 保留30天的日志
            encoding='utf-8'  # 使用utf-8编码
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.suffix = "%Y-%m-%d"  # 日志文件后缀格式
    
    # 添加文件处理器到logger
    logger.addHandler(file_handler)
    
    return logger

# 创建一个默认的应用日志记录器
app_logger = get_logger("bank-book")