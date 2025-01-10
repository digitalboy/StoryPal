# app/models/scene_model.py
from app.models.base_model import BaseModel


class SceneModel(BaseModel):
    def __init__(self, scene_id, name, description, **kwargs):
        super().__init__(id=scene_id, **kwargs)
        self.scene_id = self.id
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            "scene_id": self.scene_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            scene_id=data.get("scene_id"),
            name=data.get("name"),
            description=data.get("description"),
            created_at=data.get("created_at"),
        )
