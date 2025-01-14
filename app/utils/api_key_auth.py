# app/utils/api_key_auth.py
from functools import wraps
from flask import request, jsonify
from app.utils.error_handling import handle_error
from app.config import get_api_key_from_config
import logging


def api_key_required(func):
    """
    API Key 认证装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("Authorization")
        if not api_key or not api_key.startswith("Bearer "):
            logging.warning("API Key missing")
            return handle_error(401, "API Key missing")
        api_key = api_key[7:]  # Remove "Bearer " prefix
        if api_key != get_api_key_from_config():
            logging.warning("Invalid API Key")
            return handle_error(401, "Invalid API Key")
        return func(*args, **kwargs)

    return wrapper
