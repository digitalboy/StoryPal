# app/utils/literacy_calculator.py
import re
from typing import List, Tuple, Set, Dict, Union
import logging
import string


class LiteracyCalculator:
    """
    生词率计算器 (基于词级别和词性)
    """

    def __init__(self, word_service):
        if not word_service:
            raise ValueError("word_service cannot be None")
        self.word_service = word_service
        self.logger = logging.getLogger(__name__)
        self.punctuation = set(
            string.punctuation
            + "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘㙀〙〚〛〜〝〞〟〰–—‘'‛“”„‟…⋯᠁"
        )
        # 建立中英文词性映射关系
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
            "UNKNOWN": "UNKNOWN",  #  保持 UNKNOWN 不变
        }

    def _load_known_words(self, target_level: int) -> Set[Tuple[str, str]]:
        """
        加载 **小于** 目标级别的所有词汇中包含的词和词性组合。  **(已更正为 < target_level)**
        Args:
            target_level: 目标级别 (整数)。
        Returns:
            一个包含已知词和词性组合的集合 (set)， 使用 (word, part_of_speech) tuple。
        Raises:
            ValueError: 如果 words.json 文件中存在词，但是没有词性。
        """
        known_words: Set[Tuple[str, str]] = set()
        if not self.word_service.words:
            return known_words

        for word_model in self.word_service.words.values():
            if (
                word_model.chaotong_level is not None  # 增加判断
                and isinstance(word_model.chaotong_level, int)  # 增加判断
                and word_model.chaotong_level < target_level
            ):  # **已改回 < target_level**
                if not word_model.part_of_speech:
                    self.logger.error(f"word {word_model.word} 不存在词性")
                    raise ValueError(
                        f"词 {word_model.word} 缺少词性，请检查 words.json 文件"
                    )
                known_words.add((word_model.word, word_model.part_of_speech))
        self.logger.debug(f"target_level: {target_level}, known_words: {known_words}")
        return known_words

    def calculate_vocabulary_rate(
        self, text: str, target_level: int
    ) -> Tuple[int, float, List[Dict[str, Union[str, int, None]]]]:  # 修改返回类型
        """
        计算文本的词数、生词率，并返回生词列表。
        """
        # 使用正则表达式分词， 匹配中文词语和英文单词， 并提取词性和词语
        tokens = re.findall(r"([\w]+)\(([A-Z]+)\)|([^\w\s])", text, re.UNICODE)
        word_count = 0
        unknown_words: List[Dict[str, Union[str, int, None]]] = []  # 修改类型
        known_words = self._load_known_words(target_level)
        unknown_word_count = 0

        for token in tokens:
            # token 结构为 (word, pos, symbol), 每次只match 一种，另外两种为 ""
            word, pos, symbol = token
            # 如果是标点符号， 直接跳过
            if symbol and symbol in self.punctuation:
                continue

            # 如果是词语， 则进行后续处理
            if word and pos:
                word = word.strip().lower()
                pos = pos.strip().upper()
                # 确保词语和词性不为空
                if not word or not pos:
                    self.logger.warning(f"无效的词语或词性: {token}")
                    continue
                word_count += 1
                if (word, pos) not in known_words:
                    # 获取词汇信息
                    word_model = next(
                        (
                            wm
                            for wm in self.word_service.words.values()
                            if wm.word.lower() == word
                        ),
                        None,
                    )

                    if word_model:
                        chaotong_level = word_model.chaotong_level
                    else:
                        chaotong_level = None

                    # 只添加大于等于 target_level 的词汇， 或者 words.json 中不存在的词汇
                    if (
                        chaotong_level is not None and chaotong_level >= target_level
                    ) or chaotong_level is None:
                        # 去重机制
                        if not any(
                            d["word"] == word and d["pos"] == pos for d in unknown_words
                        ):
                            unknown_words.append(
                                {"word": word, "pos": pos, "level": chaotong_level}
                            )  # 修改生词列表格式
                            unknown_word_count += 1
                else:
                    self.logger.debug(f"已知词：{word}, 词性: {pos}")

        new_word_rate = unknown_word_count / word_count if word_count else 0.0
        self.logger.debug(
            f"text: {text}, target_level: {target_level}, word_count: {word_count}, new_word_rate: {new_word_rate}, unknown_words: {unknown_words}"
        )
        return word_count, new_word_rate, unknown_words
