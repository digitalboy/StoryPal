# app/api/scene_api.py
from flask import Blueprint, request, jsonify
from app.services.scene_service import SceneService
from app.utils.error_handling import handle_error
from app.utils.api_key_auth import api_key_required
import logging

scene_api = Blueprint("scene_api", __name__, url_prefix="/v1/scenes")
scene_service = SceneService()


@scene_api.route("", methods=["POST"])
@api_key_required
def create_scene():
    """
    创建场景
    """
    data = request.get_json()
    if not data:
        return handle_error(4001, "Missing request body")

    name = data.get("name")
    description = data.get("description")

    if not name:
        return handle_error(4001, "Missing required field: 'name'")
    if not description:
        return handle_error(4001, "Missing required field: 'description'")
    if not isinstance(name, str):
        return handle_error(4002, "Invalid field type: 'name' must be a string")
    if not isinstance(description, str):
        return handle_error(4002, "Invalid field type: 'description' must be a string")
    try:
        scene = scene_service.add_scene(data)
        return jsonify(
            {
                "code": 200,
                "message": "Scene created successfully",
                "data": {"scene_id": scene.scene_id},
            }
        )
    except Exception as e:
        logging.error(f"Error while creating scene: {e}")
        return handle_error(5001, f"Internal server error: {str(e)}")


@scene_api.route("/<string:scene_id>", methods=["GET"])
@api_key_required
def get_scene(scene_id):
    """
    获取场景
    """
    try:
        scene = scene_service.get_scene(scene_id)
        if not scene:
            return handle_error(4041, "Scene not found")
        return jsonify(
            {
                "code": 200,
                "message": "Scene retrieved successfully",
                "data": scene.to_dict(),
            }
        )
    except Exception as e:
        logging.error(f"Error while getting scene: {e}")
        return handle_error(5001, f"Internal server error: {str(e)}")


@scene_api.route("/<string:scene_id>", methods=["PUT"])
@api_key_required
def update_scene(scene_id):
    """
    更新场景
    """
    data = request.get_json()
    if not data:
        return handle_error(4001, "Missing request body")
    name = data.get("name")
    description = data.get("description")

    if not name:
        return handle_error(4001, "Missing required field: 'name'")
    if not description:
        return handle_error(4001, "Missing required field: 'description'")
    if not isinstance(name, str):
        return handle_error(4002, "Invalid field type: 'name' must be a string")
    if not isinstance(description, str):
        return handle_error(4002, "Invalid field type: 'description' must be a string")
    try:
        scene = scene_service.update_scene(scene_id, data)
        if not scene:
            return handle_error(4041, "Scene not found")

        return jsonify(
            {"code": 200, "message": "Scene updated successfully", "data": None}
        )
    except Exception as e:
        logging.error(f"Error while updating scene: {e}")
        return handle_error(5001, f"Internal server error: {str(e)}")


@scene_api.route("/<string:scene_id>", methods=["DELETE"])
@api_key_required
def delete_scene(scene_id):
    """
    删除场景
    """
    try:
        scene = scene_service.delete_scene(scene_id)
        if not scene:
            return handle_error(4041, "Scene not found")
        return jsonify(
            {"code": 200, "message": "Scene deleted successfully", "data": None}
        )
    except Exception as e:
        logging.error(f"Error while deleting scene: {e}")
        return handle_error(5001, f"Internal server error: {str(e)}")
