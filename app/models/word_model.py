# app/models/word_model.py
from typing import List, Dict, Optional
from app.models.base_model import BaseModel


class WordModel(BaseModel):
    """
    词语数据模型。
    """

    def __init__(
        self,
        word_id: str = None,
        word: str = None,
        chaotong_level: int = None,
        hsk_level: Optional[float] = None,
        part_of_speech: str = None,
        created_at: str = None,
    ):
        """
        初始化方法。
        Args:
            word_id (str, optional): 词语的唯一ID，如果为None，则自动生成UUID.
            word (str): 词语.
            chaotong_level (int): 超童级别，取值范围 1-100.
            hsk_level (float): HSK级别.
            part_of_speech (str): 词性
            created_at (str, optional): 模型的创建时间，如果为None，则设置为当前时间.
        """
        super().__init__(id=word_id, created_at=created_at)
        self.word = word
        self.chaotong_level = chaotong_level
        self.hsk_level = hsk_level
        self.part_of_speech = part_of_speech

    def to_dict(self) -> Dict:
        """
        将模型对象转换为字典。
        Returns:
            dict: 模型对象的字典表示。
        """
        return {
            "word_id": self.id,
            "word": self.word,
            "chaotong_level": self.chaotong_level,
            "hsk_level": self.hsk_level,
            "part_of_speech": self.part_of_speech,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """
        从字典创建模型对象。
        Args:
            data (dict): 模型对象的字典表示。
        Returns:
            WordModel: 词语模型对象。
        """
        chaotong_level = data.get("chaotong_level")
        if chaotong_level is not None:
            try:
                chaotong_level = int(chaotong_level)
            except (ValueError, TypeError):
                chaotong_level = None  # 或者设置默认值，或者抛出异常
        return cls(
            word_id=data.get("word_id"),
            word=data.get("word"),
            chaotong_level=chaotong_level,
            hsk_level=data.get("hsk_level"),
            part_of_speech=data.get("part_of_speech"),
            created_at=data.get("created_at"),
        )
