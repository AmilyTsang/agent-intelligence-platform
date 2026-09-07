from functools import lru_cache

from app.rag.vector_store import load_vector_store


@lru_cache(maxsize=1)
def get_vector_store():
    """
    获取全局复用的 FAISS Vector Store。

    第一次调用：
        load_vector_store()
        ↓
        加载 Embedding Model
        ↓
        加载 FAISS Index

    后续调用：
        直接返回内存中的 Vector Store

    这样可以避免：

        company_search(OpenAI)
        ↓
        load vector store

        company_search(Google)
        ↓
        再次 load vector store

        Retry
        ↓
        又再次 load vector store

    注意：
        如果重新执行 ingest 并更新了本地 FAISS，
        当前 Python 进程不会自动重新读取。

        开发阶段最简单的处理方式是：
        重新启动 Python 进程。
    """

    print(
        "\n[Vector Store Cache] "
        "Initializing vector store..."
    )

    vector_store = load_vector_store()

    print(
        "[Vector Store Cache] "
        "Vector store ready."
    )

    return vector_store


def clear_vector_store_cache():
    """
    手动清空 Vector Store Cache。

    一般只用于：

        - 测试
        - 重新 ingest 后
        - 调试缓存行为

    正常 Agent Research 不需要调用。
    """

    get_vector_store.cache_clear()

    print(
        "\n[Vector Store Cache] "
        "Cache cleared."
    )