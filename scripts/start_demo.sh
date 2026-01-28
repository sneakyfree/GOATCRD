#!/bin/bash
# GOATCRD Demo Startup Script
# One-command launch for investor demo

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_PORT=8847
FRONTEND_PORT=5849

echo "🐐 GOATCRD Demo Startup"
echo "========================"

# Check if ports are in use
if lsof -i :$BACKEND_PORT >/dev/null 2>&1; then
    echo "⚠️  Backend port $BACKEND_PORT already in use"
else
    echo "🚀 Starting backend on port $BACKEND_PORT..."
    cd "$PROJECT_ROOT/backend"
    PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
    BACKEND_PID=$!
    echo "   PID: $BACKEND_PID"
fi

sleep 2

if lsof -i :$FRONTEND_PORT >/dev/null 2>&1; then
    echo "⚠️  Frontend port $FRONTEND_PORT already in use"
else
    echo "🎨 Starting frontend on port $FRONTEND_PORT..."
    cd "$PROJECT_ROOT/frontend"
    npm run dev -- --port $FRONTEND_PORT --host &
    FRONTEND_PID=$!
    echo "   PID: $FRONTEND_PID"
fi

sleep 3

echo ""
echo "✅ Demo Stack Ready!"
echo "===================="
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Backend:  http://localhost:$BACKEND_PORT"
echo "API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "Demo Credentials:"
echo "  Email: demo@goatcrd.com"
echo "  Password: demo123"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait
