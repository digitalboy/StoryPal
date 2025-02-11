# app/services/deepseek_service.py
import json
import logging
from typing import List, Dict
from openai import OpenAI
from app.config import Config
from app.services.ai_service import AIService


class DeepseekService(AIService):
    """
    Deepseek AI 服务
    """

    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com"
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.logger = logging.getLogger(__name__)

    def generate_story(self, prompt: str) -> Dict:
        """
        使用 Deepseek AI 生成故事
        Args:
            prompt (str): 提示语
        Returns:
            Dict: 包含故事标题、内容和关键词的字典
        """
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},  
            )
            ai_message = response.choices[0].message.content
            return json.loads(ai_message)
        except Exception as e:
            self.logger.error(f"Deepseek AI 服务调用失败: {e}")
            raise Exception(f"Deepseek AI 服务调用失败: {e}")