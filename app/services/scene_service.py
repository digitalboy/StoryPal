# app/services/scene_service.py
import json
import logging
from app.config import Config
from app.models.scene_model import SceneModel


class SceneService:
    def __init__(self):
        self.scenes = self._load_scenes()

    def _load_scenes(self):
        logging.info("Loading scenes data from json file")
        try:
            with open(Config.SCENES_FILE_PATH, "r", encoding="utf-8") as f:
                scenes_data = json.load(f)
            logging.info(f"Loaded {len(scenes_data)} scenes from file")
            return {
                scene_data["scene_id"]: SceneModel.from_dict(scene_data)
                for scene_data in scenes_data
            }
        except FileNotFoundError:
            logging.error("scenes.json not found")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding json file: {e}")
            return {}

    def get_scene(self, scene_id):
        logging.info(f"Getting scene by id: {scene_id}")
        return self.scenes.get(scene_id)

    def list_scenes(self):
        logging.info("Listing all scenes")
        return list(self.scenes.values())

    def add_scene(self, scene_data):
        logging.info(f"Adding scene {scene_data}")
        scene = SceneModel.from_dict(scene_data)
        self.scenes[scene.scene_id] = scene
        return scene

    def update_scene(self, scene_id, scene_data):
        logging.info(f"Updating scene {scene_id} with {scene_data}")
        scene = self.get_scene(scene_id)
        if not scene:
            logging.error(f"Scene not found {scene_id}")
            return None
        updated_scene = SceneModel(scene_id=scene_id, **scene_data)
        self.scenes[scene_id] = updated_scene
        return updated_scene

    def delete_scene(self, scene_id):
        logging.info(f"Deleting scene {scene_id}")
        scene = self.get_scene(scene_id)
        if not scene:
            logging.error(f"Scene not found {scene_id}")
            return None
        del self.scenes[scene_id]
        return scene
