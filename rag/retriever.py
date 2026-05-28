from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

from .vector_store import get_vector_store


# 混合检索权重（两者相加=1.0）
VECTOR_WEIGHT = 0.7   # 语义向量检索权重
BM25_WEIGHT = 0.3     # BM25 关键词检索权重
TOP_K = 5             # 每路检索返回文档数



def build_hybrid_retriever(docs=None,k:int=TOP_K):
    """
    构建混合检索器（向量 + BM25）

    :param docs: 用于初始化 BM25 的文档列表（需要从 Qdrant 预加载）
    :param k: 最终返回文档数
    :return: EnsembleRetriever 混合检索器
    """
    vector_store = get_vector_store()
    vector_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

    if docs is None:
        docs = _load_all_docs_from_qdrant(vector_store)

    bm25_retriever = BM25Retriever.from_documents(docs, k=k)

    # 融合：加权 EnsembleRetriever ---
    ensemble_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[VECTOR_WEIGHT, BM25_WEIGHT]
    )

    return ensemble_retriever


def _load_all_docs_from_qdrant(vector_store):
    """
    从 Qdrant 中滚动读取所有文档，用于初始化 BM25
    （BM25 是内存检索，需要提前加载全部语料）
    """
    client = vector_store.client
    collection_name = vector_store.collection_name

    all_docs = []
    offset = None

    while True:
        results, next_offset = client.scroll(
            collection_name=collection_name,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False  # BM25 不需要向量
        )

        if not results:
            break

        from langchain_core.documents import Document
        for point in results:
            payload = point.payload or {}
            page_content = payload.get("page_content", "")
            metadata = payload.get("metadata", {})
            if page_content:
                all_docs.append(Document(page_content=page_content, metadata=metadata))

        if next_offset is None:
            break
        offset = next_offset

    print(f"📚 BM25 加载了 {len(all_docs)} 个文档片段")
    return all_docs


def retrieve_knowledge(query: str, k: int = TOP_K) -> str:
    """
    混合检索入口函数（供各 Agent 调用）

    :param query: 用户查询
    :param k: 返回文档数
    :return: 拼接后的上下文字符串
    """
    try:
        retriever = build_hybrid_retriever(k=k)
        docs = retriever.invoke(query)

        if not docs:
            return "未找到相关的外贸知识库信息。"

        # 去重（向量和 BM25 可能返回重复文档）
        seen = set()
        unique_docs = []
        for doc in docs:
            content_hash = hash(doc.page_content)
            if content_hash not in seen:
                seen.add(content_hash)
                unique_docs.append(doc)

        context = "\n\n".join([
            f"【参考资料 {i + 1}】\n{doc.page_content}"
            for i, doc in enumerate(unique_docs)
        ])
        return context

    except Exception as e:
        print(f"知识库检索出错: {e}")
        return "知识库系统暂时不可用。"

