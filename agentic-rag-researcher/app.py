import gradio as gr
import os
from dotenv import load_dotenv

# AI & RAG
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

load_dotenv()

app_agent = None

def process_pdf(pdf_file):
    global app_agent
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    if not groq_key or not tavily_key:
        return "❌ Error: API keys missing in .env (GROQ_API_KEY and TAVILY_API_KEY)"

    try:
        # 1. Load and Split PDF
        loader = PyPDFLoader(pdf_file.name)
        docs = loader.load()

        # Fix 1 - Larger chunks for better context
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " "]
        )
        splits = text_splitter.split_documents(docs)

        # 2. LOCAL EMBEDDINGS
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # 3. LOCAL FAISS VECTOR STORE
        vectorstore = FAISS.from_documents(splits, embeddings)

        # Fix 2 - Better retriever with top 8 chunks
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 8}
        )

        # Fix 3 - Stronger RAG tool description
        rag_tool = create_retriever_tool(
            retriever,
            "pdf_search",
            "ALWAYS use this tool FIRST for ANY question about the document, paper, study, or authors. Only use web search for current events or external information not found in the PDF."
        )
        search_tool = TavilySearchResults(max_results=2, tavily_api_key=tavily_key)

        # 4. INITIALIZE BRAIN (Llama 3 via Groq)
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=groq_key,
            temperature=0
        )

        # Fix 4 - Strict system prompt
        system_prompt = """You are a research assistant with access to a PDF document and web search.

Follow these rules strictly:
1. For ANY question about the document, paper, study, or authors, ALWAYS use pdf_search tool FIRST
2. If pdf_search returns relevant results, answer ONLY from those results
3. If pdf_search returns nothing relevant, respond with 'This information is not found in the document'
4. ONLY use web search for questions about current events, recent news, or external tools not mentioned in the PDF
5. NEVER mix PDF content with web content in the same answer
6. NEVER answer from memory — always use a tool"""

        # 5. Create Agent
        app_agent = create_react_agent(llm, [rag_tool, search_tool], prompt=system_prompt)
        return "✅ Agent Ready with Llama 3 (Groq)! Ask your questions."

    except Exception as e:
        return f"❌ Setup Error: {str(e)}"


def chat(message, history):
    global app_agent
    if app_agent is None: return "Upload a PDF first."

    try:
        inputs = {"messages": [("human", message)]}
        result = app_agent.invoke(inputs)
        return result["messages"][-1].content
    except Exception as e:
        return f"⚠️ Chat Error: {str(e)}"


# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🚀 Professional Agentic Researcher")
    gr.Markdown("Local Data Processing + **Llama 3 (Groq)** Reasoning + Web Search")

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload PDF")
            status = gr.Textbox(label="Status", interactive=False)
            file_input.change(fn=process_pdf, inputs=file_input, outputs=status)
        with gr.Column(scale=2):
            gr.ChatInterface(fn=chat, title="Chat with Research Agent")

if __name__ == "__main__":
    demo.launch(share=True)