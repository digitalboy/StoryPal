# app/__init__.py
from flask import Flask, jsonify, send_from_directory
import logging

# 导入所有模型以防止 SQLAlchemy 在服务实例化时出现循环依赖问题
from app.models.word_model import WordModel  # noqa: F401
from app.models.scene_model import SceneModel  # noqa: F401
from app.models.story_model import StoryModel  # noqa: F401
from app.models.original_story_model import OriginalStoryModel  # noqa: F401
from app.utils.error_handling import handle_error
from app.api.scene_api import scene_api
from app.api.word_api import word_api
from app.api.story_api import story_api
from app.api.original_story_api import original_story_api


def create_app():
    """
    创建并配置 Flask 应用
    """
    app = Flask(__name__, static_folder="static")
    app.debug = True
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s",
    )
    # 注册 Blueprint
    app.register_blueprint(word_api)
    app.register_blueprint(scene_api)
    app.register_blueprint(story_api)
    app.register_blueprint(original_story_api)

    # 添加根路由
    @app.route("/", methods=["GET"])
    def hello():
        return jsonify({"message": "Hello, StoryPal!"})

    # 添加 favicon.ico 路由
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(app.static_folder, "favicon.ico")

    #  全局 404 错误处理，
    @app.errorhandler(404)
    def not_found_error(error):
        logging.error(f"Not found error: {error}")
        return handle_error(404, "Resource not found")

    @app.errorhandler(500)
    def internal_server_error(error):
        logging.error(f"Internal server error: {error}")
        return handle_error(5001, "Internal server error")

    return app
