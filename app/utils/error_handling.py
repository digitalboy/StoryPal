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


def handle_error(code, message=None):
    """通用错误处理函数"""
    error_message = message if message else ERROR_CODES.get(code, "未知错误")
    response = {
        "code": code,
        "message": error_message,
        "data": None,
    }
    return jsonify(response), code
