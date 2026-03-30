# --- Backend Build Stage ---
FROM python:3.11-slim as backend

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# --- Frontend Build Stage ---
FROM node:20-alpine as frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# --- Final Production Image ---
FROM python:3.11-slim

WORKDIR /app

# Copy backend from backend stage
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend /usr/local/bin /usr/local/bin
COPY --from=backend /app/backend ./backend

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

# Install Nginx to serve the React app and proxy to FastAPI
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Setup Nginx configuration
RUN echo " \n\
server { \n\
    listen 80; \n\
    location / { \n\
        root /app/frontend_dist; \n\
        index index.html index.htm; \n\
        try_files \$uri \$uri/ /index.html; \n\
    } \n\
    location /api/ { \n\
        proxy_pass http://127.0.0.1:8000; \n\
        proxy_set_header Host \$host; \n\
        proxy_set_header X-Real-IP \$remote_addr; \n\
    } \n\
    location /trigger-collection { \n\
        proxy_pass http://127.0.0.1:8000; \n\
    } \n\
} \n\
" > /etc/nginx/sites-available/default

# Start script
RUN echo "#!/bin/bash\nnginx\nuvicorn backend.app.main:app --host 127.0.0.1 --port 8000" > /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 80

CMD ["/app/start.sh"]
