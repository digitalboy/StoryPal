# app/api/word_api.py
from flask import Blueprint, request, jsonify
from app.services.word_service import WordService
from app.utils.error_handling import handle_error
from app.utils.api_key_auth import api_key_required
import logging

word_api = Blueprint("word_api", __name__, url_prefix="/api/v1/words")

# 初始化 WordService
word_service = WordService()


@word_api.route("", methods=["GET"])
@api_key_required
def get_words():
    """
    获取字词列表
    """
    try:
        level = request.args.get("level", type=int)
        part_of_speech = request.args.get("part_of_speech")
        page = request.args.get("page", default=1, type=int)
        page_size = request.args.get("page_size", default=10, type=int)
        below_level = request.args.get("below_level", type=int)

        if page < 1:
            return handle_error(400, "Invalid page number")
        if page_size < 1:
            return handle_error(400, "Invalid page size")

        if level is not None and below_level is not None:
            return handle_error(
                400, "Cannot use both 'level' and 'below_level' parameters"
            )

        if below_level is not None:
            words = word_service.get_words_below_level(below_level, part_of_speech)
            word_list = [word.to_dict() for word in words]
            return jsonify(
                {
                    "code": 200,
                    "message": "Words retrieved successfully",
                    "data": {"words": word_list, "total": len(word_list)},
                }
            )
        else:
            words = word_service.get_words(level, part_of_speech, page, page_size)
            total = word_service.get_total_words(level, part_of_speech)
            word_list = [word.to_dict() for word in words]
            return jsonify(
                {
                    "code": 200,
                    "message": "Words retrieved successfully",
                    "data": {"words": word_list, "total": total},
                }
            )
    except Exception as e:
        logging.error(f"Error getting words: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")
