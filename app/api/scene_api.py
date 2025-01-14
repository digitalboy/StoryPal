# app/api/scene_api.py
from flask import Blueprint, request, jsonify
from app.services.scene_service import SceneService
from app.utils.error_handling import handle_error
from app.utils.api_key_auth import api_key_required
from app.config import Config
import logging

scene_api = Blueprint("scene_api", __name__, url_prefix="/api/v1/scenes")

# 初始化 SceneService
scene_service = SceneService()


@scene_api.route("", methods=["POST"])
@api_key_required
def create_scene():
    """
    创建场景
    """
    try:
        data = request.get_json()
        if not data:
            return handle_error(400, "Missing request body")

        name = data.get("name")
        description = data.get("description")

        if not name:
            return handle_error(400, "Missing required field: name")
        if not description:
            return handle_error(400, "Missing required field: description")

        scene = scene_service.create_scene(name, description)
        return jsonify(
            {
                "code": 200,
                "message": "Scene created successfully",
                "data": {"scene_id": scene.id},
            }
        )
    except Exception as e:
        logging.error(f"Error creating scene: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")


@scene_api.route("/<scene_id>", methods=["GET"])
@api_key_required
def get_scene(scene_id):
    """
    获取场景
    """
    try:
        scene = scene_service.get_scene_by_id(scene_id)
        if scene:
            return jsonify(
                {
                    "code": 200,
                    "message": "Scene retrieved successfully",
                    "data": {
                        "scene_id": scene.id,
                        "name": scene.name,
                        "description": scene.description,
                    },
                }
            )
        else:
            return handle_error(404, "Scene not found")
    except Exception as e:
        logging.error(f"Error getting scene: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")


@scene_api.route("/<scene_id>", methods=["PUT"])
@api_key_required
def update_scene(scene_id):
    """
    更新场景
    """
    try:
        data = request.get_json()
        if not data:
            return handle_error(400, "Missing request body")

        name = data.get("name")
        description = data.get("description")

        if not name:
            return handle_error(400, "Missing required field: name")
        if not description:
            return handle_error(400, "Missing required field: description")

        scene = scene_service.update_scene(scene_id, name, description)
        if scene:
            return jsonify(
                {
                    "code": 200,
                    "message": "Scene updated successfully",
                    "data": None,
                }
            )
        else:
            return handle_error(404, "Scene not found")

    except Exception as e:
        logging.error(f"Error updating scene: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")


@scene_api.route("/<scene_id>", methods=["DELETE"])
@api_key_required
def delete_scene(scene_id):
    """
    删除场景
    """
    try:
        if scene_service.delete_scene(scene_id):
            return jsonify(
                {
                    "code": 200,
                    "message": "Scene deleted successfully",
                    "data": None,
                }
            )
        else:
            return handle_error(404, "Scene not found")
    except Exception as e:
        logging.error(f"Error deleting scene: {e}")
        return handle_error(500, f"Internal server error: {str(e)}")
