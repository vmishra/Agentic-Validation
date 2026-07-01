#!/usr/bin/env bash
#
# Aegis — dev control script.
#   ./app.sh start      install deps if needed, start backend + frontend (background)
#   ./app.sh stop       stop both
#   ./app.sh restart    stop then start
#   ./app.sh status      is it running?
#   ./app.sh logs        tail the combined log
#
# Ports are overridable:  AEGIS_FE_PORT=3000 AEGIS_BE_PORT=9000 ./app.sh start
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

FE_PORT="${AEGIS_FE_PORT:-5176}"
BE_PORT="${AEGIS_BE_PORT:-8791}"
export AEGIS_BE_PORT="$BE_PORT"   # the Vite dev proxy reads this to reach the backend
PID_FILE="$ROOT/.app.pid"
LOG_FILE="$ROOT/.app.log"
PY="$ROOT/.venv/bin/python"

ensure_env() {
  if [ ! -f .env ]; then
    cp .env.example .env
    echo "→ created .env from .env.example"
  fi
  if ! grep -q '^GEMINI_API_KEY=..*' .env 2>/dev/null; then
    echo "⚠  No GEMINI_API_KEY set in .env."
    echo "   Get a free key at https://aistudio.google.com/apikey and add it to .env."
    echo "   (The app still starts; scans need a key — a key-less run returns the static index only.)"
  fi
}

ensure_backend() {
  if [ ! -x "$PY" ]; then
    echo "→ creating .venv and installing backend deps (first run)…"
    python3 -m venv .venv
    "$PY" -m pip install -q --upgrade pip
    "$PY" -m pip install -q -r backend/requirements.txt
  fi
}

ensure_frontend() {
  [ -d node_modules ] || { echo "→ installing frontend deps (npm install)…"; npm install; }
}

free_port() {
  local p="$1" pids
  pids="$(lsof -ti tcp:"$p" 2>/dev/null || true)"
  [ -n "$pids" ] && kill $pids 2>/dev/null || true
  return 0
}

start() {
  ensure_env; ensure_backend; ensure_frontend
  free_port "$BE_PORT"; free_port "$FE_PORT"
  echo "→ starting backend :$BE_PORT · frontend :$FE_PORT"
  : > "$LOG_FILE"
  # nohup + disown so the servers survive after this script (and its caller) exit
  nohup bash -c "cd '$ROOT/backend' && exec '$PY' -m uvicorn server:app --host 127.0.0.1 --port $BE_PORT" >>"$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"; disown 2>/dev/null || true
  nohup bash -c "cd '$ROOT' && exec npm run dev -- --port $FE_PORT" >>"$LOG_FILE" 2>&1 &
  echo $! >> "$PID_FILE"; disown 2>/dev/null || true
  sleep 3
  echo "✓ Aegis up — open http://localhost:$FE_PORT   (logs: ./app.sh logs · stop: ./app.sh stop)"
}

stop() {
  if [ -f "$PID_FILE" ]; then
    while read -r pid; do kill "$pid" 2>/dev/null || true; done < "$PID_FILE"
  fi
  free_port "$BE_PORT"; free_port "$FE_PORT"; rm -f "$PID_FILE"
  echo "✓ stopped"
}

case "${1:-start}" in
  start) start ;;
  stop) stop ;;
  restart) stop; start ;;
  status) if [ -f "$PID_FILE" ]; then echo "✓ running — http://localhost:$FE_PORT"; else echo "✗ not running"; fi ;;
  logs) touch "$LOG_FILE"; tail -f "$LOG_FILE" ;;
  *) echo "usage: ./app.sh {start|stop|restart|status|logs}"; exit 1 ;;
esac
