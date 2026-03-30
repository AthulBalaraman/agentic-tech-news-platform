#!/bin/bash
# Startup script for local development

echo "Starting Backend (FastAPI)..."
cd backend
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend (Vite)..."
cd ../frontend
npm install
npm run dev -- --port 3000 &
FRONTEND_PID=$!

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

echo "Platform is running. Press Ctrl+C to stop."
wait
