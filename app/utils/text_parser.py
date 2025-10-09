import re
from typing import List, Optional, Tuple, Set
import logging

logger = logging.getLogger(__name__)

def parse_tokenized_string(text: str, valid_pos_tags: Set[str]) -> List[Tuple[str, Optional[str]]]:
    """
    解析AI返回的分词字符串，例如 "他(PRON)|走(V)|到(PREP)|。"，
    返回一个 (词, 词性) 的元组列表。
    标点符号的词性为 None。

    Args:
        text (str): AI返回的、以'|'分隔的原始分词字符串。
        valid_pos_tags (Set[str]): 一个包含所有合法大写英文词性标签的集合。

    Returns:
        List[Tuple[str, Optional[str]]]: 一个元组列表，每个元组是 (词, 词性) 或 (标点, None)。
    """
    if not text:
        return []

    # 正则表达式仅用于从 "词(词性)" 结构中提取内容
    pattern = re.compile(r"(.+?)\((.*?)\)")

    tokens = []
    parts = text.split("|")

    for part in parts:
        part = part.strip()
        if not part:
            continue

        match = pattern.fullmatch(part)
        if match:
            word, pos = match.groups()
            word = word.strip()
            pos = pos.strip().upper()
            # 如果AI给出的词性无效，则标记为UNKNOWN
            if pos not in valid_pos_tags:
                logger.warning(
                    f"检测到无效词性 '{pos}' 来自词 '{word}'，已更正为 UNKNOWN。"
                )
                pos = "UNKNOWN"
            tokens.append((word, pos))
        else:
            # 如果正则不匹配，认为它是一个没有词性的词（如标点）
            tokens.append((part, None))

    return tokens