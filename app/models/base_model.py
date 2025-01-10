# app/models/base_model.py
 import uuid
 from datetime import datetime, timezone

 class BaseModel:
    def __init__(self, **kwargs):
         # 如果有 id， 直接赋值， 否则生成一个新的 uuid
        self.id = kwargs.get('id') if kwargs.get('id') else str(uuid.uuid4())
        self.created_at = kwargs.get('created_at') if kwargs.get('created_at') else datetime.now(timezone.utc).isoformat()


    def to_dict(self):
         return self.__dict__

    @classmethod
    def from_dict(cls, data):
      return cls(**data)

    def __repr__(self):
     return f"<{self.__class__.__name__} id={self.id}>"