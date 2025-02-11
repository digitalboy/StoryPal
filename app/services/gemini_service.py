# app/services/gemini_service.py
import google.generativeai as genai
import json
import logging
from typing import List, Dict
from app.config import Config
from app.services.ai_service import AIService


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
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-pro")  #  或者你希望使用的模型
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
            response = self.model.generate_content(prompt)
            ai_message = response.text  #  假设 Gemini API 返回的是文本
            #  需要根据 Gemini API 的实际返回格式进行解析
            try:
                ai_response = json.loads(ai_message)
                return ai_response
            except (json.JSONDecodeError, TypeError) as e:
                self.logger.error(
                    f"Gemini AI 服务返回无效的 JSON 格式: {e}, 返回内容: {ai_message}"
                )
                #  如果 Gemini 不返回 JSON 格式，你需要自己解析
                #  例如，使用正则表达式提取标题、内容和关键词
                #  这部分代码需要根据 Gemini API 的实际情况进行调整
                raise Exception(f"Gemini AI 服务返回无效的 JSON 格式: {e}")

        except Exception as e:
            self.logger.error(f"Gemini AI 服务调用失败: {e}")
            raise Exception(f"Gemini AI 服务调用失败: {e}")
