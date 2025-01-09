# filepath: app/utils/error_handling.py
from flask import jsonify

# 错误码定义
ERROR_CODES = {
    200: "成功",
    400: "请求参数错误",
    401: "未授权",
    403: "禁止访问",
    404: "资源未找到",
    422: "请求参数验证失败",
    429: "请求过多",
    500: "服务器内部错误",
}

# 扩展错误码
EXTENDED_ERROR_CODES = {
    4001: "缺少必填字段",
    4002: "字段类型错误",
    4003: "字段值超出范围",
    4011: "API Key 缺失",
    4012: "API Key 无效",
    4041: "场景未找到",
    4042: "字词未找到",
    4043: "故事未找到",
    4221: "生字率超出范围",
    4222: "目标级别超出范围",
    5001: "数据库连接失败",
    5002: "第三方服务调用失败",
}


def handle_error(code, message=None, extended_code=None):
    """通用错误处理函数"""
    error_message = message if message else ERROR_CODES.get(code, "未知错误")
    response = {
        "code": extended_code if extended_code else code,
        "message": error_message,
        "data": None,
    }
    return jsonify(response), code
