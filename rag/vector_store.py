import os

import dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import Distance, VectorParams

dotenv.load_dotenv()
# Qdrant 本地持久化路径
QDRANT_PATH = "./data/qdrant_db"
COLLECTION_NAME = "ecommerce_knowledge"
EMBEDDING_DIM = 1024  # text-embedding-v3 实际输出维度

def get_embedding():
    return DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
    )

def get_qdrant_client():
    """获取 Qdrant 本地客户端（文件持久化）"""
    os.makedirs(QDRANT_PATH, exist_ok=True)
    return QdrantClient(path=QDRANT_PATH)

def get_vector_store():
    embedding = get_embedding()
    client = get_qdrant_client()

    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embedding
    )


def get_or_create_vector_store():
    """获取或创建向量库，保证只存在一个 QdrantClient 实例"""
    client = get_qdrant_client()
    embedding = get_embedding()

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE
            )
        )

    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embedding
    )