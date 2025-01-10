# filepath: app/api/words.py
from flask import request, jsonify
from app.services.word_service import WordService
from app.utils.error_handling import handle_error

# 初始化字词服务
word_service = WordService()


def init_word_routes(app):
    @app.route("/v1/words", methods=["POST"])
    def create_word():
        """
        创建字词 API
        - 请求体需包含以下字段：
          - word: 词
          - pinyin: 拼音
          - definition: 释义
          - part_of_speech: 词性
          - chaotong_level: 超童级别
          - characters: 词中包含的字（可选）
          - example: 例句（可选）
        """
        try:
            # 解析请求体
            data = request.get_json()
            if not data:
                return handle_error(400, "请求体不能为空", 4001)

            # 验证必填字段
            required_fields = [
                "word",
                "pinyin",
                "definition",
                "part_of_speech",
                "chaotong_level",
            ]
            for field in required_fields:
                if field not in data:
                    return handle_error(400, f"缺少必填字段: {field}", 4001)

            # 调用字词创建服务
            word = word_service.create_word(data)

            # 返回成功响应
            return jsonify(
                {
                    "code": 200,
                    "message": "Word created successfully",
                    "data": {"word_id": word.id},
                }
            ), 200

        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5001)

    @app.route("/v1/words/<word_id>", methods=["GET"])
    def get_word(word_id):
        """
        获取字词 API
        - 路径参数：
          - word_id: 字词ID
        """
        try:
            # 调用字词查询服务
            word = word_service.get_word(word_id)
            if word:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Word retrieved successfully",
                        "data": word,
                    }
                ), 200
            else:
                return handle_error(404, "Word not found", 4042)
        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5001)

    @app.route("/v1/words/<word_id>", methods=["PUT"])
    def update_word(word_id):
        """
        更新字词 API
        - 路径参数：
          - word_id: 字词ID
        - 请求体需包含以下字段（可选）：
          - word: 词
          - pinyin: 拼音
          - definition: 释义
          - part_of_speech: 词性
          - chaotong_level: 超童级别
          - characters: 词中包含的字
          - example: 例句
        """
        try:
            # 解析请求体
            data = request.get_json()
            if not data:
                return handle_error(400, "请求体不能为空", 4001)

            # 调用字词更新服务
            success = word_service.update_word(word_id, data)
            if success:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Word updated successfully",
                        "data": None,
                    }
                ), 200
            else:
                return handle_error(404, "Word not found", 4042)
        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5001)

    @app.route("/v1/words/<word_id>", methods=["DELETE"])
    def delete_word(word_id):
        """
        删除字词 API
        - 路径参数：
          - word_id: 字词ID
        """
        try:
            # 调用字词删除服务
            success = word_service.delete_word(word_id)
            if success:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Word deleted successfully",
                        "data": None,
                    }
                ), 200
            else:
                return handle_error(404, "Word not found", 4042)
        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5001)

    @app.route("/v1/words", methods=["GET"])
    def get_words():
        """
        查询字词 API
        - 查询参数：
          - level: 超童级别（1-100）
          - part_of_speech: 词性（如“名词”）
        """
        try:
            # 解析查询参数
            level = request.args.get("level", type=int)
            part_of_speech = request.args.get("part_of_speech")
            page = request.args.get("page", default=1, type=int)
            page_size = request.args.get("page_size", default=10, type=int)

            # 调用字词查询服务
            if level:
                words = word_service.get_words_by_level(level)
            elif part_of_speech:
                words = word_service.get_words_by_part_of_speech(part_of_speech)
            else:
                words = word_service.get_all_words()

            # 分页处理
            start = (page - 1) * page_size
            end = start + page_size
            paged_words = words[start:end]
            total = len(words)

            # 返回成功响应
            return jsonify(
                {
                    "code": 200,
                    "message": "Words retrieved successfully",
                    "data": {
                        "words": [word.to_dict() for word in paged_words],
                        "total": total,
                    },
                }
            ), 200

        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5001)
