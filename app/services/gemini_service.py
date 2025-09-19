# app/services/gemini_service.py
import json
import logging
from typing import Dict
from app.config import Config
from app.services.ai_service import AIService

from google import genai  # 正确的引入方式
from google.genai import types
from httpx import RemoteProtocolError, TimeoutException


class GeminiService(AIService):
    """
    Gemini AI 服务
    """

    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError(
                "Gemini API 密钥不能为空，请在 .env 文件中配置 GEMINI_API_KEY"
            )

        retry_options = types.HttpRetryOptions(
            attempts=3,
            initial_delay=5.0,  # 初始延迟 5 秒
            max_delay=240.0,  # 最大延迟 240 秒
            exp_base=2.0,  # 指数基数
        )

        timeout_milliseconds = 240 * 1000

        http_options = types.HttpOptions(
            timeout=timeout_milliseconds, retry_options=retry_options
        )

        # 使用 genai.Client 初始化 Gemini 客户端
        self.client = genai.Client(api_key=self.api_key, http_options=http_options)

        # 模型选择
        self.model = "gemini-2.5-flash"

        self.logger = logging.getLogger(__name__)

    def generate_story(self, prompt: str) -> Dict:
        """
        使用 Gemini AI 生成故事
        Args:
            prompt (str): 提示语
        Returns:
            Dict: 包含故事标题、内容和关键词的字典
        """
        try:
            # 发送 prompt 给 Gemini 模型
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config={"response_mime_type": "application/json"},
            )
            ai_message = response.text
            print(ai_message)
            try:
                ai_response = json.loads(ai_message)
                return ai_response
            except (json.JSONDecodeError, TypeError) as e:
                self.logger.error(
                    f"Gemini AI 服务返回无效的 JSON 格式: {e}, 返回内容: {ai_message}"
                )
                raise Exception(f"Gemini AI 服务返回无效的 JSON 格式: {e}")

        except RemoteProtocolError as e:
            self.logger.error(
                f"Gemini AI 服务连接在响应前被关闭: {e}。这可能是由于请求过大或服务器端超时。"
            )
            raise Exception(f"Gemini AI service connection was closed prematurely: {e}")
        except TimeoutException as e:
            self.logger.error(f"调用 Gemini AI 服务超时: {e}")
            raise Exception(f"Gemini AI service timed out: {e}")
        except Exception as e:
            self.logger.error(f"Gemini AI 服务调用失败: {e}")
            raise Exception(f"Gemini AI 服务调用失败: {e}")

    def generate_text(self, prompt: str) -> str:
        """
        使用 Gemini AI 生成纯文本
        Args:
            prompt (str): 提示语
        Returns:
            str: AI 生成的文本
        """
        try:
            # 发送 prompt 给 Gemini 模型
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
            )
            ai_message = response.text
            return ai_message
        except Exception as e:
            self.logger.error(f"Gemini AI 服务调用失败 (generate_text): {e}")
            raise Exception(f"Gemini AI 服务调用失败 (generate_text): {e}")
