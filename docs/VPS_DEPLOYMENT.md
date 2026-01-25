# VPS Deployment Guide (Ubuntu)

This guide shows how to deploy the StudduoAI FastAPI backend on an Ubuntu VPS with Nginx, systemd, and SSL.

## 1) Choose a VPS Size
- Dev/small: 2 vCPU, 4 GB RAM, 20 GB SSD
- Standard prod: 4 vCPU, 8 GB RAM, 30+ GB SSD

## 2) Prepare the Server (Ubuntu 22.04+)
```bash
# Update base system
sudo apt update && sudo apt -y upgrade

# Install runtime deps
sudo apt -y install python3 python3-venv python3-pip git

# PDF/OCR deps (required by pdf2image + Tesseract)
sudo apt -y install tesseract-ocr poppler-utils libjpeg-dev zlib1g-dev

# Web + SSL
sudo apt -y install nginx
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Optional: firewall (UFW)
sudo apt -y install ufw
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 3) Create App User and Paths
```bash
# Create a dedicated user
sudo adduser --system --group --home /opt/studduoai studduoai

# Create directories (code, data, secrets)
sudo mkdir -p /opt/studduoai/app
sudo mkdir -p /var/data/studduoai/chroma_db
sudo mkdir -p /etc/studduoai

# Allow ownership to the app user
sudo chown -R studduoai:studduoai /opt/studduoai /var/data/studduoai
```

## 4) Fetch Code and Set Up Python
```bash
# As root or your admin user
cd /opt/studduoai/app
sudo -u studduoai git clone https://your.git.repo.url.git .

# Create venv and install deps
sudo -u studduoai python3 -m venv venv
sudo -u studduoai /opt/studduoai/app/venv/bin/pip install --upgrade pip
sudo -u studduoai /opt/studduoai/app/venv/bin/pip install -r requirements.txt

# Create needed folders
sudo -u studduoai mkdir -p knowledge chroma_db
```

## 5) Configure Environment & Secrets
Place your Firebase credentials JSON at:
```bash
sudo cp /path/to/firebase-credentials.json /etc/studduoai/firebase-credentials.json
sudo chown studduoai:studduoai /etc/studduoai/firebase-credentials.json
sudo chmod 600 /etc/studduoai/firebase-credentials.json
```

Create an `.env` file in `/opt/studduoai/app`:
```bash
sudo -u studduoai tee /opt/studduoai/app/.env > /dev/null << 'EOF'
APP_ENV=production
API_PORT=8000
ALLOWED_ORIGINS=https://your-frontend.example

GOOGLE_API_KEY=YOUR_GEMINI_KEY
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_CREDENTIALS_PATH=/etc/studduoai/firebase-credentials.json

# Linux Tesseract path
TESSERACT_CMD=/usr/bin/tesseract

# Paths (persist chroma on disk)
CHROMA_PERSIST_DIR=/var/data/studduoai/chroma_db
KNOWLEDGE_DIR=/opt/studduoai/app/knowledge

MODEL_NAME=gemini-pro
TEMPERATURE=0.7
MAX_TOKENS=8192
EOF
```

## 6) (Optional) Ingest Documents
If you already have PDFs in `knowledge/`, ingest them:
```bash
cd /opt/studduoai/app
sudo -u studduoai /opt/studduoai/app/venv/bin/python ingest_documents.py
```

## 7) Test Locally
```bash
cd /opt/studduoai/app
sudo -u studduoai /opt/studduoai/app/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
# Visit http://SERVER_IP:8000/api/health
```

## 8) Create a systemd Service
Create `/etc/systemd/system/studduoai.service`:
```bash
sudo tee /etc/systemd/system/studduoai.service > /dev/null << 'EOF'
[Unit]
Description=StudduoAI FastAPI Service
After=network.target

[Service]
User=studduoai
Group=studduoai
WorkingDirectory=/opt/studduoai/app
EnvironmentFile=/opt/studduoai/app/.env
ExecStart=/opt/studduoai/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable studduoai
sudo systemctl start studduoai
sudo systemctl status studduoai --no-pager
```

## 9) Set Up Nginx Reverse Proxy
Create `/etc/nginx/sites-available/studduoai`:
```bash
sudo tee /etc/nginx/sites-available/studduoai > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-api.example;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/studduoai /etc/nginx/sites-enabled/studduoai
sudo nginx -t
sudo systemctl restart nginx
```

## 10) Enable HTTPS with Certbot
```bash
sudo certbot --nginx -d your-api.example
# Auto-renew cron is installed by certbot; verify with:
sudo systemctl list-timers | grep certbot
```

## 11) Health Checks & CORS
- Backend health: `https://your-api.example/api/health`
- Update `ALLOWED_ORIGINS` in `.env` to your frontend URL(s)

## 12) Persistence & Backups
- ChromaDB persists at `/var/data/studduoai/chroma_db`
- Keep `knowledge/` under `/opt/studduoai/app/knowledge`
- Back up `/etc/studduoai/firebase-credentials.json` safely

## 13) Routine Operations
```bash
# Logs
journalctl -u studduoai -f

# Restart after code updates
sudo systemctl restart studduoai

# Update code
cd /opt/studduoai/app && sudo -u studduoai git pull && sudo systemctl restart studduoai
```

## Notes
- Ensure outbound internet access for Firebase Admin and Gemini API.
- For higher throughput, raise `--workers` to match CPU cores.
- If ingestion is heavy, run it off-hours or via a separate job.
