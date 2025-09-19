# app/services/ai_service.py
from abc import ABC, abstractmethod
from typing import List, Dict


class AIService(ABC):
    """
    AI 服务抽象基类
    """

    @abstractmethod
    def generate_story(
        self,
        prompt: str,
    ) -> Dict:
        """
        生成故事
        Args:
            prompt (str): 提示语
        Returns:
            Dict: 包含故事标题、内容和关键词的字典
        """
        pass

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """
        根据 prompt 生成纯文本
        Args:
            prompt (str): 提示语
        Returns:
            str: AI 生成的文本
        """
        pass
