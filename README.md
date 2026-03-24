# 🌐 WebBuddy MCP — AI-Powered Website RAG Assistant

WebBuddy MCP is an end-to-end **Retrieval-Augmented Generation (RAG)** system that crawls websites, processes content, builds a vector index, and enables intelligent question-answering using local LLMs via MCP (Model Context Protocol).

---

## 🚀 Features

* 🔎 **Automated Web Crawling** using sitemap-based scraping
* 🧠 **RAG Pipeline** (Chunking + Embeddings + FAISS Index)
* 🤖 **LLM Integration** via Ollama (local models like LLaMA3, Mistral)
* ⚡ **MCP Server समर्थन** (Claude Desktop / MCP clients compatible)
* 🔁 **Auto Pipeline Trigger** (builds index if missing)
* 📦 Modular and scalable architecture

---

## 🏗️ Project Architecture

```
WebBuddy_MCP/
│
├── mcp_server.py          # MCP server (tools: run_pipeline, ask)
├── crawler/
│   └── fetch_data.py     # Scrapy spider + sitemap crawler
├── data/
│   └── data.py           # Chunking, embedding, FAISS index
├── LLM/
│   └── main.py           # Retrieval + Ollama LLM logic
├── /tmp/
│   ├── output.csv        # Raw crawled data
│   ├── chunks.csv        # Processed chunks
│   └── faiss.index       # Vector index
```

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/WebBuddy_MCP.git
cd WebBuddy_MCP
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Install & Run Ollama

Install Ollama and start it:

```bash
ollama serve
```

Pull a model:

```bash
ollama pull llama3
```

---

## 🔧 Configuration (MCP)

Add this config to your MCP client (Claude Desktop):

```json
{
  "mcpServers": {
    "WebBuddy": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

---

## 🧪 Usage

### ▶️ Start MCP Server

```bash
python mcp_server.py
```

---

### 🛠️ Available Tools

#### 1. `run_pipeline`

Crawls and builds knowledge base:

```json
{
  "url": "https://example.com"
}
```

---

#### 2. `ask_website_question`

Ask questions from the crawled website:

```json
{
  "query": "What does this website offer?",
  "url": "https://example.com",
  "top_k": 5
}
```

---

## 🔄 Pipeline Workflow

1. 🌐 Crawl website via sitemap
2. 📄 Store raw content → `output.csv`
3. ✂️ Chunk text data
4. 🔢 Generate embeddings
5. 🧠 Build FAISS index
6. 🔍 Retrieve relevant chunks
7. 🤖 Generate answer via LLM

---

## 🧠 LLM Configuration

In `LLM/main.py`:

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"
```

### Recommended Models

| Model          | Use Case                  |
| -------------- | ------------------------- |
| `llama3`       | Fast + reliable           |
| `mistral`      | Balanced                  |
| `mixtral`      | Better reasoning          |
| `gpt-oss:120b` | Heavy (requires high GPU) |

---

## ⚠️ Known Limitations

* Large models (120B) require high-end hardware
* Some websites may block scraping
* Sitemap-based crawling may miss dynamic pages
* No multi-site indexing (yet)

---

## 🚀 Future Improvements

* ✅ Multi-website support
* ✅ Smart caching (avoid re-crawling)
* ✅ Async pipeline execution
* ✅ Hybrid LLM (Ollama + Claude API)
* ✅ UI dashboard

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Built by **A B**
AI Intern | ML • DL • GenAI • Systems

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
