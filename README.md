<div align="center">

# LangGraph Chatbot

**A production-style multi-tool AI assistant** built with LangGraph, Mistral AI, and Streamlit — featuring RAG, per-session persistent memory, native tool calling, and a live settings panel.

![CI](https://github.com/niravrupapara/ChatBot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Framework](https://img.shields.io/badge/framework-LangGraph-orange)
![LLM](https://img.shields.io/badge/LLM-Mistral%20AI-purple)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## Overview

This project is a full-stack AI chatbot that goes beyond a simple prompt-and-response wrapper. It is built around a **LangGraph state machine** that orchestrates the LLM, tool calls, and memory in parallel — with a Streamlit front-end that makes the whole thing feel like a real product.

The goal was to design and ship a system that reflects how a chatbot might actually be built inside a company: config-driven, structured logging, session isolation, retrieval-augmented, memory-aware, and testable.

---

## Features

- **LangGraph state machine** — parallel execution of the reasoning agent and long-term memory extractor.
- **Native Mistral tool calling** — 4 built-in tools (web search, calculator, stock prices, RAG search) with an iterative tool-use loop.
- **Per-session RAG** — upload PDFs, chunk and embed with FAISS + `all-MiniLM-L6-v2`, in-memory index cache for low-latency queries.
- **Two-tier memory** — short-term conversation summarization + long-term fact extraction persisted to SQLite via a custom `SqliteStore`.
- **Multi-session UI** — sidebar chat sessions with LLM-generated titles, full SQLite chat history, resume anywhere.
- **Live settings panel** — override model, temperature, max tokens, memory window, and RAG top-k at runtime without a restart.
- **Tool call indicator** — visual feedback in the chat when the agent invokes a tool.
- **MLOps hygiene** — YAML config, structured logging via a single `get_logger` factory, ruff-linted, CI on every push.

---

## Architecture

```
                  ┌───────────────┐
User message ───▶ │   LangGraph   │ ───▶ Response
                  │   StateGraph  │
                  └───────┬───────┘
                          │
              ┌───────────┴────────────┐
              ▼                        ▼
      ┌───────────────┐        ┌──────────────────┐
      │  agent_node   │        │  remember_node   │
      │ Mistral +     │        │ Long-term memory │
      │ tool loop     │        │ fact extractor   │
      └───────┬───────┘        └────────┬─────────┘
              │                         │
              ▼                         ▼
      ┌───────────────┐        ┌──────────────────┐
      │ web_search    │        │  SqliteStore     │
      │ calculator    │        │  (facts by       │
      │ stock_price   │        │   session_id)    │
      │ rag_search    │        └──────────────────┘
      └───────────────┘

Checkpoints + long-term facts persisted to data/chat_history.db
```

The `agent` and `remember` nodes run **in parallel** — the memory extractor's latency is hidden behind the model call.

---

## Tech Stack

| Layer          | Technology                                          |
|----------------|-----------------------------------------------------|
| LLM            | Mistral AI (`mistral-small-latest`) via native SDK  |
| Orchestration  | LangGraph (StateGraph + SqliteSaver checkpoints)    |
| UI             | Streamlit                                           |
| Vector store   | FAISS + `sentence-transformers/all-MiniLM-L6-v2`    |
| Persistence    | SQLite (chats, checkpoints, long-term facts)        |
| Tools          | DuckDuckGo Search, `numexpr`, `yfinance`, RAG       |
| Tooling / CI   | Ruff, GitHub Actions                                |

---

## Project Structure

```
chatbot_new/
├── configs/config.yaml         # Model, memory, RAG, logging config
├── data/                       # SQLite DB + FAISS indexes (gitignored)
├── main.py                     # CLI entry point
├── src/
│   ├── agents/tools/           # web_search, calculator, stock, rag_search
│   ├── graph/
│   │   ├── builder.py          # StateGraph + SqliteSaver + SqliteStore
│   │   └── nodes/
│   │       ├── agent.py        # Mistral tool-calling loop
│   │       └── remember.py     # Long-term memory extractor
│   ├── memory/long_term.py     # SqliteStore + fact extractor
│   ├── rag/embeddings.py       # FAISS embeddings + in-memory cache
│   ├── session/manager.py      # Session CRUD + LLM title generation
│   └── utils/                  # Logger + runtime_config overrides
├── ui/
│   ├── app.py                  # Streamlit entry point
│   ├── pages/settings.py       # Runtime config sliders
│   └── components/             # Sidebar, chat window, file upload
├── .github/workflows/ci.yml    # Lint + import smoke test
└── pyproject.toml              # Ruff config
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- A Mistral AI API key ([get one here](https://console.mistral.ai))

### 1. Clone and install

```bash
git clone https://github.com/niravrupapara/ChatBot.git
cd ChatBot
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_key_here
```

### 3. Run the app

**Streamlit UI** (recommended):

```bash
streamlit run ui/app.py
```

**CLI mode:**

```bash
python main.py
```

---

## Configuration

All runtime knobs live in `configs/config.yaml`:

```yaml
model:
  name: "mistral-small-latest"
  temperature: 0.7
  max_tokens: 1024

memory:
  summary_threshold: 20    # summarize after N messages
  window_size: 6           # keep last N messages verbatim

rag:
  chunk_size: 500
  chunk_overlap: 50
  embedding_model: "all-MiniLM-L6-v2"
  top_k: 3
```

You can also override these live from the **Settings** page in the UI without editing config or restarting.

---

## Agent Tools

The agent decides autonomously which tool to call for each query:

| Tool               | Purpose                                                    |
|--------------------|------------------------------------------------------------|
| `web_search`       | DuckDuckGo web search for current information              |
| `calculator`       | Safe math evaluation via `numexpr`                         |
| `get_stock_price`  | Live stock quotes via `yfinance`                           |
| `rag_search`       | Retrieve chunks from the current session's uploaded PDFs   |

The tool-calling loop runs until the model returns a final answer with no more tool requests.

---

## RAG (Retrieval-Augmented Generation)

1. User uploads a PDF via the Streamlit sidebar.
2. Document is chunked (500-token chunks with 50-token overlap).
3. Chunks are embedded with `all-MiniLM-L6-v2` and stored in a **per-session FAISS index**.
4. The FAISS index + chunks are cached in-memory after first load for near-instant retrieval on subsequent queries.
5. The agent calls `rag_search` when relevant, retrieves the top-k chunks, and grounds its answer.

---

## Memory System

**Two-tier design** — inspired by how humans remember conversations.

- **Short-term:** the last N messages (configurable) are kept verbatim; older context is summarized on the fly.
- **Long-term:** the `remember_node` runs in parallel with each turn and extracts durable facts about the user (preferences, background, ongoing projects) into a per-session key-value store (`SqliteStore`).

Long-term facts are retrieved and injected as system context on every future turn — the bot actually remembers you across sessions.

---

## Development

### Lint

```bash
ruff check .
```

### CI

Every push and PR to `main` runs:

1. `ruff check .` — static analysis
2. Import smoke test — verifies the graph builds without errors

See `.github/workflows/ci.yml`.

---

## Roadmap

- [ ] Streaming responses (`st.write_stream`)
- [ ] Dockerized deployment
- [ ] MCP tool integration
- [ ] Live tool-call status indicator (`st.status`)
- [ ] Unit test suite

---

## License

MIT — see [LICENSE](LICENSE).
