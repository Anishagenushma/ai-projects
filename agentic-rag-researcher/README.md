# 🚀 Professional Agentic Researcher

An AI-powered research assistant that combines **local PDF processing** with **web search** capabilities using Llama 3 (via Groq), LangChain, and Gradio.

---

## 📌 Features

- 📄 Upload any PDF and chat with it instantly
- 🔍 Smart RAG (Retrieval-Augmented Generation) using FAISS vector store
- 🌐 Web search integration via Tavily for current/external information
- 🤖 Powered by Llama 3.3 70B via Groq (fast & free)
- 🧠 Agentic behavior — automatically decides whether to search PDF or web
- 🏠 100% local embeddings — no data sent to OpenAI

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM | Llama 3.3 70B (via Groq) |
| Embeddings | HuggingFace all-MiniLM-L6-v2 (local) |
| Vector Store | FAISS (local) |
| RAG Framework | LangChain + LangGraph |
| Web Search | Tavily API |
| UI | Gradio |

---

## 📁 Project Structure

```
agentic-rag-researcher/
│
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env                # API keys (not committed to git)
├── simple.py           # Streamlit test file
└── list_models.py      # Google model listing utility
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/agentic-rag-researcher.git
cd agentic-rag-researcher
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 5. Run the app
```bash
python app.py
```

Then open your browser at `http://localhost:7860`

---

## 🔑 Getting API Keys

| Service | URL | Cost |
|---|---|---|
| Groq | https://console.groq.com | Free |
| Tavily | https://tavily.com | Free tier available |

---

## 🚀 How to Use

1. Run `python app.py` in your terminal
2. Open `http://localhost:7860` in your browser
3. Upload a PDF file using the left panel
4. Wait for **"✅ Agent Ready"** status message
5. Start asking questions in the chat!

---

## 💡 How the Agent Works

```
User Question
      │
      ▼
 Is it about the PDF?
      │
   Yes ──► pdf_search tool ──► Answer from PDF
      │
   No  ──► Tavily web search ──► Answer from web
```

The agent automatically decides which tool to use based on your question:
- **PDF questions** → searches the uploaded document first
- **Current events / external info** → uses Tavily web search
- **Mixed questions** → uses both tools and combines the answer

---

## ⚠️ Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError: langchain.tools.retriever` | Use `from langchain_core.tools.retriever import create_retriever_tool` |
| `search_tool is not defined` | Make sure `TavilySearchResults` line is inside `process_pdf()` function |
| `HTTP 404: No interface is running` | Run `python app.py` again in terminal |
| Wrong answers from PDF | Be specific in questions — mention names, table numbers, or exact terms |

---

## 📝 Tips for Better Results

- ✅ Ask specific questions mentioning names or terms from the document
- ✅ Reference table numbers or figure numbers when asking about data
- ✅ For web questions, mention "current", "latest", or "2025"
- ❌ Avoid vague questions like "what are the results?" — be specific

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [Groq](https://groq.com) for fast LLM inference
- [LangChain](https://langchain.com) for the RAG framework
- [Tavily](https://tavily.com) for web search API
- [Gradio](https://gradio.app) for the UI
- [HuggingFace](https://huggingface.co) for local embeddings
