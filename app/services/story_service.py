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
from app.services.ai_service import AIService  # 导入 AIService
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
        ai_service: AIService,  # 替换 deepseek_client
    ):
        self.word_service = word_service
        self.scene_service = scene_service
        self.literacy_calculator = literacy_calculator
        self.ai_service = ai_service  # 替换 deepseek_client
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
            "scene_name": scene.name,
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
        for message in messages:
            print(message["content"])
        print("====================================")

        try:
            #  使用 AI 服务生成故事
            ai_message = self.ai_service.generate_story(
                prompt="\n".join([message["content"] for message in messages])
            )

            try:
                ai_response = ai_message  # json.loads(ai_message)
                title = ai_response.get("title")
                content = ai_response.get("content")
                ai_key_words = (
                    ai_response.get("key_words") if ai_response.get("key_words") else []
                )

                # 调用 LiteracyCalculator 计算词数、生词率和生词列表
                word_count, new_word_rate, unknown_words = (
                    self.literacy_calculator.calculate_vocabulary_rate(
                        content, vocabulary_level
                    )
                )

                story = StoryModel(
                    title=title,
                    content=content,
                    vocabulary_level=vocabulary_level,
                    scene=scene_id,
                    word_count=word_count,  # 使用计算出的词数
                    new_word_rate=new_word_rate,  # 使用计算出的生词率
                    key_words=ai_key_words,
                    unknown_words=unknown_words,  # 使用计算出的生词列表
                )

                self.add_story(story)  # 保存 story
                return story

            except (json.JSONDecodeError, TypeError) as e:
                logging.error(f"AI 服务返回无效的 JSON 格式: {e}")
                raise Exception(f"AI 服务返回无效的 JSON 格式: {e}")
        except Exception as e:
            logging.error(f"AI 服务调用失败: {e}")
            raise Exception(f"AI 服务调用失败: {e}")
