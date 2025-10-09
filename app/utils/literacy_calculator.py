# app/utils/literacy_calculator.py
import re
from typing import List, Tuple, Set, Dict, Union
from app.services.word_service import WordService
import logging
import string
from app.utils.text_parser import parse_tokenized_string  # 导入新的解析函数


class LiteracyCalculator:
    """
    生词率计算器 (基于词级别和词性)
    """

    def __init__(self, word_service: WordService):
        if not word_service:
            raise ValueError("word_service cannot be None")
        self.word_service = word_service
        self.logger = logging.getLogger(__name__)
        self.punctuation = set(
            string.punctuation
            + "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘㙀〙〚〛〜〝〞〟〰–—‘'‛“”„‟…⋯᠁"
        )
        # 添加词性映射 (英文缩写 -> 中文)
        self.pos_mapping = {
            "N": "名词",
            "PN": "专有名词",
            "V": "动词",
            "ADJ": "形容词",
            "ADV": "副词",
            "NUM": "数词",
            "QTY": "量词",
            "PRON": "代词",
            "PREP": "介词",
            "CONJ": "连词",
            "AUX": "助词",
            "L": "方位词",
            "DET": "限定词",
            "IDIOM": "成语",
            "PHR": "短语",
            "INT": "叹词",
            "UNKNOWN": "未知",  # 新增：未知词性
        }
        # 创建一个反向映射，用于从中文词性查找英文缩写
        self.inverse_pos_mapping = {v: k for k, v in self.pos_mapping.items()}

    def _load_known_words(self, target_level: int) -> Set[Tuple[str, str]]:
        """
        加载 **小于** 目标级别的所有词汇中包含的词和 **英文词性缩写** 组合。
        Args:
            target_level: 目标级别 (整数)。
        Returns:
            一个包含已知词和 **英文词性缩写** 组合的集合 (set)， 使用 (word, pos_abbreviation) tuple。
        Raises:
            ValueError: 如果 words.json 文件中存在词，但是没有词性或词性无法映射。
        """
        known_words: Set[Tuple[str, str]] = set()
        known_word_models = self.word_service.get_words_below_level(target_level)

        for word_model in known_word_models:
            if not word_model.part_of_speech:
                self.logger.warning(
                    f"词 '{word_model.word}' 缺少词性，将视为 'UNKNOWN'。"
                )
                pos_abbreviation = "UNKNOWN"
            else:
                # 将中文词性转换为英文缩写
                pos_abbreviation = self.inverse_pos_mapping.get(
                    word_model.part_of_speech
                )
                if not pos_abbreviation:
                    self.logger.warning(
                        f"无法将词性 '{word_model.part_of_speech}' (来自词 '{word_model.word}') 映射为英文缩写，将视为 'UNKNOWN'。"
                    )
                    pos_abbreviation = "UNKNOWN"

            known_words.add(
                (word_model.word.lower(), pos_abbreviation)
            )  # 存储英文缩写并转为小写

        self.logger.debug(
            f"target_level: {target_level}, loaded known_words count: {len(known_words)}"
        )
        # self.logger.debug(f"Sample known_words: {list(known_words)[:10]}") # 可选：打印样本以供调试
        return known_words

    def calculate_vocabulary_rate(
        self, text: str, target_level: int, use_full_dictionary: bool = False
    ) -> Tuple[int, float, List[Dict[str, Union[str, int, None]]]]:
        """
        计算文本的词数、生词率，并返回生词列表（包含英文词性缩写）。
        此方法经过优化，避免在循环中查询数据库。

        生词定义:
        - 如果 use_full_dictionary=True: 生词是完全不在 `words` 表中的词。
        - 如果 use_full_dictionary=False: 生词是 1. 不在词库中；2. 在词库中但其 'chaotong_level' 大于或等于 'target_level'。

        Args:
            text (str): 待分析的已分词文本。
            target_level (int): 目标级别，仅在 use_full_dictionary=False 时有效。
            use_full_dictionary (bool): 是否使用全词库作为参考系。

        Returns:
            Tuple[int, float, List[Dict]]: (总词数, 生词率, 生词列表)
        """
        known_words_set: Set[Tuple[str, str]] = set()
        higher_level_map: Dict[Tuple[str, str], int] = {}

        if use_full_dictionary:
            # 全词库模式：加载所有词汇作为已知词
            self.logger.debug("使用全词库模式计算生词率。")
            all_word_models = self.word_service.get_words()  # 获取所有词
            for word_model in all_word_models:
                pos_abbr = self.inverse_pos_mapping.get(
                    word_model.part_of_speech, "UNKNOWN"
                )
                known_words_set.add((word_model.word.lower(), pos_abbr))
        else:
            # 级别相关模式：按 target_level 加载词汇
            self.logger.debug(
                f"使用级别相关模式计算生词率，target_level={target_level}。"
            )
            # 已知词 (level < target_level)
            known_words_set = self._load_known_words(target_level)
            # 高级别词 (level >= target_level)，用于查找生词的级别
            higher_level_words = self.word_service.get_words_at_or_above_level(
                target_level
            )
            for word_model in higher_level_words:
                pos_abbr = self.inverse_pos_mapping.get(word_model.part_of_speech)
                if pos_abbr:
                    higher_level_map[(word_model.word.lower(), pos_abbr)] = (
                        word_model.chaotong_level
                    )

        # 2. 解析文本 (使用新的、统一的解析器)
        valid_pos_tags = set(self.pos_mapping.keys())
        tokens = parse_tokenized_string(text, valid_pos_tags)

        word_count = 0
        unknown_words_list: List[Dict[str, Union[str, int, None]]] = []
        processed_unknowns = set()  # 用于对生词进行去重

        # 3. 遍历文本中的词
        for word, pos in tokens:
            # 词性为 None 的是标点符号，直接跳过
            if pos is None:
                continue

            # 统一将词语转为小写处理，以匹配 known_words_set
            word_lower = word.strip().lower()
            if not word_lower:
                continue

            word_count += 1
            word_tuple = (word_lower, pos)  # 使用小写词和原始词性(已大写)

            # 如果不是已知词，则为生词
            if word_tuple not in known_words_set:
                if word_tuple not in processed_unknowns:
                    # 查找该生词的级别
                    # 在全词库模式下，生词的级别总是 None
                    # 在级别相关模式下，才需要去 higher_level_map 中查找
                    word_level = (
                        None
                        if use_full_dictionary
                        else higher_level_map.get(word_tuple)
                    )
                    # 返回的生词使用原始的大小写，而不是小写版本
                    unknown_words_list.append(
                        {"word": word.strip(), "pos": pos, "level": word_level}
                    )
                    processed_unknowns.add(word_tuple)

        unknown_word_count = len(unknown_words_list)
        new_word_rate = unknown_word_count / word_count if word_count else 0.0
        self.logger.debug(
            f"text: {text}, target_level: {target_level}, word_count: {word_count}, new_word_rate: {new_word_rate}, unknown_words: {unknown_words_list}"
        )
        return word_count, new_word_rate, unknown_words_list
