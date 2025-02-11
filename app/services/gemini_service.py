# app/services/gemini_service.py
import json
import logging
from typing import List, Dict
from app.config import Config
from app.services.ai_service import AIService
import os
from google import genai  # 正确的引入方式


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


        # 使用 genai.Client 初始化 Gemini 客户端
        self.client = genai.Client(api_key=self.api_key)

        # 模型选择
        self.model = "gemini-2.0-flash"  

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

        except Exception as e:
            self.logger.error(f"Gemini AI 服务调用失败: {e}")
            raise Exception(f"Gemini AI 服务调用失败: {e}")
