# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件


class Config:
    # 获取 API Key
    API_KEY = os.getenv("API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    # 如果是开发环境，可以设置 DEBUG = True
    DEBUG = os.getenv("DEBUG", False) == "True"
    # 配置其他
    # 生字率容差值
    NEW_WORD_RATE_TOLERANCE = float(os.getenv("NEW_WORD_RATE_TOLERANCE", 0.1))
    # 字数容差值
    WORD_COUNT_TOLERANCE = float(os.getenv("WORD_COUNT_TOLERANCE", 0.2))
    # API 请求频率限制
    REQUEST_LIMIT = int(os.getenv("REQUEST_LIMIT", 100))

    # 故事字数容差值
    STORY_WORD_COUNT_TOLERANCE = int(os.getenv("STORY_WORD_COUNT_TOLERANCE", 20))
    # 获取当前文件(config.py)的绝对路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 加载词汇数据的路径
    WORDS_FILE_PATH = os.path.join(
        BASE_DIR, "..", os.getenv("WORDS_FILE_PATH", "app/data/words.json")
    )
    SCENES_FILE_PATH = os.path.join(
        BASE_DIR, "..", os.getenv("SCENES_FILE_PATH", "app/data/scenes.json")
    )

    STORIES_FILE_PATH = os.path.join(  # 添加
        BASE_DIR,
        "..",
        os.getenv("STORIES_FILE_PATH", "app/data/stories.json"),  # 添加
    )  # 添加


def get_api_key_from_config():
    return Config.API_KEY
