from langchain_openai import ChatOpenAI

from app.config import settings


def get_llm(
    temperature: float = 0.1,
) -> ChatOpenAI:
    """
    返回统一配置的 LLM 实例。
    """

    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=temperature,
    )