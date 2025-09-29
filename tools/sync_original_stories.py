# sync_original_stories.py
import requests
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from app.database import engine, SessionLocal, Base
from sqlalchemy.dialects.postgresql import insert
from app.models.original_story_model import OriginalStoryModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 外部 API 基础 URL
EXTERNAL_API_BASE_URL = "http://106.52.130.188:8889"


def get_stories_by_level(story_type: int, level: int) -> Optional[List[Dict[str, Any]]]:
    """
    从外部 API 获取指定级别和类型的故事列表。

    Args:
        story_type: 故事类型 (2 表示中文绘本)。
        level: 故事级别。

    Returns:
        包含故事详情的字典列表，或在出错时返回 None。
    """
    list_url = (
        f"{EXTERNAL_API_BASE_URL}/content/getContentListByLevel/{story_type}/{level}"
    )
    logger.info(f"Fetching stories from: {list_url}")

    try:
        response = requests.get(list_url, timeout=20)
        if response.status_code != 200:
            logger.error(
                f"Failed to fetch stories for level {level}. Status: {response.status_code}"
            )
            return None

        data = response.json()
        if data.get("code") != 200:
            logger.error(f"API error for level {level}. Message: {data.get('msg')}")
            return None

        return data.get("data", [])

    except requests.exceptions.RequestException as e:
        logger.exception(f"Request failed for level {level}: {e}")
        return None


def sync_stories():
    """
    主同步函数：获取所有旧故事并存入数据库。
    使用 "INSERT ... ON CONFLICT DO UPDATE" (UPSERT) 逻辑，确保数据同步且无冗余。
    """
    logger.info("Starting to sync original stories...")

    # 1. 确保表已创建
    logger.info("Creating 'original_stories' table if not exists...")
    Base.metadata.create_all(bind=engine)
    logger.info("Table check complete.")

    db = SessionLocal()
    try:
        # 2. 定义要同步的级别范围 (中文绘本: 1-958)
        for level in range(1, 959):
            stories_data = get_stories_by_level(story_type=2, level=level)

            if stories_data is None:
                logger.warning(f"Skipping level {level} due to fetch error.")
                continue

            if not stories_data:
                logger.info(f"No stories found for level {level}.")
                continue

            stories_to_upsert = []
            for story_data in stories_data:
                story_id = story_data.get("storyId")
                if not story_id:
                    continue

                # 合并段落内容
                paragraphs = story_data.get("paragraphs", [])
                content = " ".join(
                    p.get("text", "")
                    for p in paragraphs
                    if p.get("sequenceOrder", -1) != 0
                ).strip()

                stories_to_upsert.append(
                    {
                        "id": story_id,
                        "name": story_data.get("storyName"),
                        "level": story_data.get("storyLevel"),
                        "content": content,
                    }
                )

            if not stories_to_upsert:
                continue

            # 3. 使用 PostgreSQL 的 ON CONFLICT DO UPDATE (UPSERT)
            stmt = insert(OriginalStoryModel).values(stories_to_upsert)
            update_stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "name": stmt.excluded.name,
                    "level": stmt.excluded.level,
                    "content": stmt.excluded.content,
                    "updated_at": datetime.now(timezone.utc),
                },
            )
            db.execute(update_stmt)
            db.commit()
            logger.info(
                f"Synced level {level}: Upserted {len(stories_to_upsert)} stories."
            )

    finally:
        db.close()

    logger.info("Original stories synchronization finished.")


if __name__ == "__main__":
    sync_stories()
