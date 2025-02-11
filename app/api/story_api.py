# app/api/story_api.py
from flask import Blueprint, request, jsonify
from app.services.story_service import StoryService
from app.utils.error_handling import handle_error
from app.utils.api_key_auth import api_key_required
from app.config import Config
from app.services.word_service import WordService
from app.services.scene_service import SceneService
from app.utils.literacy_calculator import LiteracyCalculator
from app.services.ai_service_factory import AIServiceFactory  # 导入 AIServiceFactory
import logging


story_api = Blueprint("story_api", __name__, url_prefix="/api/v1/stories")


# 初始化 StoryService
# 为了避免循环依赖，在这里初始化依赖
word_service = WordService()
scene_service = SceneService()
literacy_calculator = LiteracyCalculator(word_service)


@story_api.route("/generate", methods=["POST"])
@api_key_required
def generate_story():
    """
    生成故事
    """
    try:
        data = request.get_json()
        if not data:
            return handle_error(400, "Missing request body")

        vocabulary_level = data.get("vocabulary_level")
        scene_id = data.get("scene_id")
        story_word_count = data.get("story_word_count")
        new_word_rate = data.get("new_word_rate")
        key_word_ids = data.get("key_word_ids", [])
        new_word_rate_tolerance = data.get("new_word_rate_tolerance")
        story_word_count_tolerance = data.get("story_word_count_tolerance")
        request_limit = data.get("request_limit")
        ai_service_name = data.get("ai_service", "deepseek")  # 默认使用 deepseek

        # 验证参数是否存在
        if not vocabulary_level:
            return handle_error(400, "Missing required field: 'vocabulary_level'")
        if not scene_id:
            return handle_error(400, "Missing required field: 'scene_id'")
        if not story_word_count:
            return handle_error(400, "Missing required field: 'story_word_count'")
        if not new_word_rate:
            return handle_error(400, "Missing required field: 'new_word_rate'")

        # 验证参数类型
        if not isinstance(vocabulary_level, int):
            return handle_error(
                400, "Invalid field type: 'vocabulary_level' must be an integer"
            )
        if not isinstance(scene_id, str):
            return handle_error(400, "Invalid field type: 'scene_id' must be a string")
        if not isinstance(story_word_count, int):
            return handle_error(
                400, "Invalid field type: 'story_word_count' must be an integer"
            )
        if not isinstance(new_word_rate, float):
            return handle_error(
                400, "Invalid field type: 'new_word_rate' must be a float"
            )
        if key_word_ids and not isinstance(key_word_ids, list):
            return handle_error(
                400, "Invalid field type: 'key_word_ids' must be a list"
            )

        # 验证参数取值范围
        if not 1 <= vocabulary_level <= 300:
            return handle_error(
                400, "Validation failed: 'vocabulary_level' must be between 1 and 300"
            )
        if not 0 <= new_word_rate <= 1:
            return handle_error(
                400, "Validation failed: 'new_word_rate' must be between 0 and 1"
            )

        if new_word_rate_tolerance is not None and not isinstance(
            new_word_rate_tolerance, float
        ):
            return handle_error(
                400,
                "Invalid field type: 'new_word_rate_tolerance' must be a float",
            )

        if story_word_count_tolerance is not None and not isinstance(
            story_word_count_tolerance, int
        ):
            return handle_error(
                400,
                "Invalid field type: 'story_word_count_tolerance' must be a integer",
            )

        if request_limit is not None and not isinstance(request_limit, int):
            return handle_error(
                400, "Invalid field type: 'request_limit' must be a integer"
            )

        try:
            #  创建 AI 服务对象
            ai_service = AIServiceFactory.create_ai_service(
                ai_service_name=ai_service_name,
            )
        except ValueError as e:
            return handle_error(400, str(e))

        story_service = StoryService(
            word_service=word_service,
            scene_service=scene_service,
            literacy_calculator=literacy_calculator,
            ai_service=ai_service,  # 传递 AI 服务对象
        )

        story = story_service.generate_story(
            vocabulary_level=vocabulary_level,
            scene_id=scene_id,
            story_word_count=story_word_count,
            new_word_rate=new_word_rate,
            key_word_ids=key_word_ids,
            new_word_rate_tolerance=new_word_rate_tolerance,
            story_word_count_tolerance=story_word_count_tolerance,
            request_limit=request_limit,
        )

        return jsonify(
            {
                "code": 200,
                "message": "Story generated successfully",
                "data": story.to_dict(),
            }
        )
    except Exception as e:
        logging.error(f"Error generating story: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")
