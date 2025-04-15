# app/services/story_service.py
import json
import logging
from typing import List
from jinja2 import Environment, FileSystemLoader
from app.config import Config
from app.models.story_model import StoryModel  
from app.services.word_service import WordService
from app.services.scene_service import SceneService
from app.utils.literacy_calculator import LiteracyCalculator
from app.services.ai_service import AIService  

# import logging
from enum import Enum
from app.utils.json_storage import JSONStorage
import string
from app.services.fetch_story_content import get_story_details  # 引入 get_story_details


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
        self.story_storage = JSONStorage(Config.STORIES_FILE_PATH)  # 新增
        self.logger = logging.getLogger(__name__)  # 初始化 logger
        self.punctuation = set(
            string.punctuation
            + "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰–—‘'‛“”„‟…⋯᠁"
        )

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
            # 使用 AI 服务生成故事
            ai_response = self.ai_service.generate_story(
                prompt="\n".join([message["content"] for message in messages])
            )

            try:
                title = ai_response.get("title")
                content = ai_response.get("content")
                ai_key_words_raw = (
                    ai_response.get("key_words") if ai_response.get("key_words") else []
                )
                
                # 调用 LiteracyCalculator 计算词数、生词率和生词列表
                word_count, new_word_rate, unknown_words_raw = (
                    self.literacy_calculator.calculate_vocabulary_rate(
                        content, vocabulary_level
                    )
                )
                

                story = StoryModel(
                    story_id=None,
                    title=title,
                    content=content,
                    vocabulary_level=vocabulary_level,
                    scene_id=scene_id,
                    scene_name=scene.name,
                    word_count=word_count,
                    new_word_rate=new_word_rate,
                    key_words=ai_key_words_raw,  # 直接使用原始列表
                    unknown_words=unknown_words_raw,  # 直接使用原始列表
                    created_at=None,
                )

                self.story_storage.add(story.to_dict())
                return story

            except (json.JSONDecodeError, TypeError) as e:
                self.logger.error(f"AI 服务返回无效的 JSON 格式: {e}")
                # 不记录故事
                raise Exception(f"AI 服务返回无效的 JSON 格式: {e}")
        except Exception as e:
            self.logger.error(f"AI 服务调用失败: {e}")
            raise Exception(f"AI 服务调用失败: {e}")

    def rewrite_story(
        self,
        original_story_id: str,
        target_level: int,
        story_type: int = 2,  # 默认中文绘本
    ) -> StoryModel | None:  # 更新返回类型提示
        """
        改写现有故事到目标级别。

        Args:
            original_story_id: 原始故事的 ID。
            target_level: 目标词汇级别。
            story_type: 故事类型 (用于获取原始故事)。

        Returns:
            改写成功则返回新的 StoryModel，否则返回 None。
        """
        self.logger.info(
            f"开始改写故事 ID:{original_story_id} 到目标级别:{target_level}"
        )

        # 1. 获取原始故事详情
        original_story_details = get_story_details(original_story_id, story_type)
        if not original_story_details:
            self.logger.error(f"无法获取原始故事详情，ID: {original_story_id}")
            return None

        original_text = original_story_details.get("text")
        original_title = original_story_details.get("storyName")
        original_level = original_story_details.get("storyLevel")
        if not original_text:
            self.logger.error(f"原始故事内容为空，ID: {original_story_id}")
            return None

        self.logger.info(f"成功获取原始故事 '{original_title}' (级别:{original_level})")

        # 2. 准备 Prompt
        known_words_list = self.word_service.get_words_below_level(target_level)
        known_words_sample = [  # 只传递部分示例给 Prompt，避免过长
            {"word": w.word, "part_of_speech": w.part_of_speech}
            for w in known_words_list[:800]  # 最多传递 200 个词作为参考
        ]

        rewrite_prompt_data = {
            "original_story_text": original_text,
            "original_story_level": original_level,
            "target_level": target_level,
            "known_words": json.dumps(known_words_sample, ensure_ascii=False),
        }
        rewrite_prompt = self.get_prompt("rerwrite_prompt.txt", rewrite_prompt_data)

        # 3. 调用 AI 服务进行改写
        try:
            self.logger.debug("正在调用 AI 服务进行故事改写...")
            ai_response = self.ai_service.generate_story(rewrite_prompt)
            if not ai_response:
                self.logger.error("AI 服务返回空响应")
                return None

            # 4. 解析 AI 响应
            title = ai_response.get("title")
            content = ai_response.get("content")
            ai_key_words_raw = ai_response.get("key_words", [])
            scene_data_from_ai = ai_response.get("scene")  # 获取 scene 对象
            ai_target_level = ai_response.get("target_level")

            # 检查 scene_data_from_ai 是否是字典并包含 name 和 description
            if not isinstance(scene_data_from_ai, dict) or not all(
                k in scene_data_from_ai for k in ("name", "description")
            ):
                self.logger.error(
                    f"AI 响应中的 'scene' 字段格式无效或缺少 'name'/'description': {scene_data_from_ai}"
                )
                return None

            scene_name_from_ai = scene_data_from_ai.get("name")
            scene_description_from_ai = scene_data_from_ai.get("description")

            if not all(
                [title, content, scene_name_from_ai, scene_description_from_ai]
            ):  # 确保 description 也存在
                self.logger.error(
                    f"AI 响应缺少必要字段（标题、内容、场景名称或场景描述）: {ai_response}"
                )
                return None

            # 确认 AI 理解的目标级别与请求一致 (可选)
            if ai_target_level != target_level:
                self.logger.warning(
                    f"AI 返回的目标级别 {ai_target_level} 与请求的 {target_level} 不一致，将使用请求的级别。"
                )

            self.logger.info(f"AI 改写成功。标题: {title}, 场景: {scene_name_from_ai}")

            # 5. 词汇分析
            self.logger.debug("正在进行词汇分析...")
            # calculate_vocabulary_rate 返回元组 (word_count, new_word_rate, unknown_words_raw)
            word_count, new_word_rate, unknown_words_raw = (
                self.literacy_calculator.calculate_vocabulary_rate(
                    content, target_level
                )
            )
            # 移除 WordInfo 转换
            # unknown_words = [WordInfo(**uw) for uw in unknown_words_raw]

            self.logger.info(
                f"词汇分析结果: 词数={word_count}, 生词率={new_word_rate:.2%}"
            )

            # 6. 处理场景信息 (查找或创建)
            self.logger.debug(f"查找或创建场景: {scene_name_from_ai}")
            # 调用新的 find_or_create_scene 方法
            scene_model = self.scene_service.find_or_create_scene(
                scene_name_from_ai, scene_description_from_ai
            )
            # find_or_create_scene_by_name 保证会返回一个 SceneModel，无需检查 None

            # 7. 创建并保存 StoryModel
            new_story = StoryModel(
                # id 和 created_at 由 BaseModel 自动处理
                title=title,
                content=content,
                vocabulary_level=target_level,
                scene_id=scene_model.id,
                scene_name=scene_model.name,
                key_words=ai_key_words_raw,  # 直接使用原始列表
                word_count=word_count,  # 直接使用分析结果
                new_word_rate=new_word_rate,  # 直接使用分析结果
                unknown_words=unknown_words_raw,  # 直接使用分析结果
                # original_story_id=original_story_id,
                # original_story_level=original_level,
            )

            self.story_storage.add(new_story.to_dict())
            self.logger.info(f"成功改写并保存故事。")
            return new_story

        except json.JSONDecodeError as e:
            self.logger.exception(f"解析 AI 响应 JSON 失败: {e}")
            return None
        except Exception as e:
            self.logger.exception(f"改写过程中发生错误: {e}")
            return None
