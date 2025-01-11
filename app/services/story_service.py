# app/services/story_service.py
import logging
import re
import json
from jinja2 import Environment, FileSystemLoader
from app.config import Config
from app.models.story_model import StoryModel
from app.services.word_service import WordService
from app.services.scene_service import SceneService
from openai import OpenAI
from uuid import uuid4


class StoryService:
    def __init__(self):
        self.word_service = WordService()
        self.scene_service = SceneService()
        self.deepseek_api = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"
        )
        self.template_env = Environment(loader=FileSystemLoader("app/templates"))
        self.messages = []  # 用于存储多轮对话的上下文

    def _custom_segment(self, text):
        """
        自定义分词函数
        Args:
            text: 待分词的文本字符串
        Returns:
            一个列表， 包含分词后的结果， 例如  [('你好', 'l'), ('，', 'x'), ('我', 'r'), ('喜欢', 'v'), ('跑步', 'n'), ('。', 'x')]
        """
        words = list(self.word_service.words.values())
        words.sort(
            key=lambda word: len(word.word), reverse=True
        )  # 按词语长度进行排序，从长到短

        result = []
        start = 0
        while start < len(text):
            matched = False
            for word_model in words:
                if text.startswith(word_model.word, start):
                    result.append((word_model.word, word_model.part_of_speech))
                    start += len(word_model.word)
                    matched = True
                    break
            if not matched:  # 处理没有匹配到的字符，默认为 "其他"
                result.append((text[start], "其他"))
                start += 1
        return result

    def _calculate_literacy_rate(self, text, target_level):
        """
        计算指定级别已知字率和生字率。

        Args:
            text: 待分析的文本字符串。
            target_level: 目标级别 (整数)。
        Returns:
            一个包含已知字率和生字率的元组 (known_rate, unknown_rate)。
        """
        known_word_pos_dict = self._load_known_words(target_level)
        chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
        total_chinese_words = len(chinese_chars)

        if total_chinese_words == 0:
            return (1, 0)

        known_words_count = 0
        # 使用自定义分词
        seg_list = self._custom_segment(text)
        text_word_pos = {}
        start = 0

        for word, flag in seg_list:
            for i in range(len(word)):
                text_word_pos[start] = (word[i], flag)
                start += 1

        for i in range(len(chinese_chars)):
            char = chinese_chars[i]
            char_pos = text_word_pos.get(i)

            if char_pos is not None:
                char_in_text, pos_in_text = char_pos
                is_known = False
                if char_in_text in known_word_pos_dict:
                    if pos_in_text in known_word_pos_dict[char_in_text]:
                        is_known = True
                    else:
                        for word_model in self.word_service.words.values():
                            if word_model.chaotong_level <= target_level:
                                for char_data in word_model.characters:
                                    if (
                                        char_data["character"] == char_in_text
                                        and char_data["part_of_speech"]
                                        in known_word_pos_dict[char_in_text]
                                    ):
                                        is_known = True
                                        break
                                if is_known:
                                    break
                if is_known:
                    known_words_count += 1

        known_rate = known_words_count / total_chinese_words
        unknown_rate = 1 - known_rate
        return (known_rate, unknown_rate)

    def _load_known_words(self, target_level):
        """
        加载小于等于目标级别的所有词汇。
        Args:
            target_level: 目标级别 (整数)。
        Returns:
            一个字典，key为字，value为词性集合(set), 例如 {"好": {"a", "ad"}, "人": {"n"}, "学": {"v"}}
        """
        known_words_dict = {}
        for word_model in self.word_service.words.values():
            if word_model.chaotong_level <= target_level:
                for char_data in word_model.characters:
                    char = char_data["character"]
                    part_of_speech = char_data["part_of_speech"]
                    if char not in known_words_dict:
                        known_words_dict[char] = set()
                    known_words_dict[char].add(part_of_speech)
        return known_words_dict

    def _generate_prompt(
        self, vocabulary_level, scene_id, story_word_count, key_word_ids
    ):
        """
        生成提示语。
        Args:
            vocabulary_level: 目标级别 (整数)。
            scene_id: 场景 ID
            story_word_count: 故事字数。
            key_word_ids: 重点词汇 ID 列表
        Returns:
            提示语字符串。
        """
        logging.info(
            f"Generating prompt, vocabulary_level: {vocabulary_level}, scene_id: {scene_id}, story_word_count: {story_word_count}, key_word_ids: {key_word_ids}"
        )
        scene = self.scene_service.get_scene(scene_id)
        if not scene:
            logging.error(f"Scene not found: {scene_id}")
            return None

        key_words = []
        if key_word_ids:
            for word_id in key_word_ids:
                word = self.word_service.get_word(word_id)
                if not word:
                    logging.error(f"Key word not found, word_id: {word_id}")
                    return None
                key_words.append(word.to_dict())
        template = self.template_env.get_template("prompt_template.txt")

        word_count_tolerance = Config.STORY_WORD_COUNT_TOLERANCE
        word_count_min = max(1, story_word_count - word_count_tolerance)
        word_count_max = story_word_count + word_count_tolerance

        data = {
            "scene_description": scene.description,
            "vocabulary_level": vocabulary_level,
            "word_count_min": word_count_min,
            "word_count_max": word_count_max,
            "key_words": key_words,
        }
        prompt = template.render(data)
        self.messages.append({"role": "user", "content": prompt})

        # 已知词汇
        known_words = self._load_known_words(vocabulary_level)
        template = self.template_env.get_template("known_words_template.txt")
        data = {"known_words": json.dumps(list(known_words.keys()), ensure_ascii=False)}
        prompt = template.render(data)
        self.messages.append({"role": "user", "content": prompt})

        template = self.template_env.get_template("final_instruction.txt")
        prompt = template.render()
        self.messages.append({"role": "user", "content": prompt})
        return self.messages

    def generate_story(
        self, vocabulary_level, scene_id, story_word_count, new_char_rate, key_word_ids
    ):
        """
        生成故事。
        Args:
           vocabulary_level: 目标级别 (整数)。
            scene_id: 场景 ID。
           story_word_count: 故事字数。
            new_char_rate: 目标生字率。
           key_word_ids: 重点词汇 ID 列表
        Returns:
            StoryModel 对象
        """
        logging.info(
            f"Generating story, vocabulary_level: {vocabulary_level}, scene_id: {scene_id}, story_word_count: {story_word_count}, new_char_rate: {new_char_rate}, key_word_ids: {key_word_ids}"
        )
        self.messages = []  # 清空上下文
        prompt_messages = self._generate_prompt(
            vocabulary_level, scene_id, story_word_count, key_word_ids
        )

        if not prompt_messages:
            logging.error("Failed to generate prompt message")
            return None

        try:
            ai_response = self.deepseek_api.chat.completions.create(
                model="deepseek-chat", messages=prompt_messages
            )
            ai_content = ai_response.choices[0].message.content
            story_data = json.loads(ai_content)
        except Exception as e:
            logging.error(f"Failed to generate story: {e}")
            return None

        # Validate story
        title = story_data.get("title")
        content = story_data.get("content")
        ai_key_words = story_data.get("key_words")

        if not title or not content or not ai_key_words:
            logging.error(
                f"Failed to generate story, missing title, content or key_words: {ai_content}"
            )
            return None

        known_rate, unknown_rate = self._calculate_literacy_rate(
            content, vocabulary_level
        )
        new_char = len(re.findall(r"[\u4e00-\u9fff]", content)) * unknown_rate

        new_story = StoryModel(
            story_id=str(uuid4()),
            title=title,
            content=content,
            vocabulary_level=vocabulary_level,
            scene=scene_id,
            word_count=len(re.findall(r"[\u4e00-\u9fff]", content)),
            new_char_rate=unknown_rate,
            new_char=int(new_char),
            key_words=ai_key_words,
        )
        return new_story
