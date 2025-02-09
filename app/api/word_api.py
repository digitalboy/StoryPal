# app/api/word_api.py
from flask import Blueprint, request, jsonify
from app.services.word_service import WordService
from app.utils.error_handling import handle_error
from app.utils.api_key_auth import api_key_required
import logging
import math

word_api = Blueprint("word_api", __name__, url_prefix="/api/v1/words")

# 初始化 WordService
word_service = WordService()


@word_api.route("", methods=["GET"])
@api_key_required
def get_words():
    """
    获取词语列表
    """
    try:
        chaotong_level = request.args.get("chaotong_level")
        part_of_speech = request.args.get("part_of_speech")
        page = request.args.get("page", default=1)
        page_size = request.args.get("page_size", default=10)
        below_level = request.args.get("below_level")

        # 类型验证和默认值处理
        try:
            if page:
                page = int(page)
            else:
                page = 1  # 默认为 1
            if page < 1:
                return handle_error(400, "Invalid page number, must be >= 1")
        except ValueError:
            return handle_error(400, "Invalid page number, must be an integer")

        try:
            if page_size:
                page_size = int(page_size)
            else:
                page_size = 10  # 默认为 10
            if page_size < 1:
                return handle_error(400, "Invalid page size, must be >= 1")
        except ValueError:
            return handle_error(400, "Invalid page size, must be an integer")

        try:
            if chaotong_level:
                chaotong_level = int(chaotong_level)
                if not 1 <= chaotong_level <= 100:
                    return handle_error(
                        400, "Invalid chaotong_level, must be between 1 and 100"
                    )
            else:
                chaotong_level = None  # 允许为空
        except ValueError:
            return handle_error(
                400, "Invalid chaotong_level, must be an integer"
            )  # 验证失败

        try:
            if below_level:
                below_level = int(below_level)
                if not 1 <= below_level <= 100:
                    return handle_error(
                        400, "Invalid below_level, must be between 1 and 100"
                    )
            else:
                below_level = None  # 允许为空
        except ValueError:
            return handle_error(400, "Invalid below_level, must be an integer")

        if chaotong_level is not None and below_level is not None:
            return handle_error(
                400, "Cannot use both 'chaotong_level' and 'below_level' parameters"
            )

        if below_level is not None:
            words = word_service.get_words_below_level(below_level)
            word_list = [word.to_dict() for word in words]
            return jsonify(
                {
                    "code": 200,
                    "message": "Words retrieved successfully",
                    "data": {
                        "words": word_list,
                        "total": len(word_list),
                        "page": 1,
                        "page_size": len(word_list),
                        "total_pages": 1,
                    },
                }
            )
        else:
            words = word_service.get_words(chaotong_level, page, page_size)
            total = word_service.get_total_words(chaotong_level)
            word_list = [word.to_dict() for word in words]
            total_pages = math.ceil(total / page_size)
            return jsonify(
                {
                    "code": 200,
                    "message": "Words retrieved successfully",
                    "data": {
                        "words": word_list,
                        "total": total,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": total_pages,
                    },
                }
            )
    except Exception as e:
        logging.error(f"Error getting words: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")
