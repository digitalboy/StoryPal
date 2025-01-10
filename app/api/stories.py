# filepath: app/api/stories.py
from flask import request, jsonify
from app.services.story_service import StoryService
from app.utils.error_handling import handle_error

# 初始化故事服务
story_service = StoryService()


def init_story_routes(app):
    @app.route("/v1/stories/<story_id>", methods=["GET"])
    def get_story(story_id):
        """
        获取故事 API
        - 路径参数：
          - story_id: 故事ID
        """
        try:
            # 调用故事查询服务
            story = story_service.get_story(story_id)
            if story:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Story retrieved successfully",
                        "data": story.to_dict(),
                    }
                ), 200
            else:
                return handle_error(404, "Story not found", 4043)
        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5001)

    @app.route("/v1/stories/<story_id>", methods=["PUT"])
    def update_story(story_id):
        """
        更新故事 API
        - 路径参数：
          - story_id: 故事ID
        - 请求体需包含以下字段（可选）：
          - title: 故事标题
          - content: 故事内容
          - vocabulary_level: 超童级别
          - scene_id: 场景ID
          - word_count: 故事字数
          - new_char_rate: 生字率
          - new_words: 生词列表
          - key_words: 重点词汇列表
        """
        try:
            # 解析请求体
            data = request.get_json()
            if not data:
                return handle_error(400, "请求体不能为空", 4001)

            # 调用故事更新服务
            success = story_service.update_story(story_id, data)
            if success:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Story updated successfully",
                        "data": None,
                    }
                ), 200
            else:
                return handle_error(404, "Story not found", 4043)
        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5001)

    @app.route("/v1/stories/<story_id>", methods=["DELETE"])
    def delete_story(story_id):
        """
        删除故事 API
        - 路径参数：
          - story_id: 故事ID
        """
        try:
            # 调用故事删除服务
            success = story_service.delete_story(story_id)
            if success:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Story deleted successfully",
                        "data": None,
                    }
                ), 200
            else:
                return handle_error(404, "Story not found", 4043)
        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5001)

    @app.route("/v1/stories/generate", methods=["POST"])
    def generate_story():
        """
        生成故事 API
        - 请求体需包含以下字段：
          - vocabulary_level: 目标词汇级别（1-100）
          - scene_id: 场景ID
          - word_count: 故事字数
          - new_char_rate: 目标生字率（0-1）
          - key_word_ids: 重点词汇ID列表（可选）
        """
        try:
            # 解析请求体
            data = request.get_json()
            if not data:
                return handle_error(400, "请求体不能为空", 4001)

            # 获取请求参数
            vocabulary_level = data.get("vocabulary_level")
            scene_id = data.get("scene_id")
            word_count = data.get("word_count")
            new_char_rate = data.get("new_char_rate")
            key_word_ids = data.get("key_word_ids", [])

            # 验证必填字段
            required_fields = [
                "vocabulary_level",
                "scene_id",
                "word_count",
                "new_char_rate",
            ]
            for field in required_fields:
                if field not in data:
                    return handle_error(400, f"缺少必填字段: {field}", 4001)

            if not (1 <= vocabulary_level <= 100):
                return handle_error(
                    422, f"Invalid vocabulary_level: {vocabulary_level}", 4222
                )
            if not (0 <= new_char_rate <= 1):
                return handle_error(
                    422, f"Invalid new_char_rate: {new_char_rate}", 4221
                )

            # 调用故事生成服务
            story = story_service.generate_story(
                vocabulary_level=vocabulary_level,
                scene_id=scene_id,
                word_count=word_count,
                new_char_rate=new_char_rate,
                key_word_ids=key_word_ids,
            )

            # 返回成功响应
            return jsonify(
                {
                    "code": 200,
                    "message": "Story generated successfully",
                    "data": story.to_dict(),
                }
            ), 200

        except ValueError as e:
            # 处理参数错误
            return handle_error(400, str(e), 4003)
        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5002)
