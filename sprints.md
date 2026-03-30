# 🚀 Project Roadmap & Sprint Plan

This roadmap divides the AI Tech Intelligence Platform into 5 functional sprints. Each sprint concludes with a working increment (MVP) of the system.

---

## 🏃 Sprint 1: The Pulse (Foundation & Collection)
**Goal:** Establish the core backend and the ability to fetch and store raw data.

### Tasks:
*   **Infrastructure:** Setup FastAPI project structure, MongoDB (Metadata), and Redis (Cache/Task Queue).
*   **Collector Agents:** Implement the GitHub Agent (GraphQL) and News Agent (RSS/Scraping).
*   **Orchestrator:** Create a basic LangGraph workflow to trigger collectors on a schedule.
*   **Storage:** Implement the `raw_data` collection in MongoDB to archive all fetches.

**MVP 1 Output:** A CLI or API endpoint that, when triggered, fetches "MCP" and "Agent Framework" data from GitHub/News and saves it to a database.

---

## 🏃 Sprint 2: The Memory (Intelligence & RAG)
**Goal:** Integrate Gemini for synthesis and ChromaDB for semantic deduplication.

### Tasks:
*   **LLM Integration:** Connect **Gemini 1.5 Flash** for initial data cleaning and filtering.
*   **Vector DB:** Setup **ChromaDB** and implement the Memory Agent.
*   **RAG Logic:** Create a deduplication layer that checks ChromaDB before processing new items.
*   **Summarizer:** Build the first version of the Summarization Agent to create structured JSON reports.

**MVP 2 Output:** The system now fetches data, ignores duplicates based on semantic meaning, and generates a structured technical summary for each new item.

---

## 🏃 Sprint 3: The Digest (Analysis & Delivery)
**Goal:** Add high-level analysis and a notification layer.

### Tasks:
*   **Trend Agent:** Implement logic to cluster similar new items and detect emerging "patterns."
*   **Evaluator Agent:** Add a **Gemini 1.5 Pro** "Critic" step to verify summary accuracy.
*   **Notification Agent:** Build the Telegram Bot integration to push daily summaries.
*   **Verification:** Implement automated "Refine" loops if the Evaluator rejects a summary.

**MVP 3 Output:** An autonomous system that sends a "Daily AI Intel" digest to a Telegram channel with verified, high-quality insights.

---

## 🏃 Sprint 4: The Control (UI & HITL)
**Goal:** Provide a visual interface and a Human-in-the-Loop approval system.

### Tasks:
*   **Frontend Setup:** Initialize React + Vite + Tailwind + Shadcn/ui.
*   **Dashboard:** Build a view to browse past insights and active trends.
*   **HITL Panel:** Create an "Admin Review" queue where summaries can be edited or approved before being sent to Telegram.
*   **Charts:** Integrate Recharts to visualize tech popularity and repository growth.

**MVP 4 Output:** A web-based dashboard where you can review, edit, and approve the AI’s findings before they are broadcast.

---

## 🏃 Sprint 5: The Expert (Scale & Multi-Modal)
**Goal:** Final polishing, vision capabilities, and production deployment.

### Tasks:
*   **Vision Integration:** Enable Gemini to analyze architecture diagrams found in GitHub READMEs.
*   **Knowledge Graph:** (Optional) Setup Neo4j to track relationships between different AI frameworks.
*   **DevOps:** Dockerize the entire stack (FastAPI, React, Mongo, Redis, Chroma).
*   **Optimization:** Implement LangSmith for monitoring and cost-tracking.

**Final Product:** A production-grade intelligence platform that "sees" architecture, tracks the AI graph, and delivers curated technical intelligence daily.
