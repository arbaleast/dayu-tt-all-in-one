#!/usr/bin/env python3
"""
RAG Indexer — 大鱼 TT 知识库
将 docs/ 下的所有 markdown 文档向量化，存入 ChromaDB
"""

import os
import glob
from pathlib import Path
from llama_index.core import Document, VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# ── 配置 ──────────────────────────────────────────────
PROJECT_ROOT = Path("/vol1/1000/projects/3d-printing/dayu-tt-all-in-one")
DB_PATH      = PROJECT_ROOT / ".chromadb"
INDEX_DIR    = PROJECT_ROOT / ".rag_index"

EMBED_MODEL = "nomic-embed-text"
LLM_MODEL   = "llama3.1"

# ── 加载文档 ───────────────────────────────────────────
def load_markdown_docs():
    """递归加载所有 .md 文件（排除 .git / .rag_index）"""
    docs_dir = PROJECT_ROOT / "docs"
    patterns = ["**/*.md", "**/*.txt"]

    documents = []
    for pattern in patterns:
        for fp in docs_dir.glob(pattern):
            # 跳过临时/缓存目录
            if any(p.startswith(".") for p in fp.parts):
                continue
            try:
                text = fp.read_text(encoding="utf-8")
                # 提取相对路径作为 metadata
                rel = fp.relative_to(PROJECT_ROOT)
                doc = Document(
                    text=text,
                    metadata={
                        "source": str(rel),
                        "file_name": fp.name,
                    }
                )
                documents.append(doc)
            except Exception as e:
                print(f"  ⚠ 跳过 {fp}: {e}")

    print(f"✅ 共加载 {len(documents)} 个文档")
    return documents

# ── 构建索引 ───────────────────────────────────────────
def build_index(documents):
    """用 Ollama Embedding + ChromaDB 构建向量索引"""

    # 1. ChromaDB 客户端
    chroma_client = chromadb.PersistentClient(path=str(DB_PATH))

    # 清理旧 collection（可选，取消注释可强制重建）
    try:
        chroma_client.delete_collection("dayu_tt_knowledge")
    except Exception:
        pass

    collection = chroma_client.get_or_create_collection("dayu_tt_knowledge")

    # 2. 向量存储
    vector_store = ChromaVectorStore(chroma_collection=collection)

    # 3. Embedding 模型
    embed_model = OllamaEmbedding(
        model_name=EMBED_MODEL,
        base_url="http://localhost:11434",
    )

    # 4. LLM
    llm = Ollama(
        model=LLM_MODEL,
        base_url="http://localhost:11434",
        request_timeout=120,
    )

    # 5. 构建索引（禁用 streaming 以避免输出问题）
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print(f"🔧 用 {EMBED_MODEL} 向量化 {len(documents)} 个文档...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    # 6. 保存索引
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=str(INDEX_DIR))
    print(f"✅ 索引已保存至 {INDEX_DIR}")

    return index

# ── 主流程 ───────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("大鱼 TT RAG 知识库构建器")
    print("=" * 50)

    documents = load_markdown_docs()
    if not documents:
        print("❌ 没有找到文档，退出")
        exit(1)

    index = build_index(documents)
    print("\n🎉 索引构建完成！")
    print(f"   文档数: {len(documents)}")
    print(f"   索引目录: {INDEX_DIR}")
    print(f"   向量数据库: {DB_PATH}")
