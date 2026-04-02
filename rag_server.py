#!/usr/bin/env python3
"""
RAG Query Server — 大鱼 TT 知识库问答
Flask Web UI，基于本地 Ollama LLM + ChromaDB 向量检索
"""

from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import urllib.request, urllib.error, json

# ── 配置 ──────────────────────────────────────────────
PROJECT_ROOT = Path("/vol1/1000/projects/3d-printing/dayu-tt-all-in-one")
DB_PATH      = PROJECT_ROOT / ".chromadb"
INDEX_DIR    = PROJECT_ROOT / ".rag_index"

EMBED_MODEL = "nomic-embed-text"
LLM_MODEL   = "qwen2.5:7b"
PORT        = 5010

# ── Flask App ───────────────────────────────────────────
app = Flask(__name__)

_index      = None
_query_engine = None
_retriever   = None

def get_retriever():
    """懒加载检索引擎"""
    global _index, _retriever
    if _retriever is None:
        print("🔧 正在加载索引...")
        chroma_client = chromadb.PersistentClient(path=str(DB_PATH))
        collection    = chroma_client.get_or_create_collection("dayu_tt_knowledge")
        embed_model   = OllamaEmbedding(model_name=EMBED_MODEL, base_url="http://localhost:11434")
        vector_store  = ChromaVectorStore(chroma_collection=collection)
        storage_ctx   = StorageContext.from_defaults(persist_dir=str(INDEX_DIR), vector_store=vector_store)
        _index        = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_ctx, embed_model=embed_model)
        _retriever    = _index.as_retriever(similarity_top_k=5)
        print("✅ 索引加载完成")
    return _retriever

SYSTEM_PROMPT = """你是一个专业、耐心的大鱼 TT 3D打印机技术助手。
基于给定的知识库内容回答用户问题。
回答要求：
- 优先使用中文
- 引用具体文档来源（metadata.source）
- 如果知识库没有相关信息，坦诚说明，不要编造
- 回答要实用、有操作指导性
- 适当引用文档细节（价格、规格、配置命令等）"""

# ── 路由 ───────────────────────────────────────────────

@app.route("/")
def index():
    HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>🐟 大鱼 TT 知识库问答</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f172a; color: #e2e8f0; min-height: 100vh; }
  .container { max-width: 900px; margin: 0 auto; padding: 2rem 1rem; }
  h1 { font-size: 1.6rem; margin-bottom: .4rem; color: #38bdf8; }
  .subtitle { color: #64748b; font-size: .85rem; margin-bottom: 1.5rem; }
  .chat-box { background: #1e293b; border-radius: 12px; padding: 1.2rem;
              min-height: 420px; max-height: 60vh; overflow-y: auto;
              border: 1px solid #334155; margin-bottom: 1rem; }
  .msg { margin-bottom: 1rem; line-height: 1.7; font-size: .95rem; }
  .msg.user { color: #7dd3fc; font-weight: 600; }
  .msg.assistant { color: #a5f3fc; white-space: pre-wrap; }
  .msg .meta { font-size: .75rem; color: #475569; margin-top: .4rem; }
  .sources { margin-top: .5rem; }
  .src-chip { background: #334155; border-radius: 4px; padding: 2px 8px;
              margin: 2px; display: inline-block; font-size: .75rem; color: #94a3b8; }
  .input-row { display: flex; gap: .5rem; }
  input[type=text] { flex: 1; background: #1e293b; border: 1px solid #334155;
     color: #e2e8f0; border-radius: 8px; padding: .8rem 1rem; font-size: 1rem; outline: none; }
  input[type=text]:focus { border-color: #38bdf8; }
  button { background: #0ea5e9; color: white; border: none; border-radius: 8px;
           padding: .8rem 1.5rem; font-size: 1rem; cursor: pointer; font-weight: 600; }
  button:hover { background: #0284c7; }
  button:disabled { opacity: .5; cursor: not-allowed; }
  .loading { color: #64748b; font-style: italic; }
  .error { color: #f87171; background: #2d1010; border-radius: 6px; padding: .8rem; }
  .chunk { background: #0f172a; border-left: 3px solid #0ea5e9; padding: .6rem 1rem;
           margin: .5rem 0; border-radius: 0 6px 6px 0; font-size: .88rem; color: #cbd5e1; }
  .chunk-text { margin-bottom: .4rem; }
  .chunk-src { font-size: .72rem; color: #475569; }
  .status { font-size: .78rem; color: #475569; margin-bottom: 1rem; }
</style>
</head>
<body>
<div class="container">
  <h1>🐟 大鱼 TT 知识库问答</h1>
  <p class="subtitle">ChromaDB 向量检索 · nomic-embed-text</p>
  <div id="status" class="status">✅ 服务就绪</div>
  <div class="chat-box" id="chatBox"></div>
  <div class="input-row">
    <input type="text" id="question" placeholder="问我关于大鱼 TT 的任何问题..." onkeydown="if(event.key==='Enter')ask()">
    <button id="sendBtn" onclick="ask()">提问</button>
  </div>
</div>
<script>
const chatBox = document.getElementById('chatBox');
const sendBtn = document.getElementById('sendBtn');
const inp = document.getElementById('question');
let history = [];

async function ask() {
  const q = inp.value.trim();
  if (!q) return;
  inp.value = '';
  sendBtn.disabled = true;

  history.push({role:'user', content:q});
  chatBox.innerHTML += `<div class="msg user">问：${esc(q)}</div>`;
  chatBox.innerHTML += `<div class="msg assistant" id="tmp"><span class="loading">🔍 检索中...</span></div>`;
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const r = await fetch('/api/query', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: q})
    });
    const data = await r.json();
    const tmp = document.getElementById('tmp');
    if (data.error) {
      tmp.innerHTML = `<div class="error">❌ ${esc(data.error)}</div>`;
    } else if (data.chunks && data.chunks.length) {
      let html = '<div style="margin-bottom:.5rem;color:#e2e8f0">找到 ' + data.chunks.length + ' 条相关文档：</div>';
      data.chunks.forEach(c => {
        html += `<div class="chunk">
          <div class="chunk-text">${esc(c.text)}</div>
          <div class="chunk-src">📄 ${esc(c.source)}</div>
        </div>`;
      });
      tmp.innerHTML = html;
    } else {
      tmp.innerHTML = '<span style="color:#64748b">未找到相关内容</span>';
    }
    tmp.classList.remove('loading');
  } catch(e) {
    document.getElementById('tmp').innerHTML = `<div class="error">❌ 网络错误：${e.message}</div>`;
  }
  sendBtn.disabled = false;
  inp.focus();
  chatBox.scrollTop = chatBox.scrollHeight;
}

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
</script>
</body>
</html>
"""
    return render_template_string(HTML)


@app.route("/api/query", methods=["POST"])
def api_query():
    data = request.get_json()
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "问题不能为空"})

    try:
        retriever = get_retriever()
        nodes = retriever.retrieve(question)

        # 取 top-5 chunks，每个截断到 800 字
        MAX_CHARS = 800
        chunks = []
        for n in nodes[:5]:
            text   = n.get_text()[:MAX_CHARS]
            meta   = n.metadata or {}
            source = meta.get("source", "未知")
            chunks.append({"text": text, "source": source})

        # 直接返回检索结果（不做 LLM 合成）
        return jsonify({
            "chunks": chunks,
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/health")
def api_health():
    try:
        get_retriever()
        return jsonify({"status": "ok", "model": LLM_MODEL, "embed": EMBED_MODEL})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """直接调 Ollama API 做 LLM 合成（绕过 llama_index 超时问题）"""
    data = request.get_json()
    context   = (data.get("context") or "").strip()
    question  = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "问题不能为空"})

    try:
        system_prompt = (
            "你是一个专业、耐心的大鱼 TT 3D打印机技术助手。 "
            "基于给定的知识库内容回答用户问题。 "
            "回答要求：优先使用中文、引用具体文档来源、 "
            "如果知识库没有相关信息则坦诚说明不要编造、回答要实用有操作性。"
        )
        payload = json.dumps({
            "model": LLM_MODEL,
            "prompt": f"上下文：\n{context}\n\n问题：{question}\n\n请基于上下文回答，要求中文、实用、有操作性。",
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 512}
        }).encode()

        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read())
            answer = result.get("response", "").strip()
            return jsonify({"answer": answer})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": f"LLM 合成失败：{e}"}), 500


if __name__ == "__main__":
    print(f"🚀 大鱼 TT RAG 问答服务")
    print(f"   访问地址: http://localhost:{PORT}")
    print(f"   LLM: {LLM_MODEL}  |  Embedding: {EMBED_MODEL}")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
