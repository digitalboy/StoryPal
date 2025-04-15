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
from app.models.story_model import StoryModel  # 确保导入 StoryModel
import logging

story_api = Blueprint("story_api", __name__, url_prefix="/api/v1/stories")


# 初始化 StoryService
# 为了避免循环依赖，在这里初始化依赖
word_service = WordService()
scene_service = SceneService()
# literacy_calculator = LiteracyCalculator(word_service)  #  移动到 key_word_ids 验证之后


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
        ai_service_name = data.get("ai_service", "gemini")  # 默认使用 gemini
        multiplier = data.get("multiplier")  # 获取倍率参数， 允许为空

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

        if multiplier is not None:  # 如果 multiplier 不为空， 则验证其类型
            if not isinstance(multiplier, (int, float)):
                return handle_error(
                    400, "Invalid field type: 'multiplier' must be a number"
                )
        else:
            multiplier = 1.2  # 如果 multiplier 为空， 则使用默认值 1.2

        try:
            #  创建 AI 服务对象
            ai_service = AIServiceFactory.create_ai_service(
                ai_service_name=ai_service_name,
            )
        except ValueError as e:
            return handle_error(400, str(e))

        # 获取目标级别词汇
        target_words = word_service.get_words(chaotong_level=vocabulary_level)
        target_word_ids = {word.id for word in target_words}

        print(f"vocabulary_level: {vocabulary_level}")
        print(f"target_word_ids: {target_word_ids}")
        print(f"key_word_ids: {key_word_ids}")

        # 验证 key_word_ids 是否属于目标级别
        for word_id in key_word_ids:
            if word_id not in target_word_ids:
                error_message = f"关键词 ID {word_id} 不属于词汇级别 {vocabulary_level}"
                print(error_message)
                return handle_error(
                    400,
                    error_message,
                )

        # 移动 literacy_calculator 的初始化到这里
        literacy_calculator = LiteracyCalculator(word_service)

        story_service = StoryService(
            word_service=word_service,
            scene_service=scene_service,
            literacy_calculator=literacy_calculator,  # 使用更新后的 literacy_calculator
            ai_service=ai_service,  # 传递 AI 服务对象
        )

        # 获取已学词汇数量
        known_words = word_service.get_words_below_level(vocabulary_level)
        known_word_count = len(known_words)

        # 定义合理的字数范围
        max_word_count = int(
            known_word_count * multiplier
        )  # 用户要求的字数不能超过已学词汇数量的 multiplier 倍, 取整

        # 进行校验
        if story_word_count > max_word_count:
            return handle_error(400, "字数要求过多")

        story = story_service.generate_story(
            vocabulary_level=vocabulary_level,
            scene_id=scene_id,
            story_word_count=story_word_count,
            new_word_rate=new_word_rate,
            key_word_ids=key_word_ids,
            new_word_rate_tolerance=new_word_rate_tolerance,
            story_word_count_tolerance=story_word_count_tolerance,
        )  # 移除 request_limit

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


@story_api.route("/rewrite", methods=["POST"])
@api_key_required
def rewrite_story_endpoint():
    """
    改写现有故事到目标级别
    """
    try:
        data = request.get_json()
        if not data:
            return handle_error(400, "Missing request body")

        original_story_id = data.get("original_story_id")
        target_level = data.get("target_level")
        story_type = data.get("story_type", 2)  # 默认为 2 (中文绘本)
        ai_service_name = data.get("ai_service", "gemini")  # 默认使用 gemini

        # --- 参数验证 ---
        if not original_story_id:
            return handle_error(400, "Missing required field: 'original_story_id'")
        if not target_level:
            return handle_error(400, "Missing required field: 'target_level'")

        if not isinstance(original_story_id, str):
            return handle_error(
                400, "Invalid field type: 'original_story_id' must be a string"
            )
        if not isinstance(target_level, int):
            return handle_error(
                400, "Invalid field type: 'target_level' must be an integer"
            )
        if not isinstance(story_type, int) or story_type not in [1, 2]:
            return handle_error(400, "Invalid field value: 'story_type' must be 1 or 2")
        if not 1 <= target_level <= 300:  # 假设级别范围
            return handle_error(
                400, "Validation failed: 'target_level' must be between 1 and 300"
            )
        # --- 参数验证结束 ---

        try:
            # 创建 AI 服务对象
            ai_service = AIServiceFactory.create_ai_service(
                ai_service_name=ai_service_name,
            )
        except ValueError as e:
            return handle_error(400, str(e))

        # 初始化依赖
        # word_service 和 scene_service 已在蓝图级别初始化
        literacy_calculator = LiteracyCalculator(word_service)

        story_service = StoryService(
            word_service=word_service,
            scene_service=scene_service,
            literacy_calculator=literacy_calculator,
            ai_service=ai_service,
        )

        # 调用服务层进行改写
        rewritten_story: StoryModel = story_service.rewrite_story(
            original_story_id=original_story_id,
            target_level=target_level,
            story_type=story_type,
        )

        if rewritten_story:
            return jsonify(
                {
                    "code": 200,
                    "message": "Story rewritten successfully",
                    "data": rewritten_story.to_dict(),
                }
            )
        else:
            # rewrite_story 内部已记录详细错误，这里返回通用错误
            return handle_error(500, "Failed to rewrite story")

    except Exception as e:
        logging.exception(f"Error rewriting story: {e}")  # 使用 exception 记录堆栈信息
        return handle_error(500, f"Internal server error: {str(e)}")
