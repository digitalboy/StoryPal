# app/services/original_story_service.py
import logging
import re
import threading
import string
from concurrent.futures import ThreadPoolExecutor, as_completed

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.original_story_model import OriginalStoryModel
from app.services.ai_service_factory import AIServiceFactory
from app.services.word_service import WordService
from typing import List, Optional, Set, Tuple
from app.utils.literacy_calculator import LiteracyCalculator


class OriginalStoryService:
    """
    旧有故事服务，提供与数据库交互的旧有故事相关业务逻辑。
    """

    # 用于跟踪后台任务状态的类属性
    _processing_status = {
        "is_running": False,
        "total": 0,
        "processed": 0,
        "lock": threading.Lock(),
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("OriginalStoryService initialized to work with the database.")
        self.template_env = Environment(loader=FileSystemLoader("app/prompts"))
        # 定义一个包含中英文标点符号的集合，用于在计算生词率时进行过滤
        self.punctuation = set(
            string.punctuation
            + "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰–—‘'‛“”„‟…⋯᠁"
        )

    def get_story_by_id(self, story_id: str) -> Optional[OriginalStoryModel]:
        """
        根据ID从数据库获取旧有故事。
        """
        db = SessionLocal()
        try:
            return (
                db.query(OriginalStoryModel)
                .filter(OriginalStoryModel.id == story_id)
                .first()
            )
        finally:
            db.close()

    def start_processing_stories(self, ai_service_name: str = "gemini"):
        """
        在后台线程中启动对所有原始故事的分词和生词率计算。
        """
        with self._processing_status["lock"]:
            if self._processing_status["is_running"]:
                self.logger.warning("处理任务已在运行中，请勿重复启动。")
                return  # 或者可以返回一个状态信息

            self._processing_status["is_running"] = True
            self._processing_status["processed"] = 0
            self._processing_status["total"] = 0

        self.logger.info("Starting background task for story processing.")
        thread = threading.Thread(
            target=self._process_all_stories_task_manager, args=(ai_service_name,)
        )
        thread.daemon = True
        thread.start()

    def _get_prompt(self, file_name, data):
        template = self.template_env.get_template(file_name)
        prompt = template.render(data)
        return prompt

    def _parse_tokenized_string(self, text: str) -> List[Tuple[str, Optional[str]]]:
        """
        解析AI返回的分词字符串，例如 "他(PRON)|走(V)|到(PREP)|。"，
        返回一个 (词, 词性) 的元组列表。
        标点符号的词性为 None。
        """
        if not text:
            return []

        # 正则表达式匹配 "词(词性)"
        pattern = re.compile(r"(.+)\(([A-Z]+)\)")

        tokens = []
        parts = text.split("|")
        for part in parts:
            part = part.strip()
            if not part:
                continue

            match = pattern.fullmatch(part)
            if match:
                word, pos = match.groups()
                tokens.append((word.strip(), pos.strip()))
            else:
                # 如果正则不匹配，认为它是一个没有词性的词（如标点）
                tokens.append((part, None))

        return tokens

    def _process_single_story(
        self,
        story_id: str,
        ai_service_name: str,
        known_words_set: Set[Tuple[str, str]],
    ):
        """
        处理单个故事的完整逻辑，设计为在单个工作线程中运行。
        """
        import time

        # 每个工作线程创建自己的数据库会话和AI服务实例
        db: Session = SessionLocal()
        ai_service = AIServiceFactory.create_ai_service(ai_service_name)

        try:
            story = (
                db.query(OriginalStoryModel)
                .with_for_update()  # 添加行锁，防止并发问题
                .filter(OriginalStoryModel.id == story_id)
                .first()
            )
            if not story:
                self.logger.error(f"工作线程无法找到故事 ID: {story_id}")
                return

            # 再次检查是否已被其他线程处理
            if story.tokenized_content is not None:
                self.logger.info(f"故事 ID {story_id} 已被其他线程处理，跳过。")
                return

            start_time = time.time()
            # 步骤 1: 提取内容并生成 Prompt
            if not story.content or not story.content.strip():
                self.logger.warning(f"故事 ID {story.id} 内容为空，跳过处理。")
                story.tokenized_content = ""
                story.unknown_word_ratio = 0.0
                db.commit()
                return

            prompt = self._get_prompt(
                "tokenize_prompt.txt", {"text_content": story.content}
            )

            # 步骤 2: 调用 AI 分词
            tokenized_content = ai_service.generate_text(prompt)
            story.tokenized_content = tokenized_content.strip()

            # 步骤 3: 计算比例
            tokens = self._parse_tokenized_string(story.tokenized_content)
            word_tokens = [
                t for t in tokens if t[1] is not None and t[0] not in self.punctuation
            ]
            total_word_count = len(word_tokens)
            unknown_word_count = 0

            if total_word_count > 0:
                for word, pos in word_tokens:
                    if (word, pos) not in known_words_set:
                        unknown_word_count += 1
                story.unknown_word_ratio = unknown_word_count / total_word_count
            else:
                story.unknown_word_ratio = 0.0

            # 步骤 4: 更新数据库
            db.commit()
            processing_time = time.time() - start_time
            self.logger.info(
                f"故事 ID {story.id} 处理完成。耗时: {processing_time:.2f}s. 生词率: {story.unknown_word_ratio:.2%}"
            )

        except Exception as e:
            self.logger.error(f"处理故事 ID {story_id} 失败: {e}", exc_info=True)
            db.rollback()
        finally:
            # 更新处理进度
            with self._processing_status["lock"]:
                self._processing_status["processed"] += 1
            db.close()

    def _process_all_stories_task_manager(
        self, ai_service_name: str, num_workers: int = 2
    ):
        """
        后台任务管理器（生产者），负责分发任务给多个工作线程（消费者）。
        """
        db: Session = SessionLocal()
        try:
            self.logger.info("后台任务管理器启动。")

            # 1. 准备共享的只读资源
            self.logger.info("正在加载已知词汇库...")
            word_service = WordService()
            literacy_calculator = LiteracyCalculator(word_service)
            all_words_chinese_pos = word_service.get_all_words_as_set()
            known_words_set: Set[Tuple[str, str]] = set()
            for word, chinese_pos in all_words_chinese_pos:
                pos_abbr = literacy_calculator.inverse_pos_mapping.get(chinese_pos)
                if pos_abbr:
                    known_words_set.add((word, pos_abbr))
            self.logger.info(f"已知词汇库加载完毕，共 {len(known_words_set)} 个词。")

            # 2. 获取所有待处理的故事ID列表 (非常轻量)
            self.logger.info("正在从数据库查询故事统计信息...")
            total_story_count = db.query(OriginalStoryModel.id).count()
            tokenized_story_count = (
                db.query(OriginalStoryModel.id)
                .filter(OriginalStoryModel.tokenized_content.isnot(None))
                .count()
            )

            if total_story_count > 0:
                tokenized_percentage = (
                    tokenized_story_count / total_story_count
                ) * 100
                self.logger.info(
                    f"故事总数: {total_story_count}, 已分词: {tokenized_story_count} ({tokenized_percentage:.2f}%)"
                )
            else:
                self.logger.info("数据库中没有故事。")

            self.logger.info("正在从数据库查询待处理的故事ID...")
            story_ids_to_process = (
                db.query(OriginalStoryModel.id)
                .filter(OriginalStoryModel.tokenized_content.is_(None))
                .all()
            )
            story_ids = [item[0] for item in story_ids_to_process]
            total_stories = len(story_ids)
            self.logger.info(f"查询完毕，共找到 {total_stories} 个待处理的故事。")

            with self._processing_status["lock"]:
                self._processing_status["total"] = total_stories

            if total_stories == 0:
                self.logger.info("没有需要处理的故事。")
                return

            # 3. 使用线程池并发处理
            self.logger.info(f"使用 {num_workers} 个工作线程开始并发处理...")
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                # 为每个故事ID提交一个任务
                futures = {
                    executor.submit(
                        self._process_single_story,
                        story_id,
                        ai_service_name,
                        known_words_set,
                    ): story_id
                    for story_id in story_ids
                }

                for future in as_completed(futures):
                    story_id = futures[future]
                    try:
                        future.result()  # 检查任务是否出现异常
                        processed_count = self._processing_status["processed"]
                        self.logger.info(f"进度: {processed_count}/{total_stories}")
                    except Exception as exc:
                        self.logger.error(
                            f"工作线程处理故事ID {story_id} 时产生了一个未捕获的异常: {exc}",
                            exc_info=True,
                        )

            self.logger.info("所有故事处理任务已完成。")

        except Exception as e:
            self.logger.error(f"后台任务管理器发生严重错误: {e}", exc_info=True)
        finally:
            with self._processing_status["lock"]:
                self._processing_status["is_running"] = False
            db.close()
            self.logger.info("后台任务管理器的数据库会话已关闭。")

    def get_stories_by_level(
        self,
        level: int,
        page: int = 1,
        page_size: int = 10,
    ) -> List[OriginalStoryModel]:
        """
        根据级别从数据库获取旧有故事列表，支持分页。
        """
        db = SessionLocal()
        try:
            query = db.query(OriginalStoryModel).filter(
                OriginalStoryModel.level == level
            )
            return (
                query.order_by(OriginalStoryModel.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
        finally:
            db.close()

    def get_total_stories_by_level(self, level: int) -> int:
        """
        根据级别获取旧有故事总数。
        """
        db = SessionLocal()
        try:
            return (
                db.query(OriginalStoryModel)
                .filter(OriginalStoryModel.level == level)
                .count()
            )
        finally:
            db.close()
