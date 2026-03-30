# 🏗️ AI Tech Intelligence Platform – Enhanced Architecture

## 🎯 Objective
A production-grade, multi-agent intelligence system that autonomously tracks, synthesizes, and verifies insights from the AI ecosystem (MCP, RAG, Agentic Frameworks).

---

## 🧩 Advanced System Architecture

```text
[User (React UI / Telegram)] <---> [Orchestrator Agent (FastAPI)]
                                            |
[Admin (Human)] <---> [HITL Panel] <--------+---- [Notification Agent (Telegram)]
                         ^                  |
                         |          [Agentic Pipeline (LangGraph)]
                         |          +------------------------------------------+
                         |          | [GitHub Agent]  &  [News Agent]          |
                         |          | (Collectors)       (Collectors)          |
                         |          +------------------+-----------------------+
                         |                             | (Raw Data)
                         |                  [Filter & Ranking Agent]
                         |                             | (Cleaned Data)
                         |                  [Memory Agent (Hybrid RAG)]
                         |                             | (Context)
                         |                  [Trend Detection Agent]
                         |                             | (Insights)
                         |                  [Summarization Agent]
                         |                             | (Draft)
                         |                  [Evaluator / Critic Agent]
                         +-----------------------------+ (Verified)

[Infrastructure & Storage Layer]
+------------------------------------------------------------------------------+
| [Redis (Cache)] | [MongoDB (Metadata)] | [ChromaDB (Vector)] | [Neo4j (Graph)] |
+------------------------------------------------------------------------------+
```

---

## 🛠️ Technology Stack (Updated)

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | FastAPI | Main API & Orchestration |
| **Agent Framework** | **LangGraph** | Cycle-aware multi-agent state management |
| **Intelligence (LLM)** | **Google Gemini** | **Gemini 1.5 Pro / Flash** for analysis & RAG |
| **Primary Database** | MongoDB | Raw data, processed summaries, and keyword search |
| **Vector Database** | **ChromaDB** | Semantic search and RAG context |
| **Graph Database** | **Neo4j** | (Optional) Mapping framework dependencies & ecosystems |
| **Cache & Queue** | **Redis** | Task management (Celery) & API caching |
| **Quality Control** | **LangSmith** | Agent monitoring and prompt versioning |

---

## 🤖 Enhanced Agent Specifications

### 1. Evaluator/Critic Agent (NEW)
*   **Responsibility:** Compares the `Summarizer` output against `raw_data`.
*   **Logic:** Uses **Gemini 1.5 Pro** to score the summary for accuracy, technical depth, and conciseness. If the score is low, it triggers a "Refine" loop back to the Summarizer.

### 2. Memory Agent (Hybrid RAG)
*   **Capability:** Uses **Hybrid Search** (combining ChromaDB's vector similarity with MongoDB's text search).
*   **Context:** Pulls topically similar historical items to provide a "How it changed" perspective.

### 3. Collector Agents (Multi-Modal)
*   **Vision Support:** Uses **Gemini 1.5 Pro's** native vision capabilities to "look" at architecture diagrams in READMEs or tech blogs to extract structural insights.

### 4. Knowledge Graph Agent (Future)
*   **Logic:** Updates a graph of "Technology A" -> "Depends on" -> "Technology B".
*   **Insight:** Detects when a new framework (e.g., an MCP server) connects two previously unrelated technologies.

---

## 🚀 Key Improvements & Suggestions

### 1. Human-in-the-Loop (HITL) Workflow
The system shouldn't be 100% autonomous. The `Summarization Agent` sends a draft to a "Review Queue" in the React UI. Once an admin clicks "Approve," the insight is pushed to Telegram and the public dashboard.

### 2. Feedback Learning Loop
User "likes" or "dislikes" in the UI should be stored in MongoDB and fed back into the `Filter Agent` to adjust the weight of specific keywords or GitHub stars in the ranking algorithm.

### 3. Dynamic Prompting
Store prompts in a separate collection/service. This allows you to tweak how the "Trend Agent" works without redeploying the backend.

### 4. Cost Control Layer
Integrate a monitoring service (like Helicone or LangSmith) to track token usage per agent. The Orchestrator can "throttle" deep analysis if the daily budget is exceeded.

---

## 🔄 Execution Flow (The "Pulse")
1.  **Discovery:** Parallel fetch from GitHub/News.
2.  **Scoring:** Filter Agent ranks items; duplicates are killed.
3.  **Synthesize:** Memory Agent gathers historical context.
4.  **Refine:** Summarizer writes, Evaluator critiques, and they loop until quality is met.
5.  **Curation:** Admin reviews the "Daily Digest" in the React Dashboard.
6.  **Distribution:** Final insight is saved to DB and sent to Telegram.
