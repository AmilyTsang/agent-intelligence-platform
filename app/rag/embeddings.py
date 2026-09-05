from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings


_embedding_model = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    单例方式加载 Embedding 模型，
    避免每次请求重新加载。
    """

    global _embedding_model

    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={
                "device": "cpu",
            },
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

    return _embedding_model