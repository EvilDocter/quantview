#!/bin/bash
# QuantView - Full stack launcher
set -e

echo "🔄 Stopping any existing processes..."
if [ -f /tmp/qv_tunnel_loop.pid ]; then
  echo "Stopping previous tunnel loop..."
  kill -9 $(cat /tmp/qv_tunnel_loop.pid) 2>/dev/null || true
  rm -f /tmp/qv_tunnel_loop.pid
fi
kill -9 $(lsof -t -i :8000) 2>/dev/null || true
kill -9 $(lsof -t -i :3000) 2>/dev/null || true
killall cloudflared 2>/dev/null || true
pkill -f localtunnel 2>/dev/null || true
sleep 1

echo "🚀 Starting Next.js frontend on :3000..."
cd /Users/mahant/quantview/frontend
npm run start > /tmp/qv_frontend.log 2>&1 &
FRONTEND_PID=$!
disown $FRONTEND_PID

echo "⏳ Waiting for Next.js to be ready..."
sleep 3

echo "🐍 Starting FastAPI backend on :8000 (with Next.js proxy)..."
cd /Users/mahant/quantview/backend
./venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/qv_backend.log 2>&1 &
BACKEND_PID=$!
disown $BACKEND_PID

echo "⏳ Waiting for FastAPI to be ready..."
sleep 4

echo "🌐 Starting Cloudflare Tunnel on :8000..."
cd /Users/mahant/quantview
cloudflared tunnel --url http://127.0.0.1:8000 > /tmp/qv_tunnel.log 2>&1 &
CF_PID=$!
disown $CF_PID

echo "⏳ Waiting for Cloudflare Tunnel URL..."
SECURED=false
for i in {1..20}; do
  if grep -q "https://.*trycloudflare.com" /tmp/qv_tunnel.log; then
    echo "✅ Successfully secured Cloudflare Tunnel!"
    SECURED=true
    break
  fi
  sleep 1
done

echo ""
echo "✅ All services running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -o "https://[^ ]*\.trycloudflare\.com" /tmp/qv_tunnel.log | head -1 | xargs -I{} echo "🔗 Public URL: {}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next.js PID: $FRONTEND_PID"
echo "FastAPI PID: $BACKEND_PID"
echo ""
echo "📋 Logs: /tmp/qv_frontend.log | /tmp/qv_backend.log | /tmp/qv_tunnel.log"

