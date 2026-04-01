# AI Tech Intelligence Platform - Setup & Testing Guide

This guide outlines the required API keys, local setup instructions, and testing procedures for the AI Tech Intelligence Platform.

## 1. Required API Keys and Configuration

To fully functionalize the platform, you need to create a `.env` file in the root directory with the following keys (based on `.env.example`):

| Key | Description | Source |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Intelligence Core (LLM) | [Google AI Studio](https://aistudio.google.com/) |
| `GITHUB_TOKEN` | Fetches repositories & READMEs | [GitHub Settings (Classic PAT)](https://github.com/settings/tokens) |
| `NEWSAPI_KEY` | Fetches technical news | [NewsAPI.org](https://newsapi.org/) |
| `TELEGRAM_BOT_TOKEN`| Sends daily/admin alerts | [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Your numeric ID for alerts | [@userinfobot](https://t.me/userinfobot) |
| `MONGODB_URI` | Database connection | Default: `mongodb://localhost:27017` |
| `REDIS_URL` | Task queuing/Caching | Default: `redis://localhost:6379/0` |
| `CHROMA_DB_DIR` | Vector Store storage path | Default: `./chroma_data` |

### GitHub Token Details:
For this platform, use a **Classic PAT (Personal Access Token)** rather than a fine-grained token. This allows the `GitHub Agent` to perform broad, global searches across the entire GitHub ecosystem.

**Steps to Create:**
1. Go to **GitHub Settings** -> **Developer settings** -> **Personal access tokens** -> **Tokens (classic)**.
2. Click **Generate new token (classic)**.
3. Set the name to something like `AI-Intelligence-Platform`.
4. Select the **`public_repo`** scope (this is required to read public repository data and READMEs).
5. Generate and copy the token into your `.env` file as `GITHUB_TOKEN`.

### NewsAPI Key Details:
The NewsAPI is used by the `News Agent` to aggregate technical articles and blog posts. The free tier allows 100 requests per day, which is sufficient for this project.

**Steps to Create:**
1. Visit [newsapi.org](https://newsapi.org/).
2. Click **"Get API Key"** and register for a free account.
3. Once registered, your API key will be displayed immediately.
4. Copy the key and paste it into your `.env` file as `NEWSAPI_KEY`.

### Telegram Bot Credentials:
The platform uses Telegram to send daily digests and administrative alerts when new insights are approved.

**1. How to get the `TELEGRAM_BOT_TOKEN`:**
1. Open the Telegram app and search for the **`@BotFather`** account (it has a verified blue checkmark).
2. Start a chat and send the command `/newbot`.
3. Follow the prompts to choose a name and a username for your bot.
4. Once created, `@BotFather` will reply with a message containing your **HTTP API Token** (it looks like a long string of numbers and letters).
5. Copy this token into your `.env` file as `TELEGRAM_BOT_TOKEN`.

**2. How to get your `TELEGRAM_CHAT_ID`:**
1. Open Telegram and search for the **`@userinfobot`** account.
2. Start a chat and send any message (like `/start` or `hello`).
3. The bot will instantly reply with your account information, including a numeric **Id** (e.g., `Id: 123456789`).
4. Copy this numeric ID into your `.env` file as `TELEGRAM_CHAT_ID`.
*Note: Make sure you also start a chat with your newly created bot (from step 1) and send it a `/start` message so it has permission to message you.*

---

## 2. How to Run Locally

### Option A: Docker (Recommended)
This is the simplest way to get everything (Frontend, Backend, MongoDB, Redis, and Neo4j) running in a unified environment.

1. **Configure Environment:** Create your `.env` file in the root directory.
2. **Start Services:**
   ```bash
   docker-compose up --build -d
   ```
3. **Access Platform:**
   - **Dashboard (Frontend):** `http://localhost`
   - **Backend API (Docs):** `http://localhost/api/docs`

### Option B: Manual Development Setup
Use this if you want to modify code and see changes in real-time.

**1. Start Infrastructure:**
Spin up the required databases in the background.
```bash
docker-compose up -d mongodb redis neo4j
```

**2. Setup Backend (Python):**
It is highly recommended to use a virtual environment to keep your dependencies isolated.
```powershell
# Create the virtual environment
python -m venv venv

# Activate the environment (Windows)
.\venv\Scripts\activate

# Activate the environment (macOS/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Backend server




```

**3. Setup Frontend (React):**
Open a **new terminal window** to keep the backend running.
```bash
# Navigate to the frontend directory
cd frontend

# Install Node.js packages
npm install

# Start the Vite development server
npm run dev
```
*The Dashboard will typically be available at `http://localhost:5173`.*

---

## 3. How to Test the Application

Once the application is running, follow these steps to verify the agentic workflow:

1. **Trigger the Pipeline:**
   - Open the Dashboard and click the **"Trigger All Agents"** button.
   - *Alternative (via CLI):* Run `curl -X POST http://localhost:8000/trigger-collection`.
   - This starts the orchestrator which crawls GitHub and NewsAPI, filters data, and generates summaries.

2. **Review Results:**
   - Navigate to the **"Pending"** tab on the Dashboard. You should see insights processed by the **Summarizer Agent** and verified by the **Evaluator Agent**.

3. **Test the "Human-in-the-Loop" (HITL) Flow:**
   - Click the **Approve (Checkmark)** button on a pending insight.
   - **Validation:** This should:
     1. Update the insight status in MongoDB.
     2. Index the technical details into **ChromaDB** (Semantic Memory).
     3. Send a formatted message to your configured **Telegram** chat.

4. **Verify Semantic Memory:**
   - Trigger the collection again. If similar items are found, the **Memory Agent** should discard duplicates (85% similarity threshold), ensuring your feed stays clean.
