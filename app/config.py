import os
import logging
from typing import Dict, Any

# 获取当前环境，默认为开发环境
ENV = os.environ.get("BB_ENV", "development")

# 基础配置
BASE_CONFIG = {
    "log": {
        "level": logging.INFO
    }
}

# 开发环境配置
DEV_CONFIG = {
    "redis": {
        "host": "120.0.0.1",
        "port": 6479,
        "db": {
            "session": 0,
            "business": 1
        },
        "password": "123456",
        "decode_responses": True,
        "max_connections": 50
    },
    "mongodb": {
        "host": "120.0.0.1",
        "port": 7017,
        "db": "bank-book-dev",
        "username": "bank-book-dev",
        "password": "123456",
        "connection_timeout_ms": 5000,
        "max_pool_size": 30,
        "min_pool_size": 10
    }
}

# 生产环境配置
PROD_CONFIG = {
    "redis": {
        "host": "120.0.0.1",
        "port": 6479,
        "db": {
            "session": 0,
            "business": 1
        },
        "password": "123456",
        "decode_responses": True,
        "max_connections": 100
    },
    "mongodb": {
        "host": "120.0.0.1",
        "port": 7017,
        "db": "bank-book",
        "username": "bank-book",
        "password": "123456",
        "connection_timeout_ms": 5000,
        "max_pool_size": 30,
        "min_pool_size": 10
    }
}

# 根据环境选择配置
def get_config() -> Dict[str, Any]:
    """根据当前环境返回相应的配置"""
    if ENV == "production":
        env_config = PROD_CONFIG
        print("加载生产环境配置")
    else:  # 默认使用开发环境
        env_config = DEV_CONFIG
        print("加载开发环境配置")
    
    base_config = {**BASE_CONFIG}
    
    # 递归合并配置
    def deep_merge(base, override):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                deep_merge(base[key], value)
            else:
                base[key] = value
    
    deep_merge(base_config, env_config)
    return base_config

config = get_config()
