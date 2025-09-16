# app/services/word_service.py
import logging
import uuid
from typing import Dict, List, Optional

from app.database import SessionLocal
from app.models.word_model import WordModel


class WordService:
    """
    词语服务，提供与数据库交互的词语相关业务逻辑。
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("WordService initialized to work with the database.")

    def get_word_by_id(self, word_id: str) -> Optional[WordModel]:
        """
        根据ID从数据库获取词语信息。
        """
        db = SessionLocal()
        try:
            return db.query(WordModel).filter(WordModel.id == word_id).first()
        finally:
            db.close()

    def get_words(
        self,
        chaotong_level: Optional[int] = None,
        part_of_speech: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> List[WordModel]:
        """
        根据条件从数据库获取词语列表。
        """
        db = SessionLocal()
        try:
            query = db.query(WordModel)

            if chaotong_level is not None:
                query = query.filter(WordModel.chaotong_level == chaotong_level)

            if part_of_speech:
                query = query.filter(WordModel.part_of_speech == part_of_speech)

            if sort_by:
                sort_column = getattr(WordModel, sort_by, None)
                if sort_column:
                    if sort_order == "desc":
                        query = query.order_by(sort_column.desc())
                    else:
                        query = query.order_by(sort_column.asc())

            return query.offset((page - 1) * page_size).limit(page_size).all()
        finally:
            db.close()

    def get_total_words(
        self, chaotong_level: Optional[int] = None, part_of_speech: Optional[str] = None
    ) -> int:
        """
        根据条件从数据库获取词语总数。
        """
        db = SessionLocal()
        try:
            query = db.query(WordModel)

            if chaotong_level is not None:
                query = query.filter(WordModel.chaotong_level == chaotong_level)
            if part_of_speech:
                query = query.filter(WordModel.part_of_speech == part_of_speech)

            return query.count()
        finally:
            db.close()

    def get_words_below_level(self, level: int) -> List[WordModel]:
        """
        从数据库获取指定级别以下的所有词汇。
        """
        db = SessionLocal()
        try:
            return db.query(WordModel).filter(WordModel.chaotong_level < level).all()
        finally:
            db.close()

    def get_key_words_by_ids(self, key_word_ids: List[str]) -> List[Dict]:
        """
        根据 key_word_ids 从数据库获取重点词汇的详细信息。
        """
        db = SessionLocal()
        try:
            words = db.query(WordModel).filter(WordModel.id.in_(key_word_ids)).all()
            key_words = []
            for word_model in words:
                key_words.append(
                    {
                        "word": word_model.word,
                        "pinyin": None,
                        "definition": None,
                        "example": None,
                        "part_of_speech": word_model.part_of_speech,
                    }
                )
            return key_words
        finally:
            db.close()

    def get_word_by_text_and_pos(
        self, text: str, part_of_speech: str
    ) -> Optional[WordModel]:
        """
        根据文本和词性从数据库获取词语信息。
        """
        db = SessionLocal()
        try:
            return (
                db.query(WordModel)
                .filter(
                    WordModel.word == text, WordModel.part_of_speech == part_of_speech
                )
                .first()
            )
        finally:
            db.close()

    def create_word(
        self,
        word: str,
        chaotong_level: int,
        part_of_speech: str,
        hsk_level: Optional[float],
    ) -> WordModel:
        """
        在数据库中创建新词汇。
        """
        db = SessionLocal()
        try:
            # 检查具有相同词语和词性的词是否已存在
            existing_word = (
                db.query(WordModel)
                .filter(
                    WordModel.word == word,
                    WordModel.part_of_speech == part_of_speech,
                )
                .first()
            )
            if existing_word:
                self.logger.warning(
                    f"Word '{word}' with part of speech '{part_of_speech}' already exists with ID {existing_word.id}. Returning existing word."
                )
                return existing_word

            new_word = WordModel(
                id=str(uuid.uuid4()),
                word=word,
                chaotong_level=chaotong_level,
                part_of_speech=part_of_speech,
                hsk_level=hsk_level,
            )
            db.add(new_word)
            db.commit()
            db.refresh(new_word)
            self.logger.info(f"Created new word in DB: {word} ({part_of_speech})")
            return new_word
        finally:
            db.close()

    def delete_word(self, word_id: str) -> bool:
        """
        从数据库删除词汇。
        """
        db = SessionLocal()
        try:
            word = db.query(WordModel).filter(WordModel.id == word_id).first()
            if word:
                db.delete(word)
                db.commit()
                self.logger.info(f"Deleted word from DB: ID={word_id}")
                return True
            return False
        finally:
            db.close()
