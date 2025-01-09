# filepath: app/services/story_service.py
from app.models.story import Story
from app.models.scene import Scene
from app.models.word import Word
from app.utils.json_storage import JSONStorage


class StoryService:
    """故事服务类，负责故事生成、升级/降级等业务逻辑。"""

    def __init__(self):
        self.story_storage = JSONStorage("data/stories.json")
        self.scene_storage = JSONStorage("data/scenes.json")
        self.word_storage = JSONStorage("data/words.json")

    def get_story(self, story_id: str) -> dict:
        """根据 ID 获取故事。"""
        return Story.find_by_id(story_id)

    def update_story(self, story_id: str, updated_data: dict) -> bool:
        """更新故事信息。"""
        return Story.update(story_id, updated_data)

    def delete_story(self, story_id: str) -> bool:
        """删除故事。"""
        return Story.delete(story_id)

    def generate_story(
        self,
        vocabulary_level: int,
        scene_id: str,
        word_count: int,
        new_char_rate: float,
        key_word_ids: list,
    ) -> Story:
        """
        生成符合要求的故事。
        - vocabulary_level: 目标词汇级别（1-100）
        - scene_id: 场景ID
        - word_count: 故事字数
        - new_char_rate: 目标生字率（0-1）
        - key_word_ids: 重点词汇ID列表
        """
        # 1. 根据 scene_id 获取场景
        scene = Scene.find_by_id(scene_id)
        if not scene:
            raise ValueError(f"Scene with ID {scene_id} not found")

        # 2. 根据 key_word_ids 获取重点词汇
        key_words = []
        for word_id in key_word_ids:
            word = Word.find_by_id(word_id)
            if word:
                key_words.append(word)

        # 3. 调用 DeepSeek API 生成故事（此处为伪代码）
        story_content = self._call_deepseek_api(
            vocabulary_level, scene, word_count, new_char_rate, key_words
        )

        # 4. 创建 Story 对象并保存
        story = Story(
            title=f"Generated Story for Level {vocabulary_level}",
            content=story_content,
            vocabulary_level=vocabulary_level,
            scene_id=scene_id,
            word_count=word_count,
            new_words=[],  # 确保这是一个空列表
            new_char_rate=new_char_rate,
            key_words=key_words,  # 确保这是一个列表
        )
        story.save()
        return story

    def _call_deepseek_api(
        self,
        vocabulary_level: int,
        scene: Scene,
        word_count: int,
        new_char_rate: float,
        key_words: list,
    ) -> str:
        """调用 DeepSeek API 生成故事内容（伪代码）。"""
        # 这里可以集成 DeepSeek API 的实际调用逻辑
        return "这是一个生成的故事内容..."
