from langchain_core.tools import tool
from rag.retriever import retrieve_knowledge

@tool
def search_knowledge_base(query: str) -> str:
    """
    检索外贸知识库，获取产品材质、尺寸、认证标准、外贸术语解释、售后政策等信息。
    输入参数：query (字符串)，用自然语言描述要查询的内容。
    """
    return retrieve_knowledge(query)