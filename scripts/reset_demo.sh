#!/bin/bash
# GOATCRD Demo Reset Script
# Reset database to clean seed state

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔄 GOATCRD Demo Reset"
echo "====================="
echo ""

cd "$PROJECT_ROOT/backend"

echo "📋 Running seed script..."
PYTHONPATH=. python scripts/seed_demo.py

echo ""
echo "✅ Demo data reset complete!"
echo ""
echo "Demo Credentials:"
echo "  Email: demo@goatcrd.com"
echo "  Password: demo123"
echo ""
echo "Admin Credentials:"
echo "  Email: admin@goatcrd.com"
echo "  Password: admin123"
