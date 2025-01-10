# filepath: app/services/story_service.py
from app.models.story_model import Story


class StoryService:
    """故事服务，用于处理故事的业务逻辑。"""

    def generate_story(
        self,
        vocabulary_level: int,
        scene_id: str,
        word_count: int,
        new_char_rate: float,
        key_word_ids: list = None,
    ) -> Story:
        """生成故事。"""
        story = Story(
            title="测试故事",
            content="这是一个测试故事",
            vocabulary_level=vocabulary_level,
            scene_id=scene_id,
            word_count=word_count,
            new_words=[],
            new_char_rate=new_char_rate,
            key_words=[],
        )
        story.save()
        return story

    def get_story(self, story_id: str) -> Story:
        """根据 ID 获取故事。"""
        return Story.find_by_id(story_id)

    def update_story(self, story_id: str, updated_data: dict) -> bool:
        """更新故事。"""
        return Story.update(story_id, updated_data)

    def delete_story(self, story_id: str) -> bool:
        """删除故事。"""
        return Story.delete(story_id)
