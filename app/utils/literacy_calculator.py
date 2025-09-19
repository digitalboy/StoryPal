# app/utils/literacy_calculator.py
import re
from typing import List, Tuple, Set, Dict, Union
from app.services.word_service import WordService
import logging
import string


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
            "V": "动词",
            "ADJ": "形容词",
            "ADV": "副词",
            "NUM": "数字",
            "QTY": "量词",
            "PRON": "代词",
            "AUX": "助词",
            "CONJ": "连词",
            "PHR": "短语",
            "INT": "叹词",
            "PN": "专有名词",
            "IDIOM": "成语",
            "PREP": "介词",
            "L": "方位词",  # 新增：方位词 (Localizer)
            "UNKNOWN": "UNKNOWN",  # 保持 UNKNOWN 不变
        }
        # 添加反向词性映射 (中文 -> 英文缩写)
        self.inverse_pos_mapping = {v: k for k, v in self.pos_mapping.items()}
        self.inverse_pos_mapping["特殊名词"] = (
            "PN"  # 将“特殊名词”映射到“专有名词”的缩写
        )

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
                self.logger.error(f"word {word_model.word} 不存在词性")
                raise ValueError(f"词 {word_model.word} 缺少词性，请检查数据库")
            # 将中文词性转换为英文缩写
            pos_abbreviation = self.inverse_pos_mapping.get(word_model.part_of_speech)
            if not pos_abbreviation:
                self.logger.error(
                    f"无法将词性 '{word_model.part_of_speech}' (来自词 '{word_model.word}') 映射为英文缩写。"
                )
                # 可以选择抛出错误或记录并跳过
                # raise ValueError(f"无法映射词性: {word_model.part_of_speech}")
                continue  # 跳过无法映射的词性

            known_words.add((word_model.word, pos_abbreviation))  # 存储英文缩写

        self.logger.debug(
            f"target_level: {target_level}, loaded known_words count: {len(known_words)}"
        )
        # self.logger.debug(f"Sample known_words: {list(known_words)[:10]}") # 可选：打印样本以供调试
        return known_words

    def calculate_vocabulary_rate(
        self, text: str, target_level: int
    ) -> Tuple[int, float, List[Dict[str, Union[str, int, None]]]]:
        """
        计算文本的词数、生词率，并返回生词列表（包含英文词性缩写）。
        此方法经过优化，避免在循环中查询数据库。
        生词定义为：1. 不在词库中；2. 在词库中但其 'chaotong_level' 大于或等于 'target_level'。
        """
        # 1. 高效加载词汇数据
        # 已知词 (level < target_level)
        known_words_set = self._load_known_words(target_level)

        # 高级别词 (level >= target_level)，用于查找生词的级别
        higher_level_words = self.word_service.get_words_at_or_above_level(target_level)
        higher_level_map: Dict[Tuple[str, str], int] = {}
        for word_model in higher_level_words:
            pos_abbr = self.inverse_pos_mapping.get(word_model.part_of_speech)
            if pos_abbr:
                higher_level_map[(word_model.word.lower(), pos_abbr)] = (
                    word_model.chaotong_level
                )

        # 2. 解析文本
        tokens = re.findall(r"([\w]+)\(([A-Z]+)\)|([^\w\s])", text, re.UNICODE)
        word_count = 0
        unknown_words_list: List[Dict[str, Union[str, int, None]]] = []
        processed_unknowns = set()  # 用于对生词进行去重

        # 3. 遍历文本中的词
        for token in tokens:
            word, pos, symbol = token
            if symbol and symbol in self.punctuation:
                continue

            if word and pos:
                word = word.strip().lower()
                pos = pos.strip().upper()
                if not word or not pos:
                    continue

                word_count += 1
                word_tuple = (word, pos)

                # 如果不是已知词，则为生词
                if word_tuple not in known_words_set:
                    if word_tuple not in processed_unknowns:
                        # 查找该生词的级别
                        word_level = higher_level_map.get(word_tuple)
                        unknown_words_list.append(
                            {"word": word, "pos": pos, "level": word_level}
                        )
                        processed_unknowns.add(word_tuple)

        unknown_word_count = len(unknown_words_list)
        new_word_rate = unknown_word_count / word_count if word_count else 0.0
        self.logger.debug(
            f"text: {text}, target_level: {target_level}, word_count: {word_count}, new_word_rate: {new_word_rate}, unknown_words: {unknown_words_list}"
        )
        return word_count, new_word_rate, unknown_words_list
