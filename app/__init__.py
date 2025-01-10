# filepath: app/__init__.py
from flask import Flask
from app.api.stories_api import init_story_routes
from app.api.scenes_api import init_scene_routes
from app.api.words_api import init_word_routes


def create_app():
    app = Flask(__name__)

    # 注册 API 路由
    init_story_routes(app)
    init_scene_routes(app)
    init_word_routes(app)

    return app
