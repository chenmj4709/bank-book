import re
import random
from datetime import datetime

def validate_phone_number(phone_number):
    """
    校验中国大陆手机号码
    
    Args:
        phone_number (str): 需要校验的手机号码
        
    Returns:
        bool: 如果是有效的手机号码返回True，否则返回False
    """
    # 中国大陆手机号码格式: 1开头的11位数字
    pattern = r'^1[3-9]\d{9}$'
    if re.match(pattern, phone_number):
        return True
    return False

def gen_verification_code(length=4):
    """
    生成指定长度的数字验证码
    
    Args:
        length (int, optional): 验证码长度，默认为4
        
    Returns:
        str: 生成的验证码
    """
    # 生成指定长度的随机数字
    code = ''.join(random.choice('0123456789') for _ in range(length))
    return code

def dict_to_sort_list(sort_dict: dict) -> list:
    return [(k, v) for k, v in sort_dict.items()]

def value_to_int(data, key, default=0):
    """返回数字类型"""
    try:
        value = data.get(key, default)
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default
        return default
    except (AttributeError, TypeError):
        return default

def json_format(json_str):
    """
    修复JSON字符串中的引号问题，将单引号替换为双引号
    
    Args:
        json_str (str): 需要修复的JSON字符串
        
    Returns:
        str: 修复后的JSON字符串
    """
    # 使用正则表达式替换键名的单引号
    # 匹配模式: '键名': 或 '键名' :
    json_str = re.sub(r"'(\w+)'(\s*):", r'"\1"\2:', json_str)
    
    # 替换字符串值的单引号
    # 匹配模式: : '值' 或 :'值'
    json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
    
    # 处理数组中的单引号字符串
    # 匹配模式: ['值'] 或 [ '值' ]
    json_str = re.sub(r"\[\s*'([^']*)'\s*\]", r'["\1"]', json_str)
    json_str = re.sub(r",\s*'([^']*)'", r', "\1"', json_str)
    json_str = re.sub(r"\[\s*'([^']*)'", r'["\1"', json_str)
    
    return json_str

def to_local_timezone(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return dt.astimezone(datetime.now().astimezone().tzinfo)
