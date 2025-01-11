# app/api/story_api.py
from flask import Blueprint, request, jsonify
from app.services.story_service import StoryService
from app.utils.error_handling import handle_error
from app.utils.api_key_auth import api_key_required
import logging

story_api = Blueprint("story_api", __name__, url_prefix="/v1/stories")
story_service = StoryService()


@story_api.route("/generate", methods=["POST"])
@api_key_required
def generate_story():
    """
    生成故事
    """
    data = request.get_json()
    if not data:
        return handle_error(4001, "Missing request body")

    vocabulary_level = data.get("vocabulary_level")
    scene_id = data.get("scene_id")
    story_word_count = data.get("story_word_count")
    new_char_rate = data.get("new_char_rate")
    key_word_ids = data.get("key_word_ids", [])

    if not vocabulary_level:
        return handle_error(4001, "Missing required field: 'vocabulary_level'")
    if not scene_id:
        return handle_error(4001, "Missing required field: 'scene_id'")
    if not story_word_count:
        return handle_error(4001, "Missing required field: 'story_word_count'")
    if not new_char_rate:
        return handle_error(4001, "Missing required field: 'new_char_rate'")

    if not isinstance(vocabulary_level, int):
        return handle_error(
            4002, "Invalid field type: 'vocabulary_level' must be an integer"
        )
    if not isinstance(scene_id, str):
        return handle_error(4002, "Invalid field type: 'scene_id' must be a string")
    if not isinstance(story_word_count, int):
        return handle_error(
            4002, "Invalid field type: 'story_word_count' must be an integer"
        )
    if not isinstance(new_char_rate, float):
        return handle_error(4002, "Invalid field type: 'new_char_rate' must be a float")
    if not 1 <= vocabulary_level <= 100:
        return handle_error(
            4222, "Validation failed: 'vocabulary_level' must be between 1 and 100"
        )
    if not 0 <= new_char_rate <= 1:
        return handle_error(
            4221, "Validation failed: 'new_char_rate' must be between 0 and 1"
        )

    try:
        story = story_service.generate_story(
            vocabulary_level=vocabulary_level,
            scene_id=scene_id,
            story_word_count=story_word_count,
            new_char_rate=new_char_rate,
            key_word_ids=key_word_ids,
        )
        if not story:
            return handle_error(5006, "AI 服务调用失败")
        return jsonify(
            {
                "code": 200,
                "message": "Story generated successfully",
                "data": story.to_dict(),
            }
        )
    except Exception as e:
        logging.error(f"Error while generating story: {e}")
        return handle_error(5001, f"Internal server error: {str(e)}")


@story_api.route("/<string:story_id>/adjust", methods=["POST"])
@api_key_required
def adjust_story(story_id):
    """
    升级/降级故事
    """
    data = request.get_json()
    if not data:
        return handle_error(4001, "Missing request body")
    target_level = data.get("target_level")
    if not target_level:
        return handle_error(4001, "Missing required field: 'target_level'")
    if not isinstance(target_level, int):
        return handle_error(
            4002, "Invalid field type: 'target_level' must be an integer"
        )
    if not 1 <= target_level <= 100:
        return handle_error(
            4222, "Validation failed: 'target_level' must be between 1 and 100"
        )
    try:
        story = story_service.adjust_story(story_id, target_level)
        if not story:
            return handle_error(4043, "Story not found")
        return jsonify(
            {
                "code": 200,
                "message": "Story adjusted successfully",
                "data": story.to_dict(),
            }
        )
    except Exception as e:
        logging.error(f"Error while adjusting story: {e}")
        return handle_error(5001, f"Internal server error: {str(e)}")
