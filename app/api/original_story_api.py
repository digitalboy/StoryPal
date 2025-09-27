# app/api/original_story_api.py
from flask import Blueprint, request, jsonify
from app.services.original_story_service import OriginalStoryService
from app.utils.error_handling import handle_error
from app.utils.api_key_auth import api_key_required
import logging
import math

original_story_api = Blueprint(
    "original_story_api", __name__, url_prefix="/api/v1/original-stories"
)

# 初始化 OriginalStoryService
original_story_service = OriginalStoryService()


@original_story_api.route("", methods=["GET"])
@api_key_required
def get_stories_by_level():
    """
    根据级别获取所有旧有故事，支持分页
    """
    try:
        level_str = request.args.get("level")
        if not level_str:
            return handle_error(400, "Missing required query parameter: level")

        try:
            level = int(level_str)
            page = int(request.args.get("page", 1))
            page_size = int(request.args.get("page_size", 10))
        except (ValueError, TypeError):
            return handle_error(400, "level, page and page_size must be integers.")

        stories = original_story_service.get_stories_by_level(
            level=level, page=page, page_size=page_size
        )
        total = original_story_service.get_total_stories_by_level(level=level)

        stories_data = [
            {
                "id": story.id,
                "name": story.name,
                "level": story.level,
                "content": story.content,
                "tokenized_content": story.tokenized_content,
                "unknown_word_ratio": story.unknown_word_ratio,
                "created_at": (
                    story.created_at.isoformat() if story.created_at else None
                ),
                "updated_at": (
                    story.updated_at.isoformat() if story.updated_at else None
                ),
            }
            for story in stories
        ]

        return jsonify(
            {
                "code": 200,
                "message": "Original stories retrieved successfully",
                "data": {
                    "stories": stories_data,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": math.ceil(total / page_size) if page_size > 0 else 0,
                },
            }
        )
    except Exception as e:
        logging.error(f"Error getting original stories by level: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")


@original_story_api.route("/<story_id>", methods=["GET"])
@api_key_required
def get_story_by_id(story_id):
    """
    根据ID获取单个旧有故事
    """
    try:
        story = original_story_service.get_story_by_id(story_id)
        if story:
            return jsonify(
                {
                    "code": 200,
                    "message": "Original story retrieved successfully",
                    "data": {
                        "id": story.id,
                        "name": story.name,
                        "level": story.level,
                        "content": story.content,
                        "tokenized_content": story.tokenized_content,
                        "unknown_word_ratio": story.unknown_word_ratio,
                        "created_at": (
                            story.created_at.isoformat() if story.created_at else None
                        ),
                        "updated_at": (
                            story.updated_at.isoformat() if story.updated_at else None
                        ),
                    },
                }
            )
        else:
            return handle_error(404, "Original story not found")
    except Exception as e:
        logging.error(f"Error getting original story by id: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")


@original_story_api.route("/process-all", methods=["POST"])
@api_key_required
def process_all_stories():
    """
    触发一个后台任务，对所有未处理的原始故事进行分词和生词率计算。
    支持可选参数 start_level 和 end_level 来指定处理范围。
    """
    try:
        # 可以在请求体中指定AI服务，如果需要的话
        data = request.get_json() or {}
        ai_service_name = data.get("ai_service", "gemini")
        start_level = data.get("start_level")
        end_level = data.get("end_level")

        # 参数类型校验
        if start_level is not None and not isinstance(start_level, int):
            return handle_error(400, "start_level must be an integer.")
        if end_level is not None and not isinstance(end_level, int):
            return handle_error(400, "end_level must be an integer.")

        original_story_service.start_processing_stories(
            ai_service_name=ai_service_name,
            start_level=start_level,
            end_level=end_level,
        )

        return (
            jsonify({"code": 202, "message": "Story processing has been initiated."}),
            202,
        )
    except Exception as e:
        logging.error(f"Error initiating story processing: {e}", exc_info=True)
        return handle_error(500, f"Internal server error: {str(e)}")
