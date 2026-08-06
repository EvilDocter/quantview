# QuantView 24/7 Self-Hosted Deployment Guide (RHEL 9.7 GPU Server)

Hosting QuantView directly on your server (**`10.250.101.68` / Red Hat Enterprise Linux 9.7**) is **faster, 100% free, and significantly more powerful** than Render.

---

## Why Hosting on Your Server Beats Render

1. **Zero Cloud Costs**: Unlimited CPU & memory usage on your 64-core AMD EPYC server.
2. **Native GPU Ollama Speed**: Direct zero-latency access to `http://localhost:11434` (`qwen2.5:14b`).
3. **Local Qdrant Vector DB**: High-performance local HNSW vector index stored on your 3.6 TB SSD (`/mnt/workspace/mahant/quantview_secured`).
4. **Direct Nightly Scraper**: Background filing bot runs 24/7 at 2:00 AM IST without cloud timeouts or memory caps.

---

## 1-Command Production Setup (Systemd Services)

Run the following setup on your server to create background Systemd services that automatically start QuantView when the server reboots:

### Step 1: Create Backend Systemd Service

Save this file as `/etc/systemd/system/quantview-backend.service`:

```ini
[Unit]
Description=QuantView Backend Service (FastAPI + RAG + Nightly Bot)
After=network.target

[Service]
User=mahant
WorkingDirectory=/mnt/workspace/mahant/quantview_secured/backend-india
ExecStart=/mnt/workspace/mahant/quantview_secured/backend-india/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5
Environment=APP_ENV=production
Environment=FRONTEND_URL=http://localhost:3000

[Install]
WantedBy=multi-user.target
```

### Step 2: Create Frontend Systemd Service

Save this file as `/etc/systemd/system/quantview-frontend.service`:

```ini
[Unit]
Description=QuantView Frontend Service (Next.js)
After=network.target

[Service]
User=mahant
WorkingDirectory=/mnt/workspace/mahant/quantview_secured/frontend
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=5
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
```

### Step 3: Enable & Start Services 24/7

Run these commands in your server terminal:

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Build Next.js frontend for production
cd /mnt/workspace/mahant/quantview_secured/frontend
npm run build

# Enable & start services to run 24/7
sudo systemctl enable --now quantview-backend
sudo systemctl enable --now quantview-frontend
```

---

## Alternative Setup: Using PM2 (No Sudo Required)

If you do not have `sudo` access, you can run QuantView 24/7 using `pm2`:

```bash
# 1. Install PM2 globally
npm install -g pm2

# 2. Start Backend Service
cd /mnt/workspace/mahant/quantview_secured/backend-india
pm2 start "./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4" --name quantview-backend

# 3. Start Frontend Service
cd /mnt/workspace/mahant/quantview_secured/frontend
npm run build
pm2 start "npm start" --name quantview-frontend

# 4. Save state so PM2 restarts on reboot
pm2 save
```

---

## Public Internet Access (Optional)

If you want to access your server dashboard from anywhere outside your intranet:

1. **Cloudflare Tunnel (Free & Instant)**:
   ```bash
   cloudflared tunnel --url http://localhost:3000
   ```
2. **Nginx Reverse Proxy**: Route `quantview.yourdomain.com` $\rightarrow$ `http://localhost:3000`.
