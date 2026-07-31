<div align="center">

# 🤖 LangGraph Multi-Tool AI Assistant & REST Service

**An enterprise-grade, multi-tool AI Agent system** built with LangGraph, Mistral AI, Streamlit, and FastAPI — featuring per-session RAG, two-tier persistent memory, native tool calling, fast single-pass title generation, and Docker containerization.

[![Docker Image](https://img.shields.io/badge/docker-niravrupapara%2Fchatbot-blue?style=for-the-badge&logo=docker)](https://hub.docker.com/r/niravrupapara/chatbot)
![Python](https://img.shields.io/badge/python-3.11%2B-blue?style=for-the-badge&logo=python)
![Framework](https://img.shields.io/badge/framework-LangGraph-orange?style=for-the-badge)
![LLM](https://img.shields.io/badge/LLM-Mistral%20AI-purple?style=for-the-badge)
![Frontend](https://img.shields.io/badge/UI-Streamlit-red?style=for-the-badge&logo=streamlit)
![API](https://img.shields.io/badge/API-FastAPI-green?style=for-the-badge&logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

</div>

---

## 📌 Executive Summary

This repository contains an AI Agent application engineered around a **LangGraph State Machine**. Moving beyond basic prompt wrappers, this platform orchestrates reasoning, parallel long-term memory extraction, native tool execution, document retrieval, and single-pass LLM session titling in a modular, containerized pipeline.

The project supports **two execution environments**:
1. **Interactive Streamlit UI**: Direct low-latency graph execution with per-session chat history and fast automatic titling.
2. **Standalone FastAPI REST Service (`src/api/`)**: Built-in REST endpoints (`/health` & `/api/v1/chat`) for web service integration.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  SYSTEM ARCHITECTURE                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘

       ┌────────────────────────────────────────────────────────────────────────┐
       │                        📱 CLIENT & INTERFACE LAYER                     │
       │  ┌────────────────────────────────┐  ┌──────────────────────────────┐  │
       │  │   Streamlit Web App (Port 8501)│  │  FastAPI REST Service (8000) │  │
       │  └────────────────────────────────┘  └──────────────────────────────┘  │
       └───────────────────────────────────┬────────────────────────────────────┘
                                           │ Invokes State Machine
                                           ▼
       ┌────────────────────────────────────────────────────────────────────────┐
       │                   🧠 LANGGRAPH AGENTIC STATE ENGINE                    │
       │  ┌──────────────────────────────────────────────────────────────────┐  │
       │  │                  StateGraph Checkpointer (thread_id)             │  │
       │  └────────────────────────────────┬─────────────────────────────────┘  │
       │                                   │                                    │
       │              ┌────────────────────┴────────────────────┐               │
       │              ▼                                         ▼               │
       │  ┌─────────────────────────┐             ┌──────────────────────────┐  │
       │  │       agent_node        │             │      remember_node       │  │
       │  │  Mistral Reasoning      │             │   Parallel Long-Term     │  │
       │  │    + Iterative Tool Loop│             │   Fact Extractor         │  │
       │  └───────────┬─────────────┘             └───────────┬────────────┘  │
       └──────────────│─────────────────────────────────────────│───────────────┘
                      │ Executes Tools                          │ Persists Facts
                      ▼                                         ▼
       ┌──────────────────────────────┐             ┌───────────────────────────┐
       │      🛠️ AUTONOMOUS TOOLS      │             │     💾 PERSISTENCE LAYER  │
       │  • web_search (DuckDuckGo)   │             │  • 🗄️ SQLite Database     │
       │  • calculator (NumExpr)      │             │    (data/chat_history.db) │
       │  • get_stock_price (yFinance)│             │  • 📊 FAISS Vector Index  │
       │  • rag_search (FAISS PDF)    │             │    (data/vector_store/)   │
       └──────────────────────────────┘             └───────────────────────────┘
```

---

## 📁 Repository Structure

```
📁 ChatBot/
├── 📂 .github/workflows/
│   └── 📄 ci.yml                       # GitHub Actions CI pipeline (Ruff linter + Smoke import test)
├── 📂 configs/
│   └── 📄 config.yaml                  # System parameters (LLM model, temperature, memory window, RAG top-k)
├── 📂 data/                            # Persistent data storage (Git ignored)
│   ├── 📄 chat_history.db              # SQLite DB (Chat history, checkpoints, SqliteStore long-term facts)
│   └── 📂 vector_store/                # FAISS vector indices (.index and .pkl files per chat session)
├── 📂 src/                             # Backend application source code
│   ├── 📂 agents/tools/                # Autonomous agent tools
│   │   ├── 📄 calculator.py            # Math evaluation tool via NumExpr
│   │   ├── 📄 rag_search.py            # Session document retriever tool
│   │   ├── 📄 stock.py                 # Live stock market quotes via yFinance
│   │   └── 📄 web_search.py            # Real-time web search via DuckDuckGo
│   ├── 📂 api/                         # Standalone FastAPI REST service package
│   │   ├── 📄 main.py                  # FastAPI application entry point & CORS configuration
│   │   ├── 📄 routes.py                # REST endpoints (GET /health, POST /api/v1/chat)
│   │   └── 📄 schemas.py               # Pydantic request & response data models
│   ├── 📂 db/                          # Database persistence layer
│   │   ├── 📄 connection.py            # SQLite connection manager & table migrations
│   │   └── 📂 repositories/            # SQLite CRUD repositories for sessions & memories
│   ├── 📂 graph/                       # LangGraph state machine orchestrator
│   │   ├── 📄 builder.py               # StateGraph compilation with SqliteSaver & SqliteStore
│   │   ├── 📄 state.py                 # ChatState definition (messages + summary state)
│   │   └── 📂 nodes/                   # Parallel execution nodes
│   │       ├── 📄 agent.py             # Reasoning agent node & iterative tool execution loop
│   │       └── 📄 remember.py          # Parallel long-term memory user fact extractor
│   ├── 📂 memory/                      # Two-tier cognitive memory subsystem
│   │   ├── 📄 long_term.py             # SqliteStore fact extraction & profile persistence
│   │   └── 📄 short_term.py            # Window-based conversation summarizer
│   ├── 📂 rag/                         # Document retrieval-augmented generation engine
│   │   ├── 📄 embeddings.py            # SentenceTransformers (all-MiniLM-L6-v2) & FAISS cache
│   │   └── 📄 ingestion.py             # PDF text parsing, chunking, & vector index creation
│   ├── 📂 services/                    # Core business logic services
│   │   ├── 📄 document_service.py      # PDF document processing & storage coordinator
│   │   └── 📄 session_service.py       # Session CRUD & single-pass fast LLM title generator (~0.3s)
│   └── 📂 utils/                       # Shared utility modules
│       ├── 📄 config_loader.py         # Centralized YAML configuration parser
│       ├── 📄 logger.py                # Centralized structured logger factory (get_logger)
│       ├── 📄 runtime_config.py        # Dynamic runtime configuration overrides
│       └── 📄 llm_client.py            # Mistral AI SDK client initializer
├── 📂 ui/                              # Streamlit frontend web application
│   ├── 📂 components/                  # Reusable Streamlit UI components
│   │   ├── 📄 chat_window.py           # Message stream & tool execution indicators
│   │   ├── 📄 file_upload.py           # PDF uploader sidebar component
│   │   └── 📄 sidebar.py               # Multi-session chat history navigation
│   ├── 📂 pages/                       # Multi-page views
│   │   └── 📄 settings.py              # Settings panel for live runtime config sliders
│   └── 📄 app.py                       # Streamlit web application main entry point
├── 📄 Dockerfile                       # Production Docker container blueprint (CPU PyTorch + PYTHONPATH)
├── 📄 .dockerignore                    # Exclude rules for Docker build context
├── 📄 pyproject.toml                   # Python project configuration & Ruff linter settings
└── 📄 requirements.txt                 # Production dependency manifest
```

---

## ✨ Core Features & Capabilities

- **⚡ LangGraph State Machine**: Parallel execution of `agent_node` (reasoning & tool loop) and `remember_node` (long-term memory fact extractor).
- **🛠️ Native Tool Loop**: 4 built-in tools (`web_search`, `calculator`, `get_stock_price`, `rag_search`) with an iterative tool-use loop up to 10 iterations.
- **🏷️ Fast Single-Pass LLM Titling**: Generates concise 3-4 word chat session titles via Mistral AI (`max_tokens=10`, `temperature=0.2`) on the first conversation turn, updating SQLite instantly in ~0.3s without extra UI re-renders or page flickers.
- **📄 Session-Isolated RAG Engine**: Upload PDFs per session, embed with `sentence-transformers/all-MiniLM-L6-v2`, and search using per-session FAISS vector indices.
- **🧠 Two-Tier Memory System**:
  - **Short-Term Memory**: Automatic window summarization of conversation history when threshold (20 messages) is reached.
  - **Long-Term Memory**: Durable user facts (name, preferences, tech stack) extracted in parallel and persisted to SQLite via `SqliteStore`.
- **📱 Multi-Session Streamlit Web UI**: Sidebar chat session management with full SQLite chat history persistence.
- **🌐 Standalone REST API (`src/api/`)**: Production FastAPI service (`GET /health` & `POST /api/v1/chat`) with OpenAPI Swagger docs (`/docs`).
- **🐳 Docker Containerization**: Pre-built image published on Docker Hub (`niravrupapara/chatbot:latest`) with CPU-optimized PyTorch.

---

## 🚀 Quickstart & Execution Guide

Choose one of the **two methods** below to run the application:

### Method 1: Docker Run (Recommended — Zero Local Python Setup Needed)

Testing the app via Docker requires **2 simple steps**:

#### Step 1: Pull the Docker Image
```bash
docker pull niravrupapara/chatbot:latest
```

#### Step 2: Run the Container
```bash
docker run -p 8501:8501 -e MISTRAL_API_KEY="your_actual_mistral_api_key_here" niravrupapara/chatbot:latest
```
👉 Open browser at: **`http://localhost:8501`**

*(Local build alternative: `docker build -t chatbot:latest .` then `docker run -p 8501:8501 -e MISTRAL_API_KEY="..." chatbot:latest`)*

---

### Method 2: Local Python Setup (Git Clone)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/niravrupapara/ChatBot.git
   cd ChatBot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the project root:
   ```env
   MISTRAL_API_KEY=your_actual_mistral_api_key_here
   ```

4. **Launch Application**:
   - **Streamlit Web UI**:
     ```bash
     streamlit run ui/app.py
     ```
     👉 Open browser at: **`http://localhost:8501`**

   - **FastAPI REST Service (Optional)**:
     ```bash
     uvicorn src.api.main:app --reload
     ```
     👉 Open Swagger UI docs at: **`http://localhost:8000/docs`**

---

## 📡 REST API & Microservice Package (`src/api/`)

The repository includes a production REST API built with **FastAPI** and **Pydantic** for web service integrations.

### API Endpoints:
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | API health check & system status |
| `/api/v1/chat` | `POST` | Process chat prompt, invoke LangGraph state engine, and return response |

👉 **Interactive OpenAPI Swagger Documentation**: Start Uvicorn and navigate to `http://localhost:8000/docs` to test endpoints interactively in your browser.

---

## ⚙️ Configuration & Control Knobs

All runtime parameters are centralized in `configs/config.yaml`:

```yaml
model:
  name: "mistral-small-latest"
  temperature: 0.7
  max_tokens: 1024

memory:
  summary_threshold: 20    # Summarize conversation after N messages
  window_size: 6           # Retain last N messages verbatim

rag:
  chunk_size: 500          # PDF token chunk size
  chunk_overlap: 50        # Token overlap between chunks
  embedding_model: "all-MiniLM-L6-v2"
  top_k: 3                 # Number of context chunks retrieved
```

*Note: Parameters can also be overridden dynamically at runtime from the **Settings** page in the Streamlit UI without restarting the application.*

---

## 🧪 Testing & CI/CD Pipeline

The codebase maintains strict MLOps hygiene with automated quality checks:

- **Static Code Linting**: Fast syntax and code analysis enforced via **Ruff**:
  ```bash
  ruff check .
  ```
- **Automated GitHub Actions CI**: Every push to `main` triggers `.github/workflows/ci.yml`, running Ruff analysis and an import smoke test to verify graph compilation.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
