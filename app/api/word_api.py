# app/api/word_api.py
from flask import Blueprint, request, jsonify
from app.services.word_service import WordService
from app.utils.error_handling import handle_error
from app.utils.api_key_auth import api_key_required
import logging

word_api = Blueprint("word_api", __name__, url_prefix="/v1/words")
word_service = WordService()


@word_api.route("", methods=["GET"])
@api_key_required
def list_words():
    """
    根据条件查询字词。
    """
    level = request.args.get("level", type=int)
    part_of_speech = request.args.get("part_of_speech")
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)

    if page < 1 or page_size < 1:
        return handle_error(4003, "页码和每页大小必须是大于 0 的整数")

    try:
        words = word_service.list_words(level, part_of_speech, page, page_size)
        total = len(word_service.list_words(level, part_of_speech))

        words_data = [word.to_dict() for word in words]

        return jsonify(
            {
                "code": 200,
                "message": "Words retrieved successfully",
                "data": {"words": words_data, "total": total},
            }
        )
    except Exception as e:
        logging.error(f"Error while listing words: {e}")
        return handle_error(5001, f"Internal server error: {str(e)}")
