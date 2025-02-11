# app/services/ai_service_factory.py
from app.services.ai_service import AIService
from app.services.deepseek_service import DeepseekService
from app.services.gemini_service import GeminiService


class AIServiceFactory:
    """
    AI 服务工厂类
    """

    @staticmethod
    def create_ai_service(ai_service_name: str) -> AIService:
        """
        创建 AI 服务对象
        Args:
            ai_service_name (str): AI 服务名称 (例如 deepseek, gemini)
        Returns:
            AIService: AI 服务对象
        Raises:
            ValueError: 如果 AI 服务名称无效
        """
        if ai_service_name == "deepseek":
            return DeepseekService()
        elif ai_service_name == "gemini":
            return GeminiService()
        else:
            raise ValueError(f"无效的 AI 服务名称: {ai_service_name}")
