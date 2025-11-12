import inspect
from typing import Dict, Any
from app.utils import get_logger

logger = get_logger()

def handle_error(error: Dict[str, Any], message=None):
    """
    处理错误并记录日志
    
    Args:
        error: 错误对象，字典类型
        message: 额外的错误信息，默认为None
    
    Returns:
        错误对象，字典类型
    """
    # 获取调用者的信息
    caller_frame = inspect.currentframe().f_back
    caller_function = caller_frame.f_code.co_name
    caller_line = caller_frame.f_lineno
    
    # 获取调用者的模块路径
    caller_module = inspect.getmodule(caller_frame)
    module_path = caller_module.__name__ if caller_module else "unknown_module"
    
    # 构建日志信息
    log_message = f"{module_path}.{caller_function}:{caller_line}"
    if message:
        log_message += f" - {message}"
    
    # 记录日志
    logger.error(f"{log_message} - {error}")
    
    # 如果message有值，则返回一个新的错误对象
    if message:
        try:
            # 创建一个新字典并添加message
            new_error = error.copy()
                  
            # 设置新的错误信息
            new_error['errdetail'] = message
            
            return new_error
        except Exception as e:
            # 如果创建新对象失败，记录日志并返回原始错误
            logger.warning(f"创建新错误对象失败: {e}，返回原始错误")
            return error
    
    # 返回原始错误对象
    return error
