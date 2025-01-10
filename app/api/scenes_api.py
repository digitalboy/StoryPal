# filepath: app/api/scenes.py
from flask import request, jsonify
from app.services.scene_service import SceneService
from app.utils.error_handling import handle_error

# 初始化场景服务
scene_service = SceneService()


def init_scene_routes(app):
    @app.route("/v1/scenes", methods=["POST"])
    def create_scene():
        """
        创建场景 API
        - 请求体需包含以下字段：
          - name: 场景名称
          - description: 场景描述
        """
        try:
            # 解析请求体
            data = request.get_json()
            if not data:
                return handle_error(400, "请求体不能为空", 4001)

            # 获取请求参数
            name = data.get("name")
            description = data.get("description")

            # 验证必填字段
            if not name:
                return handle_error(400, "缺少必填字段: name", 4001)
            if not description:
                return handle_error(400, "缺少必填字段: description", 4001)

            # 调用场景创建服务
            scene = scene_service.create_scene(name, description)

            # 返回成功响应
            return jsonify(
                {
                    "code": 200,
                    "message": "Scene created successfully",
                    "data": {"scene_id": scene.id},
                }
            ), 200

        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5001)

    @app.route("/v1/scenes/<scene_id>", methods=["GET"])
    def get_scene(scene_id):
        """
        获取场景 API
        - 路径参数：
          - scene_id: 场景ID
        """
        try:
            # 调用场景查询服务
            scene = scene_service.get_scene(scene_id)
            if scene:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Scene retrieved successfully",
                        "data": scene.to_dict(),
                    }
                ), 200
            else:
                return handle_error(404, "Scene not found", 4041)
        except Exception as e:
            # 处理其他错误
            print(e)  # 添加打印异常信息
            return handle_error(500, str(e), 5001)

    @app.route("/v1/scenes/<scene_id>", methods=["PUT"])
    def update_scene(scene_id):
        """
        更新场景 API
        - 路径参数：
          - scene_id: 场景ID
        - 请求体需包含以下字段：
          - name: 场景名称
          - description: 场景描述
        """
        try:
            # 解析请求体
            data = request.get_json()
            if not data:
                return handle_error(400, "请求体不能为空", 4001)

            # 获取请求参数
            name = data.get("name")
            description = data.get("description")

            # 验证必填字段
            if not name:
                return handle_error(400, "缺少必填字段: name", 4001)
            if not description:
                return handle_error(400, "缺少必填字段: description", 4001)
            # 调用场景更新服务
            print(f"update_scene data: {data}")
            success = scene_service.update_scene(scene_id, name, description)
            print(f"update_scene success: {success}")
            if success:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Scene updated successfully",
                        "data": None,
                    }
                ), 200
            else:
                return handle_error(404, "Scene not found", 4041)
        except Exception as e:
            # 处理其他错误
            print(e)
            return handle_error(500, str(e), 5001)

    @app.route("/v1/scenes/<scene_id>", methods=["DELETE"])
    def delete_scene(scene_id):
        """
        删除场景 API
        - 路径参数：
          - scene_id: 场景ID
        """
        try:
            # 调用场景删除服务
            success = scene_service.delete_scene(scene_id)
            if success:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Scene deleted successfully",
                        "data": None,
                    }
                ), 200
            else:
                return handle_error(404, "Scene not found", 4041)
        except Exception as e:
            # 处理其他错误
            return handle_error(500, str(e), 5001)
