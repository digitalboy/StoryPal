# app/services/original_story_service.py
import logging
import re
import threading
import string
import time  # 修复：导入 time 模块
from concurrent.futures import ThreadPoolExecutor, as_completed

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from sqlalchemy import tuple_
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
        新逻辑：此任务会检查所有故事，按level排序。
        - 如果故事未分词，则进行分词和计算。
        - 如果故事已分词，则根据最新的词汇库重新计算生词率和生词列表。
        """
        with self._processing_status["lock"]:
            if self._processing_status["is_running"]:
                self.logger.warning("处理任务已在运行中，请勿重复启动。")
                return  # 或者可以返回一个状态信息

            self._processing_status["is_running"] = True
            self._processing_status["processed"] = 0
            # 预先计算总数
            db = SessionLocal()
            try:
                total_stories = db.query(OriginalStoryModel.id).count()
                self._processing_status["total"] = total_stories
            finally:
                db.close()

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
        pattern = re.compile(r"(.+?)\(([A-Z]+)\)")

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
        story_id: str,  # 接收故事ID
        ai_service_name: str,
        known_words_set: Set[Tuple[str, str]],
    ):
        """
        处理单个故事的完整逻辑，设计为在单个工作线程中运行。
        新逻辑: 每个线程创建和管理自己的数据库会话，并使用 get() 加锁。
        """
        db: Session = SessionLocal()  # 每个线程创建自己的会话
        ai_service = None  # 仅在需要时初始化

        try:
            # 使用 get() 并附带 with_for_update=True 是最高效的获取并加锁的方式
            story = db.get(OriginalStoryModel, story_id, with_for_update=True)

            if not story:
                self.logger.error(f"工作线程无法找到故事 ID: {story_id}")
                return

            start_time = time.time()
            tokenized_content = ""

            # 步骤 1: 获取分词内容
            if story.tokenized_content is not None:
                # 使用已有的分词内容
                self.logger.info(f"故事 ID {story.id} 使用已有分词内容进行重新计算。")
                tokenized_content = story.tokenized_content
            else:
                # 执行AI分词
                self.logger.info(f"故事 ID {story.id} 开始执行AI分词。")
                if not story.content or not story.content.strip():
                    self.logger.warning(f"故事 ID {story.id} 内容为空，跳过处理。")
                    story.tokenized_content = ""
                    story.unknown_word_ratio = 0.0
                    story.unknown_words = []
                    db.commit()  # 提交空内容的处理结果
                    return

                prompt = self._get_prompt(
                    "tokenize_prompt.txt", {"text_content": story.content}
                )
                ai_service = AIServiceFactory.create_ai_service(ai_service_name)
                tokenized_content_from_ai = ai_service.generate_text(prompt)
                tokenized_content = tokenized_content_from_ai.strip()
                story.tokenized_content = tokenized_content

            # 步骤 2: 计算比例
            tokens = self._parse_tokenized_string(tokenized_content)
            word_tokens = [
                t for t in tokens if t[1] is not None and t[0] not in self.punctuation
            ]
            total_word_count = len(word_tokens)
            unknown_word_count = 0
            unknown_words_list = []

            if total_word_count > 0:
                for word, pos in word_tokens:
                    if (word, pos) not in known_words_set:
                        unknown_word_count += 1
                        unknown_words_list.append({"word": word, "pos": pos})
                story.unknown_word_ratio = unknown_word_count / total_word_count
            else:
                story.unknown_word_ratio = 0.0

            # 步骤 3: 更新对象属性
            story.unknown_words = unknown_words_list

            # 步骤 4: 提交事务
            db.commit()

            processing_time = time.time() - start_time
            self.logger.info(
                f"故事 ID {story.id} 处理并提交成功。耗时: {processing_time:.2f}s. 生词率: {story.unknown_word_ratio:.2%}"
            )

        except Exception as e:
            self.logger.error(f"处理故事 ID {story_id} 失败: {e}", exc_info=True)
            db.rollback()  # 发生异常时回滚
            raise  # 重新抛出异常，以便 as_completed 能捕获到
        finally:
            db.close()  # 确保会话在任何情况下都被关闭

    def _process_all_stories_task_manager(
        self, ai_service_name: str, num_workers: int = 2
    ):
        """
        后台任务管理器（生产者），负责分发任务给多个工作线程（消费者）。
        新逻辑: 严格按level升序处理，并引入背压机制。
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

            # 2. 获取故事总数和所有级别
            total_stories = db.query(OriginalStoryModel.id).count()
            distinct_levels_result = (
                db.query(OriginalStoryModel.level)
                .distinct()
                .order_by(OriginalStoryModel.level.asc())
                .all()
            )
            distinct_levels = [level[0] for level in distinct_levels_result]

            self.logger.info(
                f"查询完毕，共找到 {total_stories} 个故事，分布在 {len(distinct_levels)} 个级别中。"
            )

            with self._processing_status["lock"]:
                self._processing_status["total"] = total_stories
                self._processing_status["processed"] = 0

            if total_stories == 0:
                self.logger.info("没有需要处理的故事。")
                return

            # 3. 按级别顺序，逐级处理
            for level in distinct_levels:
                self.logger.info(
                    f"========== 开始处理 Level {level} 的所有故事 =========="
                )

                with ThreadPoolExecutor(max_workers=num_workers) as executor:
                    futures = {}
                    last_id = ""
                    batch_size = 10

                    while True:
                        # 背压机制：如果待处理任务过多，则暂停获取
                        if len(futures) > num_workers * 2:
                            self.logger.debug("待处理任务过多，暂停获取新任务...")
                            time.sleep(1)
                            # 清理已完成的 future
                            done_futures = {f for f in futures if f.done()}
                            for f in done_futures:
                                futures.pop(f)
                            continue

                        # 查询下一批故事的ID
                        query = (
                            db.query(OriginalStoryModel.id)
                            .filter(
                                OriginalStoryModel.level == level,
                                OriginalStoryModel.id > last_id,
                            )
                            .order_by(OriginalStoryModel.id.asc())
                            .limit(batch_size)
                        )

                        batch_ids = [item.id for item in query.all()]

                        if not batch_ids:
                            break

                        # 提交当前批次的任务
                        for story_id in batch_ids:
                            future = executor.submit(
                                self._process_single_story,
                                story_id,
                                ai_service_name,
                                known_words_set,
                            )
                            futures[future] = story_id

                        last_id = batch_ids[-1]
                        self.logger.info(
                            f"Level {level}: 已提交 {len(batch_ids)} 个任务，当前进度游标 id={last_id}"
                        )

                        # 新增：在每次获取批次后都强制休眠，以平滑数据库负载，避免查询风暴。
                        # 这是解决CPU 100%问题的关键应用层优化。
                        time.sleep(0.5)

                    # 等待当前级别的所有任务完成
                    self.logger.info(f"Level {level}: 所有任务已提交，等待处理完成...")
                    for future in as_completed(futures):
                        story_id = futures[future]
                        try:
                            future.result()  # 检查任务是否出现异常
                            with self._processing_status["lock"]:
                                self._processing_status["processed"] += 1
                        except Exception as exc:
                            self.logger.error(
                                f"故事 ID {story_id} (Level {level}) 在执行期间产生未捕获的异常: {exc}",
                                exc_info=True,
                            )

                self.logger.info(
                    f"========== Level {level} 的所有故事处理完成 =========="
                )

            self.logger.info("所有级别的所有故事处理任务已全部完成。")

        except Exception as e:
            self.logger.error(f"后台任务管理器发生严重错误: {e}", exc_info=True)
            db.rollback()
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
