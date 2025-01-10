import logging
import os
from dotenv import load_dotenv

load_dotenv()

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", False) == "True" else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s",
)

logging.info("logging is configured")
logging.debug("debug level log")
