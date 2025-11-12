"""
错误码定义模块
提供统一的错误码和错误消息定义
"""

class ErrorCode:
    """错误码定义类"""
    
    # 成功
    OK = {
        'errcode': 0,
        'errmsg': ''
    }
    
    # 通用错误 (1xxxx)
    UNKNOWN_ERROR = {
        'errcode': 10000,
        'errmsg': '未知错误'
    }
    INVALID_PARAMS = {
        'errcode': 10001,
        'errmsg': '无效的参数'
    }
    AUTH_FAILED = {
        'errcode': 10002,
        'errmsg': '认证失败'
    }
    SESSION_EXPIRED = {
        'errcode': 10003,
        'errmsg': '会话已过期'
    }
    RESOURCE_NOT_FOUND = {
        'errcode': 10004,
        'errmsg': '资源不存在'
    }
    INVALID_MOBILE = {
        'errcode': 10005,
        'errmsg': '无效的手机号码'
    }
    
    # 数据库相关错误 (2xxxx)
    DATABASE_ERROR = {
        'errcode': 20000,
        'errmsg': '数据库错误'
    }
    REDIS_ERROR = {
        'errcode': 20001,
        'errmsg': 'Redis错误'
    }
    DATA_ALREADY_EXISTS = {
        'errcode': 20002,
        'errmsg': '数据已存在'
    }
    DATA_NOT_FOUND = {
        'errcode': 20003,
        'errmsg': '数据不存在'
    }
    PERMISSION_DENIED = {
        'errcode': 20004,
        'errmsg': '无权限'
    }
    
    # 业务错误 (3xxxx)
    BUSINESS_ERROR = {
        'errcode': 30000,
        'errmsg': '业务错误'
    }
    OPERATION_FAILED = {
        'errcode': 30001,
        'errmsg': '操作失败'
    }
    SMS_VERIFY_ERROR = {
        'errcode': 30002,
        'errmsg': '发送短信验证码失败'
    }
