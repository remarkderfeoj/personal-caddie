#!/bin/bash
# Quick script to view Personal Caddie progress on your phone

echo "📱 Personal Caddie - View on Phone"
echo "=================================="
echo ""

# Detect OS and get IP
if [[ "$OSTYPE" == "darwin"* ]]; then
    IP=$(ipconfig getifaddr en0)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    IP=$(hostname -I | awk '{print $1}')
else
    echo "⚠️  OS not detected. Manually find your IP address."
    IP="YOUR_IP_HERE"
fi

echo "🖥️  Your computer's IP: $IP"
echo ""

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "❌ Backend API is NOT running"
    echo ""
    echo "Start it with:"
    echo "  cd backend && python3 main.py"
    echo ""
    exit 1
fi

# Start frontend server
echo ""
echo "🚀 Starting mobile dashboard server..."
echo ""

cd "$(dirname "$0")/frontend"

echo "================================================"
echo ""
echo "📱 Open this URL on your phone:"
echo ""
echo "   http://$IP:8080/progress.html"
echo ""
echo "================================================"
echo ""
echo "Make sure your phone is on the same WiFi network!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m http.server 8080
