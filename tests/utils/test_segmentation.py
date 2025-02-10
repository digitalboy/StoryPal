# tests\utils\test_segmentation.py
import logging
from app.services.word_service import WordService  # 修改
from app.utils.literacy_calculator import LiteracyCalculator  # 修改
from app.config import Config  # 修改
from app.models.word_model import WordModel  # 修改


# 配置日志
logging.basicConfig(level=logging.DEBUG)

# 测试文本
TEST_TEXT = '小明想去一个新地方，但他不知道怎么走。他看到一位路人，就问："您好，请问去学校怎么走？" 路人说："你先直走，到了前面路口再向左转。" 小明说："谢谢！" 然后他按照路人的指引走路，很快就到了学校。'
TARGET_LEVEL = 58


def main():
    # 1. 初始化 WordService
    word_service = WordService()

    # 2. 初始化 LiteracyCalculator
    literacy_calculator = LiteracyCalculator(word_service)

    # 3. 进行分词
    tokens = literacy_calculator._tokenize(TEST_TEXT)

    # 4. 打印分词结果
    print("分词结果:")
    for word, pos in tokens:
        print(f"词: {word}, 词性: {pos}")

    # 5. 计算生词率 (可选)
    known_rate, unknown_rate, message = literacy_calculator.calculate_vocabulary_rate(
        TEST_TEXT, TARGET_LEVEL
    )
    print(f"已知词率: {known_rate}")
    print(f"生词率: {unknown_rate}")
    print(f"消息: {message}")


if __name__ == "__main__":
    main()
