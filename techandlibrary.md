# 🛠️ Tech Stack & Library Specifications

This document outlines the complete set of tools, libraries, and APIs required to implement the AI Tech Intelligence Platform.

---

## 🏗️ Backend (FastAPI & Agents)

### Core Frameworks
*   **FastAPI**: High-performance web framework for the main API.
*   **Uvicorn**: ASGI server for running FastAPI.
*   **LangGraph**: For building stateful, multi-agent workflows with cycles.
*   **LangChain**: Core abstraction layer for LLMs and vector stores.

### Database & Storage Drivers
*   **Motor**: Asynchronous Python driver for **MongoDB**.
*   **ChromaDB**: Vector database client for semantic search.
*   **Redis-py / aioredis**: For caching and as a broker for task queues.
*   **Beanie**: (Optional) Object Document Mapper (ODM) for MongoDB to provide type safety.

### AI & LLM Clients
*   **Google Generative AI (SDK)**: For direct access to **Gemini 1.5 Pro / Flash**.
*   **LangChain-Google-GenAI**: Integration library for using Gemini within LangChain/LangGraph.
*   **Sentence-Transformers**: For local embedding generation (if not using Gemini embeddings).

### Task Queue & Scheduling
*   **Celery**: For handling heavy background scraping and analysis jobs.
*   **Flower**: Monitoring tool for Celery tasks.

### Utilities
*   **Pydantic v2**: For data validation and settings management.
*   **HTTPX**: Asynchronous HTTP client for API requests.
*   **BeautifulSoup4 / Playwright**: For scraping news sites and technical blogs.
*   **PyJWT**: For authentication and secure dashboard access.
*   **Python-dotenv**: For environment variable management.

---

## 🎨 Frontend (React & UI)

### Core Frameworks
*   **React (Vite)**: Fast, modern frontend builds.
*   **TypeScript**: Ensuring type safety across the UI.

### State Management & Data Fetching
*   **TanStack Query (React Query)**: For caching, synchronization, and updating server state.
*   **Zustand**: Lightweight state management for UI-specific states (e.g., sidebar toggles).

### Styling & Components
*   **Tailwind CSS**: Utility-first CSS framework.
*   **Shadcn/ui**: High-quality, accessible UI components (Radix UI based).
*   **Lucide React**: For consistent, modern iconography.
*   **Framer Motion**: For smooth transitions and agent status animations.

### Visualization
*   **Recharts**: For trend visualization and popularity graphs.
*   **React-Markdown**: For rendering the AI-generated summaries and insights.

---

## 🔌 External APIs & Integrations

### Data Sources
*   **GitHub GraphQL API**: For high-efficiency repository discovery and star-tracking.
*   **NewsAPI / RSS Feeds**: For gathering industry news and blog posts.
*   **ArXiv API**: For tracking new research papers in the AI space.

### Notifications & Communication
*   **Telegram Bot API**: For sending daily digests and real-time alerts.

### Monitoring & Quality
*   **LangSmith**: For debugging, testing, and evaluating agent traces and prompts.
*   **Helicone / LiteLLM**: For tracking token usage and cost management.

---

## 🚢 DevOps & Infrastructure
*   **Docker & Docker Compose**: Containerization of all services (FastAPI, Mongo, Redis, Chroma).
*   **Nginx**: Reverse proxy and SSL management.
*   **GitHub Actions**: For CI/CD pipelines.

---

## 🧪 Testing
*   **Pytest**: Backend unit and integration testing.
*   **Vitest**: Frontend unit testing.
*   **Playwright**: End-to-end testing for the full pipeline.
