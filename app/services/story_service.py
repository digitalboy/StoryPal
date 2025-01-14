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

    def _render_prompt(self, template_name: str, data: Dict) -> str:
        """
        渲染提示语模板。
        Args:
            template_name (str): 模板名称。
            data (Dict): 模板数据。
        Returns:
            str: 渲染后的提示语。
        """
        template = self.template_env.get_template(template_name)
        return template.render(data)

    def _load_known_words(self, target_level: int) -> List[str]:
        """
        加载已知字列表
        Args:
           target_level (int): 目标级别
        Returns:
            List[str]: 已知字列表
        """
        known_characters = set()
        for word_model in self.word_service.words.values():
            if word_model.chaotong_level < target_level:
                for char_data in word_model.characters:
                    known_characters.add(char_data["character"])
        return list(known_characters)

    def _validate_story(
        self,
        story: StoryModel,
        new_char_rate_tolerance: float = None,
        word_count_tolerance: float = None,
        story_word_count_tolerance: int = None,
    ) -> bool:
        """
        验证生成的故事是否符合要求
        Args:
            story (StoryModel): 故事模型对象。
            new_char_rate_tolerance (float, optional):  生字率容差值，默认使用配置文件的值.
            word_count_tolerance (float, optional): 字数 容差值，默认使用配置文件的值.
            story_word_count_tolerance (int, optional): 故事字数容差值，默认使用配置文件的值.
        Returns:
            bool: 如果故事符合要求，则返回 True，否则返回 False。
        """
        if new_char_rate_tolerance is None:
            new_char_rate_tolerance = Config.NEW_CHAR_RATE_TOLERANCE
        if word_count_tolerance is None:
            word_count_tolerance = Config.WORD_COUNT_TOLERANCE
        if story_word_count_tolerance is None:
            story_word_count_tolerance = Config.STORY_WORD_COUNT_TOLERANCE

        word_count_min = story.word_count * (1 - word_count_tolerance)
        word_count_max = story.word_count * (1 + word_count_tolerance)

        if not (word_count_min <= story.word_count <= word_count_max):
            logging.warning(
                f"Story word count {story.word_count} not within tolerance {word_count_tolerance}"
            )
            return False

        if not (
            story.new_char_rate - new_char_rate_tolerance
            <= story.new_char_rate
            <= story.new_char_rate + new_char_rate_tolerance
        ):
            logging.warning(
                f"Story new char rate {story.new_char_rate} not within tolerance {new_char_rate_tolerance}"
            )
            return False
        if not (
            story.word_count >= (story.word_count - story_word_count_tolerance)
            and story.word_count <= (story.word_count + story_word_count_tolerance)
        ):
            logging.warning(
                f"Story word count {story.word_count} not within tolerance {story_word_count_tolerance}"
            )
            return False

        return True

    def generate_story(
        self,
        vocabulary_level: int,
        scene_id: str,
        story_word_count: int,
        new_char_rate: float,
        key_word_ids: List[str] = None,
        new_char_rate_tolerance: float = None,
        word_count_tolerance: float = None,
        story_word_count_tolerance: int = None,
        request_limit: int = None,
    ) -> StoryModel:
        """
        生成故事
        Args:
            vocabulary_level (int): 目标词汇级别.
            scene_id (str): 场景ID.
            story_word_count (int): 故事字数.
            new_char_rate (float): 目标生字率.
            key_word_ids (List[str], optional): 重点词汇ID列表.
            new_char_rate_tolerance (float, optional):  生字率容差值，默认使用配置文件的值.
            word_count_tolerance (float, optional): 字数 容差值，默认使用配置文件的值.
            story_word_count_tolerance (int, optional): 故事字数容差值，默认使用配置文件的值.
            request_limit (int, optional): 请求频率限制，默认使用配置文件的值.
        Returns:
            StoryModel: 生成的故事模型对象.
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

        # 2. 生成初始提示语
        initial_prompt_data = {
            "scene_description": scene.description,
            "vocabulary_level": vocabulary_level,
            "word_count_min": story_word_count - story_word_count_tolerance
            if story_word_count_tolerance is not None
            else story_word_count,
            "word_count_max": story_word_count + story_word_count_tolerance
            if story_word_count_tolerance is not None
            else story_word_count,
            "new_char_rate": new_char_rate,
            "key_words": json.dumps(key_words, ensure_ascii=False),
        }
        initial_prompt = self._render_prompt("initial_prompt.txt", initial_prompt_data)
        messages.append({"role": "user", "content": initial_prompt})

        # 3. 获取已知词汇 (目标等级一下的所有词汇)
        known_words_prompt_data = {}
        known_words_list = self._load_known_words(vocabulary_level)
        if known_words_list:
            known_words_prompt_data["known_words"] = json.dumps(
                known_words_list, ensure_ascii=False
            )
            known_words_prompt = self._render_prompt(
                "known_words_prompt.txt", known_words_prompt_data
            )
            messages.append({"role": "user", "content": known_words_prompt})

        # 4. 发送最终指令
        final_instruction = self._render_prompt("final_instruction_prompt.txt", {})
        messages.append({"role": "user", "content": final_instruction})
        try:
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat", messages=messages
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
                known_rate, unknown_rate = (
                    self.literacy_calculator.calculate_literacy_rate(
                        content, vocabulary_level
                    )
                )
                story = StoryModel(
                    title=title,
                    content=content,
                    vocabulary_level=vocabulary_level,
                    scene=scene_id,
                    word_count=len(re.findall(r"[\u4e00-\u9fff]", content)),
                    new_char_rate=unknown_rate,
                    new_char=int(
                        len(re.findall(r"[\u4e00-\u9fff]", content)) * unknown_rate
                    ),
                    key_words=ai_key_words,
                )

                if self._validate_story(
                    story,
                    new_char_rate_tolerance,
                    word_count_tolerance,
                    story_word_count_tolerance,
                ):
                    return story
                else:
                    logging.warning("Story validation failed")
                    raise Exception("Story validation failed")

            except (json.JSONDecodeError, TypeError) as e:
                logging.error(f"AI 服务返回无效的 JSON 格式: {e}")
                raise Exception(f"AI 服务返回无效的 JSON 格式: {e}")
        except Exception as e:
            logging.error(f"AI 服务调用失败: {e}")
            raise Exception(f"AI 服务调用失败: {e}")
