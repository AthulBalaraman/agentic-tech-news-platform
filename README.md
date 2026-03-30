# 🧠 AI Tech Intelligence Platform

A production-grade multi-agent system designed to autonomously track, analyze, and synthesize insights from the rapidly evolving AI ecosystem (MCP, RAG, Agentic Frameworks).

---

## 🔑 API Keys & Credentials Guide

To run this platform, the agents need access to various external services. Below is a step-by-step guide on how to obtain the necessary API keys for your `.env` file. Most of these services offer **generous free tiers** suitable for development and moderate production use.

### 1. Google Gemini API Key (Primary LLM)
*Used by the Summarizer, Evaluator, and Trend Detection agents for text and vision tasks.*
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click on **"Get API key"** in the left navigation menu.
4. Click **"Create API key in new project"** (or select an existing Google Cloud project).
5. Copy the generated key.
* **Cost:** Free tier available (rate limits apply).
* **Env Variable:** `GEMINI_API_KEY`

### 2. GitHub Personal Access Token
*Used by the GitHub Collector Agent to fetch repositories using the GraphQL API without hitting strict unauthenticated rate limits.*
1. Log in to [GitHub](https://github.com/).
2. Go to **Settings** > **Developer settings** (at the bottom of the left sidebar).
3. Select **Personal access tokens** > **Tokens (classic)**.
4. Click **Generate new token (classic)**.
5. Give it a descriptive name (e.g., `ai-tech-intel-agent`).
6. Select the `public_repo` scope (or `repo` if you want it to analyze private repos).
7. Scroll down and click **Generate token**. Copy it immediately (it won't be shown again).
* **Cost:** Free.
* **Env Variable:** `GITHUB_TOKEN`

### 3. Telegram Bot Token & Chat ID
*Used by the Notification Agent to send your daily "AI Intel" digests.*
**To get the Bot Token:**
1. Open Telegram and search for the **[@BotFather](https://t.me/BotFather)**.
2. Send the message `/newbot`.
3. Follow the prompts to name your bot and give it a username (must end in `bot`).
4. BotFather will reply with your HTTP API Token. Copy this.

**To get your Chat ID (where the bot will send messages):**
1. Search for your newly created bot in Telegram and send it a message (e.g., "Hello").
2. Search for **[@userinfobot](https://t.me/userinfobot)** or **[@RawDataBot](https://t.me/RawDataBot)** in Telegram and click Start.
3. It will reply with a JSON payload or text containing your `Id` (a string of numbers). Copy this.
* **Cost:** Free.
* **Env Variables:** `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

### 4. NewsAPI Key
*Used by the News Collector Agent to scrape AI industry news and blogs.*
1. Go to [NewsAPI.org](https://newsapi.org/).
2. Click **Get API Key** and register for an account.
3. Once registered, your API key will be displayed on your account dashboard.
* **Cost:** Free for developer (development phase) use.
* **Env Variable:** `NEWSAPI_KEY`

### 5. LangSmith API Key (Optional but Highly Recommended)
*Used for debugging LangGraph workflows, tracking agent reasoning, and monitoring LLM costs.*
1. Go to [Smith.langchain.com](https://smith.langchain.com/).
2. Sign up or log in.
3. Go to **Settings** (gear icon) > **API Keys**.
4. Click **Create API Key**.
* **Cost:** Developer tier (Free) available.
* **Env Variables:** `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_ENDPOINT`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`

---

## ⚙️ Environment Setup

Create a `.env` file in the root of your project and populate it with the keys you gathered above:

```env
# --- LLM Provider ---
GEMINI_API_KEY="your_google_gemini_api_key_here"

# --- Data Sources ---
GITHUB_TOKEN="ghp_your_github_personal_access_token"
NEWSAPI_KEY="your_newsapi_org_key"

# --- Notifications ---
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
TELEGRAM_CHAT_ID="your_telegram_numeric_chat_id"

# --- Observability (LangSmith) ---
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="ls__your_langsmith_api_key"
LANGCHAIN_PROJECT="ai-tech-intelligence"

# --- Infrastructure / Databases ---
# Assuming default local Docker setup
MONGODB_URI="mongodb://localhost:27017"
REDIS_URL="redis://localhost:6379/0"
CHROMA_DB_DIR="./chroma_data"
```

## 🚀 Quick Start
*(Detailed setup instructions will be added here as development progresses through the Sprints).*
