# app/services/story_service.py
import json
import logging
import re
import uuid
from typing import Dict, List, Tuple
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI
import jieba
import jieba.posseg
from app.config import Config
from app.models.story_model import StoryModel
from app.services.word_service import WordService
from app.services.scene_service import SceneService
from app.utils.error_handling import handle_error
from enum import Enum


JIEBA_POS_MAP = {
            'n': 'n',      # 名词
            'v': 'v',      # 动词
            'a': 'a',      # 形容词
            'd': 'd',      # 副词
            'p': 'PREP',    # 介词
            'c': 'CONJ',    # 连词
            'u': 'PART',   # 助词
            'm': 'NUM',      # 数词
            'q': 'MW',     # 量词
            'r': 'PR',    # 代词
            'f': 'f',      # 方位词
            's': 's',     # 处所词
            't': 't',      # 时间词
            'l': 'OTHER',  # 临时语素, 转换为 '其他'
            'x': 'x',  # 标点符号
            'PER': 'PER', # 人名
            'LOC': 'LOC', # 地名
            'ORG': 'ORG', # 机构名
            'ADJ': 'ADJ',
            'ADV': 'ADV',
            "PR": "PR",
            "NUM": "NUM",
            "MW": "MW",
            "PREP": "PREP",
             "CONJ": "CONJ",
            "PART": "PART",
            'eng': 'OTHER',   # 英文，转换为 '其他'
        }


class ConversationState(Enum):
    """
    多轮对话的状态
    """
    INIT = "INIT"
    PROVIDE_KNOWN_WORDS = "PROVIDE_KNOWN_WORDS"
    FINAL_INSTRUCTION = "FINAL_INSTRUCTION"
    FAILED = "FAILED"


class DeepSeekClient:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.chat = self.client.chat


def map_jieba_pos(jieba_pos):
    """
    将 jieba 词性转换为 words.json 中的词性
    """
    return JIEBA_POS_MAP.get(jieba_pos, "OTHER")  # 如果不存在，默认设置为 '其他'


class StoryService:
    """
    故事服务，提供故事相关的业务逻辑。
    """

    def __init__(self):
        self.word_service = WordService()
        self.scene_service = SceneService()
        self.deepseek_client = DeepSeekClient(Config.DEEPSEEK_API_KEY)
        self.env = Environment(loader=FileSystemLoader("app/prompts"))
        self.state = ConversationState.INIT  # 初始化对话状态
        self.messages = [] # 初始化对话消息列表
        self.max_retries = 3  # 最大重试次数
        self.load_jieba_userdict() # 加载自定义词典
        logging.info("Story service initialized")

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

    def _custom_segment(self, text):
        """
        自定义分词函数
        Args:
            text: 待分词的文本字符串
        Returns:
            一个列表， 包含分词后的结果， 例如  [('你好', 'v'), ('，', 'x'), ('我', 'r'), ('喜欢', 'v'), ('跑步', 'n'), ('。', 'x')]
        """
        words = list(self.word_service.words.values())
        words.sort(key=lambda word: len(word.word), reverse=True) # 按词语长度进行排序，从长到短

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
            if not matched: # 如果没有匹配的词，则使用 jieba 分词，并转换词性
                jieba_words = jieba.cut(text[start:])
                for jieba_word in jieba_words:
                    if jieba_word.strip(): # 过滤掉空格
                        jieba_pos = jieba.posseg.cut(jieba_word)
                        for word, flag in jieba_pos:
                           result.append((word, map_jieba_pos(flag)))
                start += len(text[start:])
                matched = True  #  使用 jieba 之后，跳出当前的循环

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
                           if word_model.chaotong_level <= target_level and char_in_text == word_model.word:
                                for char_data in word_model.characters:
                                    if char_data["character"] == char_in_text and char_data["part_of_speech"] in known_word_pos_dict[char_in_text] :
                                        is_known = True
                                        break
                                if is_known:
                                   break

               if is_known:
                known_words_count += 1

        known_rate = known_words_count / total_chinese_words
        unknown_rate = 1 - known_rate
        return (known_rate, unknown_rate)


    def _call_deepseek_api(self, messages: List[Dict]) -> str:
      """
      调用 DeepSeek API
        Args:
            messages: 对话历史
        Returns:
            DeepSeek API 返回的内容
      """
      try:
          response = self.deepseek_client.chat.completions.create(
              model="deepseek-chat",
              messages=messages,
          )
          return response.choices[0].message.content
      except Exception as e:
         logging.error(f"DeepSeek API call failed: {e}")
         raise Exception(f"DeepSeek API call failed: {e}")

    def _create_initial_prompt(
        self,
        scene_description: str,
        vocabulary_level: int,
        word_count_min: int,
        word_count_max: int,
        new_char_rate: float,
        key_words: List[Dict],
    ) -> str:
      """
        创建初始提示语
      """
      template = self.env.get_template("initial_prompt.txt")
      return template.render(
          scene_description=scene_description,
          vocabulary_level=vocabulary_level,
          word_count_min=word_count_min,
          word_count_max=word_count_max,
          new_char_rate=new_char_rate,
          key_words=json.dumps(key_words, ensure_ascii=False),
      )

    def _create_provide_known_words_prompt(self, known_words: List[Dict]) -> str:
        """
          创建提供已知词汇的提示语
        """
        template = self.env.get_template("provide_known_words_prompt.txt")
        return template.render(known_words=json.dumps(known_words, ensure_ascii=False))

    def _validate_story(self, story: StoryModel, target_level: int,  new_char_rate: float,  story_word_count: int, new_char_rate_tolerance:float, word_count_tolerance:float, story_word_count_tolerance:int ) -> bool:
        """
        验证故事是否符合要求
        Args:
            story: 故事模型
            target_level: 目标级别
            new_char_rate: 目标生字率
            story_word_count: 目标故事字数
            new_char_rate_tolerance: 生字率容差值
            word_count_tolerance: 字数容差值
            story_word_count_tolerance: 故事字数容差值

        Returns:
            bool: True if the story is valid, False otherwise
        """
        if not (1 <= target_level <= 100):
            raise ValueError("Validation failed: 'vocabulary_level' must be between 1 and 100")
        if not (0 <= new_char_rate <= 1):
            raise ValueError("Validation failed: 'new_char_rate' must be between 0 and 1")
        if  story_word_count <= 0:
             raise ValueError("Validation failed: 'story_word_count' must be greater than 0")


        known_rate, unknown_rate = self._calculate_literacy_rate(story.content, target_level)

        # 验证生字率
        if not (new_char_rate - new_char_rate_tolerance <= unknown_rate <= new_char_rate + new_char_rate_tolerance):
            logging.error(f"生字率验证失败: expected {new_char_rate}, actual {unknown_rate}, tolerance {new_char_rate_tolerance}")
            return False

        #验证字数
        word_count = len(re.findall(r"[\u4e00-\u9fff]", story.content))
        if not (story_word_count * (1 - word_count_tolerance) <= word_count <= story_word_count * (1 + word_count_tolerance)):
            logging.error(f"字数验证失败: expected {story_word_count}, actual {word_count}, tolerance {word_count_tolerance}")
            return False


        #验证故事字数
        if not (story_word_count - story_word_count_tolerance <= word_count <= story_word_count + story_word_count_tolerance):
             logging.error(f"故事字数验证失败: expected {story_word_count}, actual {word_count}, tolerance {story_word_count_tolerance}")
             return False
        #  验证重点词汇
        story_words =  [word["word"] for word in story.key_words]
        for key_word in [word["word"] for word in story.key_words]:
            if key_word not in story_words:
                logging.error(f"重点词汇验证失败: {key_word} not in story")
                return False
        return True

    def _handle_deepseek_response(self, response_content: str) -> Dict:
         """
         处理 DeepSeek API 的返回结果
          Args:
              response_content: DeepSeek API 返回的 JSON 字符串
          Returns:
             Dict:  包含 title, content, key_words 的字典
         """
         try:
            response_json = json.loads(response_content)
            if not isinstance(response_json, dict):
                raise ValueError("DeepSeek API response is not a valid JSON object")
            title = response_json.get("title")
            content = response_json.get("content")
            key_words = response_json.get("key_words")

            if not title or not isinstance(title, str):
               raise ValueError("DeepSeek API response missing 'title'")
            if not content or not isinstance(content, str):
                raise ValueError("DeepSeek API response missing 'content'")
            if not key_words or not isinstance(key_words, list):
                raise ValueError("DeepSeek API response missing 'key_words'")

            return {
               "title": title,
               "content": content,
                "key_words": key_words
           }
         except json.JSONDecodeError as e:
            logging.error(f"DeepSeek API response is not a valid JSON: {e}")
            raise ValueError(f"DeepSeek API response is not a valid JSON: {e}")
         except ValueError as e:
              logging.error(f"DeepSeek API response validation failed: {e}")
              raise ValueError(f"DeepSeek API response validation failed: {e}")

    def load_jieba_userdict(self):
        """
        加载自定义词典
        """
        for word_model in self.word_service.words.values():
          jieba.add_word(word_model.word, tag=map_jieba_pos(word_model.part_of_speech) )


    def generate_story(
        self,
        vocabulary_level: int,
        scene_id: str,
        story_word_count: int,
        new_char_rate: float,
        key_word_ids: List[str] = None,
        new_char_rate_tolerance: float = Config.NEW_CHAR_RATE_TOLERANCE,
        word_count_tolerance: float = Config.WORD_COUNT_TOLERANCE,
        story_word_count_tolerance : int = Config.STORY_WORD_COUNT_TOLERANCE
    ) -> StoryModel:
        """
         生成故事
            Args:
              vocabulary_level: 目标词汇级别
              scene_id: 场景ID
              story_word_count: 故事字数
              new_char_rate: 目标生字率
              key_word_ids: 重点词汇ID列表
              new_char_rate_tolerance: 生字率容差值
              word_count_tolerance: 字数容差值
              story_word_count_tolerance: 故事字数容差值

            Returns:
               StoryModel: 生成的故事
        """
        # 参数验证
        if not isinstance(vocabulary_level, int):
            raise ValueError("Invalid field type: 'vocabulary_level' must be an integer")
        if not isinstance(scene_id, str) or not  self.scene_service.get_scene_by_id(scene_id):
             raise ValueError("Validation failed: 'scene_id' must be a valid UUID")
        if not isinstance(story_word_count, int):
            raise ValueError("Invalid field type: 'story_word_count' must be an integer")
        if not isinstance(new_char_rate, float):
             raise ValueError("Invalid field type: 'new_char_rate' must be a float")
        if not isinstance(new_char_rate_tolerance, float):
             raise ValueError("Invalid field type: 'new_char_rate_tolerance' must be a float")
        if not isinstance(word_count_tolerance, float):
            raise ValueError("Invalid field type: 'word_count_tolerance' must be a float")
        if not isinstance(story_word_count_tolerance, int):
             raise ValueError("Invalid field type: 'story_word_count_tolerance' must be a integer")

        if key_word_ids is None:
          key_word_ids = []

        if key_word_ids:
             for word_id in key_word_ids:
                if not self.word_service.get_word_by_id(word_id):
                     raise ValueError(f"Validation failed: key word id {word_id} not exist")

        # 初始化多轮对话的状态
        self.state = ConversationState.INIT
        self.messages = []
        retries = 0
        story = None

        while self.state != ConversationState.FINAL_INSTRUCTION and retries < self.max_retries:
            if self.state == ConversationState.INIT:
                # 1. 构建初始提示语
                scene = self.scene_service.get_scene_by_id(scene_id)
                if not scene:
                    raise ValueError(f"Scene with id {scene_id} not found")

                key_words = self.get_key_words_by_ids(key_word_ids)

                prompt = self._create_initial_prompt(
                   scene_description=scene.description,
                   vocabulary_level=vocabulary_level,
                   word_count_min=int(story_word_count * (1- word_count_tolerance)),
                   word_count_max=int(story_word_count * (1 + word_count_tolerance)),
                    new_char_rate=new_char_rate,
                   key_words=key_words
                 )

                self.messages.append({"role": "user", "content": prompt})
                self.state = ConversationState.PROVIDE_KNOWN_WORDS
            elif self.state == ConversationState.PROVIDE_KNOWN_WORDS:
                 # 2. 构建提供已知词汇的提示语
                 known_words_dict = self._load_known_words(vocabulary_level)
                 known_words = []
                 for word_model in self.word_service.words.values():
                     if word_model.chaotong_level <= vocabulary_level:
                        known_words.append(word_model.to_dict())
                 prompt = self._create_provide_known_words_prompt(known_words=known_words)
                 self.messages.append({"role": "user", "content": prompt})
                 self.state = ConversationState.FINAL_INSTRUCTION
            elif self.state == ConversationState.FINAL_INSTRUCTION:
                # 3. 调用 DeepSeek API 获取故事
                response_content = self._call_deepseek_api(messages=self.messages)
                try:
                    response = self._handle_deepseek_response(response_content)
                    story = StoryModel(
                      title=response["title"],
                      content=response["content"],
                      vocabulary_level=vocabulary_level,
                      scene=scene_id,
                      word_count = len(re.findall(r"[\u4e00-\u9fff]", response["content"])),
                      key_words=response["key_words"]
                    )
                except ValueError as e:
                     logging.error(f"DeepSeek API response validation failed: {e}")
                     self.state = ConversationState.INIT # 回到初始状态
                     retries += 1
                     continue
                # 4. 验证生成的故事
                try:
                    if self._validate_story(story, vocabulary_level, new_char_rate, story_word_count,  new_char_rate_tolerance, word_count_tolerance, story_word_count_tolerance):
                        known_rate, unknown_rate = self._calculate_literacy_rate(story.content, vocabulary_level)
                        story.new_char_rate = unknown_rate
                        story.new_char = int(len(re.findall(r"[\u4e00-\u9fff]", story.content)) * unknown_rate)
                        break
                    else:
                        self.state = ConversationState.INIT
                        retries += 1
                        logging.error(f"Story validation failed, retrying: {retries}")
                except ValueError as e:
                       logging.error(f"Story validation failed: {e}")
                       self.state = ConversationState.INIT # 回到初始状态
                       retries += 1
                       continue # 如果校验失败，重新开始多轮对话
                except Exception as e:
                    logging.error(f"Unexpected error during story validation: {e}")
                    self.state = ConversationState.INIT # 回到初始状态
                    retries += 1
                    continue # 如果校验失败，重新开始多轮对话


            # 将 AI 的回复添加到 messages 中
            if self.state != ConversationState.INIT and story is None :
                self.messages.append({"role": "assistant", "content": response_content})

        if retries >= self.max_retries and  story is None :
            self.state = ConversationState.FAILED
            logging.error(f"Failed to generate story after {retries} retries.")
            raise Exception(f"Failed to generate story after {retries} retries.")


        return story

    def adjust_story(self, story_id: str, target_level: int) -> StoryModel:
        """
        调整故事
        Args:
            story_id: 故事ID
            target_level: 目标级别
        Returns:
            StoryModel: 调整后的故事
        """
        # 这里只是一个示例，实际的逻辑需要调用 AI 服务进行故事调整，可以复用 generate_story 的多轮对话逻辑。
        story = StoryModel(
            story_id=story_id,
            title="调整后的故事",
            content="调整后的故事内容，词汇难度升级。",
            vocabulary_level=target_level,
            new_char_rate=0.1,
            new_char=2,
            key_words=[],
        )
        return story

    def get_key_words_by_ids(self, key_word_ids: List[str]) -> List[Dict]:
        """
        根据 key_word_ids 获取重点词汇的详细信息。
        Args:
            key_word_ids: 重点词汇 ID 列表。
        Returns:
           List[Dict]: 重点词汇的详细信息列表，包含 `word`, `pinyin`, `definition`, `part_of_speech` 和 `example`
        """
        key_words = []
        for word_id in key_word_ids:
            word_model = self.word_service.get_word_by_id(word_id)
            if word_model:
                key_words.append(
                    {
                        "word": word_model.word,
                        "pinyin": None,  # 暂时设置为 None, 后续可以从 words.json 中获取
                        "definition": None,  # 暂时设置为 None, 后续可以从 words.json 中获取
                        "part_of_speech": word_model.part_of_speech,
                        "example": None,  # 暂时设置为 None, 后续可以从 words.json 中获取
                    }
                )
        return key_words