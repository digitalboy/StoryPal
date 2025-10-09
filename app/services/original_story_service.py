# app/services/original_story_service.py
import logging
import re
import threading
import string
import time  # 修复：导入 time 模块
from collections import Counter
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
from app.utils.text_parser import parse_tokenized_string  # 导入新的解析函数


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

    def start_processing_stories(
        self,
        ai_service_name: str = "qwen",
        start_level: Optional[int] = None,
        end_level: Optional[int] = None,
        force_retokenize: bool = False,
    ):
        """
        在后台线程中启动对所有原始故事的分词和生词率计算。
        新逻辑：此任务会检查所有故事，按level排序。
        - 如果故事未分词，则进行分词和计算。
        - 如果故事已分词，则根据最新的词汇库重新计算生词率和生词列表。
        - 支持按 start_level 和 end_level 筛选要处理的故事。
        - 支持 force_retokenize 参数强制重新分词。
        """
        with self._processing_status["lock"]:
            if self._processing_status["is_running"]:
                self.logger.warning("处理任务已在运行中，请勿重复启动。")
                return  # 或者可以返回一个状态信息

            self._processing_status["is_running"] = True
            self._processing_status["processed"] = 0
            # 预先计算总数 - 现在移到后台任务中，因为它依赖于 level 范围
            self._processing_status["total"] = 0

        self.logger.info("Starting background task for story processing.")
        thread = threading.Thread(
            target=self._process_all_stories_task_manager,
            args=(ai_service_name, start_level, end_level, force_retokenize),
        )
        thread.daemon = True
        thread.start()

    def _get_prompt(self, file_name, data):
        template = self.template_env.get_template(file_name)
        prompt = template.render(data)
        return prompt

    # _parse_tokenized_string 方法已被移除，因为它的功能已移至 app/utils/text_parser.py

    def _process_single_story(
        self,
        story_id: str,  # 接收故事ID
        ai_service_name: str,
        literacy_calculator: LiteracyCalculator,  # 直接接收计算器实例
        force_retokenize: bool,
    ):
        """
        处理单个故事的完整逻辑，设计为在单个工作线程中运行。
        新逻辑: 每个线程创建和管理自己的数据库会话，并使用 get() 加锁。
        生词率计算完全委托给 LiteracyCalculator。
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
            if story.tokenized_content is not None and not force_retokenize:
                self.logger.info(f"故事 ID {story.id} 使用已有分词内容进行重新计算。")
                tokenized_content = story.tokenized_content
            else:
                log_message = (
                    f"故事 ID {story.id} 开始执行AI分词（强制刷新）。"
                    if force_retokenize
                    else f"故事 ID {story.id} 开始执行AI分词。"
                )
                self.logger.info(log_message)

                if not story.content or not story.content.strip():
                    self.logger.warning(f"故事 ID {story.id} 内容为空，跳过处理。")
                    story.tokenized_content = ""
                    story.word_count = 0
                    story.unknown_word_ratio = 0.0
                    story.unknown_words = []
                    db.commit()
                    return

                prompt = self._get_prompt(
                    "tokenize_prompt.txt", {"text_content": story.content}
                )
                ai_service = AIServiceFactory.create_ai_service(ai_service_name)
                tokenized_content_from_ai = ai_service.generate_text(prompt)
                tokenized_content = tokenized_content_from_ai.strip()
                story.tokenized_content = tokenized_content

            # 步骤 2: 使用 LiteracyCalculator 计算所有指标
            if tokenized_content:
                (
                    word_count,
                    unknown_word_ratio,
                    unknown_words,
                ) = literacy_calculator.calculate_vocabulary_rate(
                    tokenized_content,
                    story.level,
                    use_full_dictionary=True,  # <-- 关键修改：为原始故事启用全词库模式
                )
                story.word_count = word_count
                story.unknown_word_ratio = unknown_word_ratio
                story.unknown_words = unknown_words
            else:
                story.word_count = 0
                story.unknown_word_ratio = 0.0
                story.unknown_words = []

            # 步骤 3: 提交事务
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
        self,
        ai_service_name: str,
        start_level: Optional[int] = None,
        end_level: Optional[int] = None,
        force_retokenize: bool = False,
        num_workers: int = 2,
    ):
        """
        后台任务管理器（生产者），负责分发任务给多个工作线程（消费者）。
        新逻辑: 严格按level升序处理，并引入背压机制。
        支持按 start_level 和 end_level 筛选。
        """
        db: Session = SessionLocal()
        try:
            self.logger.info(
                f"后台任务管理器启动。处理范围: start_level={start_level}, end_level={end_level}, force_retokenize={force_retokenize}"
            )

            # 1. 准备共享的只读资源
            self.logger.info("正在初始化生词率计算器...")
            word_service = WordService()
            literacy_calculator = LiteracyCalculator(word_service)
            self.logger.info("生词率计算器初始化完毕。")

            # 2. 根据 level 范围获取故事总数和所有级别
            base_query = db.query(OriginalStoryModel)
            if start_level is not None:
                base_query = base_query.filter(OriginalStoryModel.level >= start_level)
            if end_level is not None:
                base_query = base_query.filter(OriginalStoryModel.level <= end_level)

            total_stories = base_query.count()
            distinct_levels_result = (
                base_query.with_entities(OriginalStoryModel.level)
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
                                literacy_calculator,  # 传递计算器实例
                                force_retokenize,
                            )
                            futures[future] = story_id

                        last_id = batch_ids[-1]
                        self.logger.info(
                            f"Level {level}: 已提交 {len(batch_ids)} 个任务，当前进度游标 id={last_id}"
                        )

                        # 新增：在每次获取批次后都强制休眠，以平滑数据库负载，避免查询风暴。
                        # 这是解决CPU 100%问题的关键应用层优化。
                        time.sleep(0.1)

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

    def get_unknown_words_summary(
        self, start_level: Optional[int] = None, end_level: Optional[int] = None
    ) -> dict:
        """
        统计指定级别范围内所有故事的未知词汇。

        Args:
            start_level (Optional[int]): 起始级别（包含）。
            end_level (Optional[int]): 结束级别（包含）。

        Returns:
            dict: 包含 "total_unknown_words" 和 "word_counts" 的字典。
                  "word_counts" 是一个列表，每个元素包含 "word", "pos", "count"。
        """
        db = SessionLocal()
        try:
            self.logger.info(
                f"开始统计未知词汇，范围: start_level={start_level}, end_level={end_level}"
            )
            query = db.query(OriginalStoryModel.unknown_words).filter(
                OriginalStoryModel.unknown_words.isnot(None)
            )

            if start_level is not None:
                query = query.filter(OriginalStoryModel.level >= start_level)
            if end_level is not None:
                query = query.filter(OriginalStoryModel.level <= end_level)

            # all() 会将所有结果加载到内存中
            results = query.all()

            word_counter = Counter()
            total_unknown_words = 0

            # results 是一个元组列表，例如 [([{'word': 'a', 'pos': 'b'}],), ...]
            for (word_list,) in results:
                if not word_list:
                    continue

                total_unknown_words += len(word_list)
                # 将列表中的字典转换为 (word, pos) 元组，以便 Counter 统计
                word_tuples = [
                    (item.get("word"), item.get("pos")) for item in word_list
                ]
                word_counter.update(word_tuples)

            # 将 Counter 对象转换为更易于JSON序列化的列表格式
            word_counts = [
                {"word": word, "pos": pos, "count": count}
                for (word, pos), count in word_counter.items()
            ]

            # 按数量降序排序
            word_counts.sort(key=lambda x: x["count"], reverse=True)

            summary = {
                "total_unknown_words": total_unknown_words,
                "unique_word_count": len(word_counts),
                "word_counts": word_counts,
            }
            self.logger.info(
                f"未知词汇统计完成。总生词数: {total_unknown_words}, 去重后生词数: {len(word_counts)}"
            )
            return summary

        finally:
            db.close()

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
