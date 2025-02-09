# app/services/story_service.py
import json
import logging
import re
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader
from app.config import Config
from app.models.story_model import StoryModel
from app.services.word_service import WordService
from app.services.scene_service import SceneService
from app.utils.literacy_calculator import LiteracyCalculator
from openai import OpenAI
import logging
from enum import Enum
from app.utils.json_storage import JSONStorage


class StoryService:
    """
    故事服务，提供故事相关的业务逻辑。
    """

    def __init__(
        self,
        word_service: WordService,
        scene_service: SceneService,
        literacy_calculator: LiteracyCalculator,
        deepseek_client,
    ):
        self.word_service = word_service
        self.scene_service = scene_service
        self.literacy_calculator = literacy_calculator
        self.deepseek_client = deepseek_client
        self.template_env = Environment(
            loader=FileSystemLoader("app/prompts"),
            enable_async=True,
        )
        self.story_storage = JSONStorage(Config.STORIES_FILE_PATH)  #  新增

    class DialogueState(Enum):
        INIT = 1
        PROVIDE_KNOWN_WORDS = 2
        FINAL_INSTRUCTION = 3
        FAILED = 4

    def get_prompt(self, file_name, data):
        template = self.template_env.get_template(file_name)
        prompt = template.render(data)
        return prompt

    def _validate_story(
        self,
        story: StoryModel,
        new_word_rate: float,  # 目标生词率
        new_word_rate_tolerance: float = None,
        story_word_count_tolerance: int = None,
    ) -> bool:
        """
        验证生成的故事是否符合要求
        """
        if new_word_rate_tolerance is None:
            new_word_rate_tolerance = Config.NEW_WORD_RATE_TOLERANCE
        if story_word_count_tolerance is None:
            story_word_count_tolerance = Config.STORY_WORD_COUNT_TOLERANCE

        if not (
            story.new_word_rate
            >= new_word_rate - new_word_rate_tolerance  # 使用参数传递
            and story.new_word_rate
            <= new_word_rate + new_word_rate_tolerance  # 使用参数传递
        ):
            logging.warning(
                f"Story new word rate {story.new_word_rate} not within tolerance {new_word_rate_tolerance}"
            )
            return False
        if not (
            story.story_word_count
            >= (story.story_word_count - story_word_count_tolerance)
            and story.story_word_count
            <= (story.story_word_count + story_word_count_tolerance)
        ):
            logging.warning(
                f"Story word count {story.story_word_count} not within tolerance {story_word_count_tolerance}"
            )
            return False

        return True

    def generate_story(
        self,
        vocabulary_level: int,
        scene_id: str,
        story_word_count: int,
        new_word_rate: float,
        key_word_ids: List[str] = None,
        new_word_rate_tolerance: float = None,
        story_word_count_tolerance: int = None,
        request_limit: int = None,
    ) -> StoryModel:
        """
        生成故事
        """
        # 1. 初始化状态
        messages = []
        key_words = (
            []
            if not key_word_ids
            else self.word_service.get_key_words_by_ids(key_word_ids)
        )
        scene = self.scene_service.get_scene_by_id(scene_id)
        if not scene:
            raise Exception(f"Scene id {scene_id} not found")

        # 2. 加载 initial_prompt
        initial_prompt = self.get_prompt("initial_prompt.txt", {})
        messages.append({"role": "user", "content": initial_prompt})

        # 3. 准备 known_words_prompt 数据
        known_words_prompt_data = {
            "scene_description": scene.description,
            "vocabulary_level": vocabulary_level,
            "story_word_count_min": story_word_count - story_word_count_tolerance
            if story_word_count_tolerance is not None
            else story_word_count,
            "story_word_count_max": story_word_count + story_word_count_tolerance
            if story_word_count_tolerance is not None
            else story_word_count,
            "new_word_rate": new_word_rate,
            "key_words": json.dumps(key_words, ensure_ascii=False),
            "scene_name": scene.name,  # 添加 scene_name
        }

        # 4. 获取已知词汇
        known_words_list = self.word_service.get_words_below_level(vocabulary_level)
        if known_words_list:
            known_words_prompt_data["known_words"] = json.dumps(
                [
                    {"word": word.word, "part_of_speech": word.part_of_speech}
                    for word in known_words_list
                ],
                ensure_ascii=False,  # 修改
            )
        else:
            known_words_prompt_data["known_words"] = json.dumps([])

        # 5. 渲染 known_words_prompt 模板
        known_words_prompt = self.get_prompt(
            "known_words_prompt.txt", known_words_prompt_data
        )
        messages.append({"role": "user", "content": known_words_prompt})

        # 6. 发送最终指令
        final_instruction = self.get_prompt("final_instruction_prompt.txt", {})
        messages.append({"role": "user", "content": final_instruction})

        print("====================================")
        print(messages)
        print("====================================")

        try:
            response = self.deepseek_client.chat.completions.create(
                # model="deepseek-chat", messages=messages
            )
            ai_message = response.choices[0].message.content
            messages.append({"role": "assistant", "content": ai_message})

            try:
                ai_response = json.loads(ai_message)
                title = ai_response.get("title")
                content = ai_response.get("content")
                ai_key_words = (
                    ai_response.get("key_words") if ai_response.get("key_words") else []
                )
                known_rate, unknown_rate, message = (
                    self.literacy_calculator.calculate_vocabulary_rate(
                        content, vocabulary_level
                    )
                )
                if message:
                    raise Exception(f"生词率计算失败: {message}")

                story = StoryModel(
                    title=title,
                    content=content,
                    vocabulary_level=vocabulary_level,
                    scene=scene_id,
                    story_word_count=len(re.findall(r"[\u4e00-\u9fff]", content)),
                    new_word_rate=unknown_rate,
                    new_words=int(
                        len(re.findall(r"[\u4e00-\u9fff]", content)) * unknown_rate
                    ),
                    key_words=ai_key_words,
                )
                story.new_words = int(story.story_word_count * story.new_word_rate)
                is_valid = self._validate_story(
                    story,
                    new_word_rate,
                    new_word_rate_tolerance,
                    story_word_count_tolerance,
                )
                if not is_valid:
                    logging.warning(f"Story validation failed")
                    raise Exception(f"Story validation failed")

                self.add_story(story)  # 保存 story
                return story

            except (json.JSONDecodeError, TypeError) as e:
                logging.error(f"AI 服务返回无效的 JSON 格式: {e}")
                raise Exception(f"AI 服务返回无效的 JSON 格式: {e}")
        except Exception as e:
            logging.error(f"AI 服务调用失败: {e}")
            raise Exception(f"AI 服务调用失败: {e}")

    def add_story(self, story: StoryModel):
        """将故事添加到 JSON 文件中。"""
        story_data = story.to_dict()
        self.story_storage.add(story_data)
        logging.info(f"Story added successfully with id: {story.id}")

    def get_story_by_id(self, story_id: str) -> StoryModel:
        """从 JSON 文件中根据 ID 获取故事。"""
        story_data = next(
            (
                item
                for item in self.story_storage.load()
                if item.get("story_id") == story_id
            ),
            None,
        )
        if story_data:
            return StoryModel.from_dict(story_data)
        return None

    def update_story(self, story: StoryModel) -> bool:
        """更新 JSON 文件中的故事。"""
        story_data = story.to_dict()
        success = self.story_storage.update(story.id, story_data)
        if success:
            logging.info(f"Story updated successfully with id: {story.id}")
        else:
            logging.warning(f"Story not found for update with id: {story.id}")
        return success

    def delete_story(self, story_id: str) -> bool:
        """从 JSON 文件中删除一条数据。"""
        success = self.story_storage.delete(story_id)
        if success:
            logging.info(f"Story deleted successfully with id: {story_id}")
        else:
            logging.warning(f"Story not found for deletion with id: {story_id}")
        return success
