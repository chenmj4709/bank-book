import json
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, _StreamingResponse
from app.define.errcode import ErrorCode
from app.utils import get_logger

logger = get_logger()

class ApiResponseMiddleware(BaseHTTPMiddleware):
    """
    API响应中间件
    用于统一处理API返回格式:
    - 正常返回: {"errcode": 0, "ret": 原始返回内容}
    - 异常返回: {"errcode": 错误码, "errmsg": 错误信息}
    """
    
    def _is_already_wrapped(self, response_data):
        """检查响应是否已经被包装"""
        return isinstance(response_data, dict) and "errcode" in response_data

    def _is_http_exception(self, response_data):
        """检查响应是否已经被包装"""
        return isinstance(response_data, dict) and "detail" in response_data and "errcode" in response_data.get("detail", {})
    
    def _clean_headers(self, headers):
        """清理headers，移除content-length"""
        headers = dict(headers)
        if "content-length" in headers:
            del headers["content-length"]
        return headers
    
    def _create_wrapped_response(self, response_data, status_code, headers):
        """创建包装后的响应"""
        # 直接使用_is_already_wrapped方法检查
        if self._is_already_wrapped(response_data):
            return JSONResponse(
                content=response_data,
                status_code=status_code,
                headers=headers
            )

        # 处理HTTPException
        if self._is_http_exception(response_data):
            response_data = response_data.get("detail", {})
            return JSONResponse(
                content=response_data,
                status_code=status_code,
                headers=headers
            )
        
        wrapped_response = {
            "errcode": ErrorCode.OK["errcode"],
            "ret": response_data
        }
        
        return JSONResponse(
            content=wrapped_response,
            status_code=status_code,
            headers=headers
        )
    
    async def dispatch(self, request: Request, call_next):   
        try:
            # 调用下一个中间件或路由处理函数
            response = await call_next(request)
            # 如果是流式响应但内容是JSONResponse，尝试提取并处理
            if isinstance(response, _StreamingResponse):
                # 检查响应的媒体类型是否为JSON
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    # 读取响应内容
                    response_body = b""
                    async for chunk in response.body_iterator:
                        response_body += chunk
                    
                    # 解析JSON内容
                    try:
                        response_data = json.loads(response_body)
                        headers = self._clean_headers(response.headers)
                        return self._create_wrapped_response(response_data, response.status_code, headers)
                    except json.JSONDecodeError:
                        # 如果不是有效的JSON，直接返回原始响应
                        return response
                
                # 如果不是JSON内容类型，直接返回
                return response
            
            # 如果不是JSON响应，则直接返回
            if not isinstance(response, JSONResponse):
                return response
            
            # 获取原始响应内容
            response_data = json.loads(response.body)
            
            # 使用封装的方法创建包装响应
            headers = dict(response.headers)
            return self._create_wrapped_response(response_data, response.status_code, headers)
        except Exception as e:
            # 记录异常
            logger.error(f"API处理异常: {str(e)}")
            
            # 默认错误信息
            error_info = ErrorCode.UNKNOWN_ERROR
            
            # 返回错误响应
            return JSONResponse(
                content=error_info,
                status_code=500
            )
   