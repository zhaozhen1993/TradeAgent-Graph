import os
import sys

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_docling.loader import DoclingLoader
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector_store import (
    get_embedding,
    get_qdrant_client,
    COLLECTION_NAME,
    QDRANT_PATH,
    EMBEDDING_DIM
)

def load_documents(directory: str):
    """遍历 data 目录，加载支持的文件"""
    all_docs = []
    supported_extensions = (".pdf", ".docx", ".pptx", ".txt")

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(supported_extensions):
            print(f"  📂 加载文件：{filename}")
            loader = DoclingLoader(file_path)
            all_docs.extend(loader.load())
    return all_docs


def ingest_data():
    print("🚀 开始导入外贸知识库（Qdrant 本地模式）...")

    # 1. 加载文档
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    data_dir = os.path.normpath(data_dir)

    if not os.path.exists(data_dir):
        print(f"❌ 数据目录 {data_dir} 不存在")
        return

    docs = load_documents(data_dir)
    if not docs:
        print("⚠️ 未找到任何可导入的文档")
        return
    print(f"📄 成功加载 {len(docs)} 个原始文档")

    # 2. 文本分块
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
    )
    split_docs = text_splitter.split_documents(docs)
    print(f"✂️  文档切分为 {len(split_docs)} 个知识片段")

    # 3. 初始化 Qdrant 客户端，重建 Collection
    client = get_qdrant_client()

    # 如果已存在旧 Collection，先删除（重建索引时用）
    if client.collection_exists(COLLECTION_NAME):
        print(f"🗑️  删除旧的 Collection: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)

    # 创建新的 Collection（指定向量维度和距离算法）
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_DIM,
            distance=Distance.COSINE  # 余弦相似度，适合文本语义检索
        )
    )
    print(f"✅ 创建 Collection: {COLLECTION_NAME}（维度={EMBEDDING_DIM}，距离=Cosine）")

    # 4. 向量化并写入 Qdrant — 直接用已有的 client，不重复创建
    print("🧠 正在生成向量并写入 Qdrant...")

    embedding = get_embedding()
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embedding
    )
    vector_store.add_documents(split_docs)
    print(f"✅ 知识库导入完成！数据保存在 {QDRANT_PATH}")


if __name__ == "__main__":
    ingest_data()
