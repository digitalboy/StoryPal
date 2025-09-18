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
        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order", default="asc")

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
                if not 1 <= chaotong_level <= 350:
                    return handle_error(
                        400, "Invalid chaotong_level, must be between 1 and 350"
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
                if not 1 <= below_level <= 350:
                    return handle_error(
                        400, "Invalid below_level, must be between 1 and 350"
                    )
            else:
                below_level = None  # 允许为空
        except ValueError:
            return handle_error(400, "Invalid below_level, must be an integer")

        # 排序参数验证
        if sort_by and sort_by not in ["part_of_speech", "chaotong_level"]:
            return handle_error(
                400,
                "Invalid 'sort_by' parameter. Allowed values are 'part_of_speech', 'chaotong_level'.",
            )

        if sort_order not in ["asc", "desc"]:
            return handle_error(
                400, "Invalid 'sort_order' parameter. Allowed values are 'asc', 'desc'."
            )

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
            words = word_service.get_words(
                chaotong_level=chaotong_level,
                part_of_speech=part_of_speech,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            total = word_service.get_total_words(
                chaotong_level=chaotong_level, part_of_speech=part_of_speech
            )
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


@word_api.route("", methods=["POST"])
@api_key_required
def create_word():
    """
    创建词汇
    """
    try:
        data = request.get_json()
        if not data:
            return handle_error(400, "Missing request body")

        word = data.get("word")
        chaotong_level = data.get("chaotong_level")
        part_of_speech = data.get("part_of_speech")
        hsk_level = data.get("hsk_level")  # 可选

        if not word:
            return handle_error(400, "Missing required field: word")
        if chaotong_level is None:
            return handle_error(400, "Missing required field: chaotong_level")
        if not part_of_speech:
            return handle_error(400, "Missing required field: part_of_speech")

        # 类型验证
        if not isinstance(word, str):
            return handle_error(400, "Invalid field type: 'word' must be a string")
        if not isinstance(chaotong_level, int):
            return handle_error(
                400, "Invalid field type: 'chaotong_level' must be an integer"
            )
        if not isinstance(part_of_speech, str):
            return handle_error(
                400, "Invalid field type: 'part_of_speech' must be a string"
            )
        if hsk_level is not None and not isinstance(hsk_level, (int, float)):
            return handle_error(400, "Invalid field type: 'hsk_level' must be a number")

        new_word = word_service.create_word(
            word=word,
            chaotong_level=chaotong_level,
            part_of_speech=part_of_speech,
            hsk_level=hsk_level,
        )

        return jsonify(
            {
                "code": 200,
                "message": "Word created successfully",
                "data": new_word.to_dict(),
            }
        )
    except Exception as e:
        logging.error(f"Error creating word: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")


@word_api.route("/<word_id>", methods=["DELETE"])
@api_key_required
def delete_word(word_id):
    """
    删除词汇
    """
    try:
        if word_service.delete_word(word_id):
            return jsonify(
                {
                    "code": 200,
                    "message": "Word deleted successfully",
                    "data": None,
                }
            )
        else:
            return handle_error(404, "Word not found")
    except Exception as e:
        logging.error(f"Error deleting word: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")
