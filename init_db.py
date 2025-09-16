import json
import logging
from app.database import engine, SessionLocal, Base
from app.models.word_model import WordModel
from app.models.scene_model import SceneModel
from app.models.story_model import StoryModel  # 导入以确保表被创建
from app.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """
    初始化数据库：创建表并从 JSON 文件填充初始数据。
    """
    logger.info("Creating database tables...")
    # Base.metadata.create_all 会找到所有继承自 Base 的子类并创建对应的表
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

    db = SessionLocal()
    try:
        # 填充 words 表
        if db.query(WordModel).count() == 0:
            logger.info(f"Populating 'words' table from {Config.WORDS_FILE_PATH}...")
            with open(Config.WORDS_FILE_PATH, "r", encoding="utf-8") as f:
                words_data = json.load(f)
                for word_data in words_data:
                    word = WordModel.from_dict(word_data)
                    db.add(word)
                db.commit()
            logger.info(f"'words' table populated with {len(words_data)} records.")
        else:
            logger.info("'words' table already populated. Skipping.")

        # 填充 scenes 表
        if db.query(SceneModel).count() == 0:
            logger.info(f"Populating 'scenes' table from {Config.SCENES_FILE_PATH}...")
            try:
                with open(Config.SCENES_FILE_PATH, "r", encoding="utf-8") as f:
                    scenes_data = json.load(f)
                    for scene_data in scenes_data:
                        scene = SceneModel.from_dict(scene_data)
                        db.add(scene)
                    db.commit()
                logger.info(
                    f"'scenes' table populated with {len(scenes_data)} records."
                )
            except FileNotFoundError:
                logger.warning(
                    f"{Config.SCENES_FILE_PATH} not found, skipping scene population."
                )
        else:
            logger.info("'scenes' table already populated. Skipping.")

    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Starting database initialization...")
    init_db()
    logger.info("Database initialization finished.")
