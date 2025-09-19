# app/services/qwen_service.py
import json
import logging
from typing import Dict
from openai import OpenAI
from app.config import Config
from app.services.ai_service import AIService


class QwenService(AIService):
    """
    Qwen (通义千问) AI 服务
    """

    def __init__(self):
        self.api_key = Config.QWEN_API_KEY
        if not self.api_key:
            raise ValueError("Qwen API 密钥不能为空，请在 .env 文件中配置 QWEN_API_KEY")

        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model = "qwen-plus-2025-09-11"
        self.logger = logging.getLogger(__name__)

    def generate_story(self, prompt: str) -> Dict:
        """
        使用 Qwen AI 生成故事
        Args:
            prompt (str): 提示语
        Returns:
            Dict: 包含故事标题、内容和关键词的字典
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                # 根据通义千问文档，非流式调用建议禁用思考过程
                extra_body={"enable_thinking": False},
            )
            ai_message = completion.choices[0].message.content
            if ai_message is None:
                raise Exception("Qwen AI 服务返回了空内容。")
            return json.loads(ai_message)
        except Exception as e:
            self.logger.error(f"Qwen AI 服务调用失败: {e}")
            raise Exception(f"Qwen AI 服务调用失败: {e}")
