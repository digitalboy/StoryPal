# app/models/word_model.py
from app.models.base_model import BaseModel


class WordModel(BaseModel):
    def __init__(
        self,
        word_id,
        word,
        chaotong_level,
        part_of_speech,
        hsk_level,
        characters,
        **kwargs,
    ):
        super().__init__(id=word_id, **kwargs)
        self.word_id = self.id
        self.word = word
        self.chaotong_level = chaotong_level
        self.part_of_speech = part_of_speech
        self.hsk_level = hsk_level
        self.characters = characters

    def to_dict(self):
        return {
            "word_id": self.word_id,
            "word": self.word,
            "chaotong_level": self.chaotong_level,
            "part_of_speech": self.part_of_speech,
            "hsk_level": self.hsk_level,
            "characters": self.characters,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            word_id=data.get("word_id"),
            word=data.get("word"),
            chaotong_level=data.get("chaotong_level"),
            part_of_speech=data.get("part_of_speech"),
            hsk_level=data.get("hsk_level"),
            characters=data.get("characters"),
            created_at=data.get("created_at"),
        )
