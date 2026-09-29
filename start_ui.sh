#!/bin/bash

# ==========================================
# ARES Full-Stack Startup Script
# ==========================================

echo "[*] Starting ARES Web Interface..."

# 1. Start the FastAPI backend in the background
echo "[*] Booting FastAPI Backend on Port 8000..."

# Activate the virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "[!] ERROR: Virtual environment not found at .venv/bin/activate"
    echo "[!] Please create it or check your paths."
    exit 1
fi


uvicorn api.main:app --reload --port 8000 --no-access-log &
BACKEND_PID=$!

# 2. Start the React frontend in the background
echo "[*] Booting React Frontend..."
cd ui && npm run dev &
FRONTEND_PID=$!

# 3. Handle shutdown gracefully
function cleanup {
  echo ""
  echo "[!] Ctrl+C detected. Shutting down ARES servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  echo "[*] Goodbye!"
  exit
}

# Trap Ctrl+C (SIGINT) and trigger the cleanup function
trap cleanup SIGINT

echo ""
echo "[*] All systems nominal. Servers are running!"
echo "    -> Backend API: http://127.0.0.1:8000"
echo "    -> Frontend UI: http://localhost:5173"
echo "[*] Press Ctrl+C to stop both servers."
echo "=========================================="

# Keep the script waiting so the trap can catch the Ctrl+C
wait