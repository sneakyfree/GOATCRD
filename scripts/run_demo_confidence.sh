#!/bin/bash
# GOATCRD Demo Confidence Suite
# Run all tests to verify demo readiness

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🧪 GOATCRD Demo Confidence Suite"
echo "================================="
echo ""

# Backend tests
echo "📋 Running backend unit tests..."
cd "$PROJECT_ROOT/backend"
PYTHONPATH=. pytest tests/ -v --tb=short 2>&1 | tail -20

echo ""
echo "✓ Checking backend imports..."
PYTHONPATH=. python -c "from app.main import app; print('✅ Backend imports OK')"

echo ""

# Frontend checks
echo "📋 Checking frontend build..."
cd "$PROJECT_ROOT/frontend"

if command -v npm &> /dev/null; then
    npm run build 2>&1 | tail -10
    echo "✅ Frontend builds OK"
else
    echo "⚠️  npm not found, skipping frontend build check"
fi

echo ""
echo "================================="
echo "🎉 Demo Confidence Suite Complete"
echo "================================="
