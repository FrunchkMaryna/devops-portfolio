#!/bin/bash
set -euo pipefail

# Конфіг (краще зберігати як env змінні або в .env)
TELEGRAM_TOKEN="${TELEGRAM_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
CPU_THRESHOLD="${CPU_THRESHOLD:-85}"   # в процентах
RAM_THRESHOLD="${RAM_THRESHOLD:-85}"
DISK_THRESHOLD="${DISK_THRESHOLD:-90}"
SLEEP_SECONDS="${SLEEP_SECONDS:-60}"   # інтервал в секундах, якщо хочеш цикл

if [ -z "$TELEGRAM_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
  echo "ERROR: TELEGRAM_TOKEN або TELEGRAM_CHAT_ID не встановлені" >&2
  exit 1
fi

# отримати значення (краще запускати у Linux / WSL)
CPU_USAGE=$(top -bn1 | awk '/Cpu\(s\)/{print 100 - $8}')
RAM_USAGE=$(free | awk '/Mem/{printf("%.0f", $3/$2 * 100)}')
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')

ALERT=""
[ "$(printf '%.0f' "$CPU_USAGE")" -ge "$CPU_THRESHOLD" ] && ALERT+="⚠️ CPU: ${CPU_USAGE}%\n"
[ "$RAM_USAGE" -ge "$RAM_THRESHOLD" ] && ALERT+="⚠️ RAM: ${RAM_USAGE}%\n"
[ "$DISK_USAGE" -ge "$DISK_THRESHOLD" ] && ALERT+="⚠️ DISK: ${DISK_USAGE}%\n"

if [ -n "$ALERT" ]; then
  TEXT="🚨 *System alert*\nRepository: $(basename "$(pwd)")\n$ALERT\nHost: $(hostname)\nTime: $(date -u +"%Y-%m-%d %H:%M:%SZ")"
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d chat_id="${TELEGRAM_CHAT_ID}" \
    -d parse_mode=Markdown \
    -d text="$TEXT" >/dev/null || echo "Failed to send telegram alert" >&2
else
  echo "System OK: CPU ${CPU_USAGE}% RAM ${RAM_USAGE}% DISK ${DISK_USAGE}%"
fi
