#!/usr/bin/env bash
set -euo pipefail

# Налаштування
# Встановити DISCORD_WEBHOOK як змінну середовища:
# export DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
WEBHOOK="${DISCORD_WEBHOOK:-}"
CPU_THRESHOLD="${1:-80}"   # відсотки
MEM_THRESHOLD="${2:-80}"   # відсотки
DISK_THRESHOLD="${3:-90}"  # відсотки for root /

if [[ -z "$WEBHOOK" ]]; then
  echo "ERROR: DISCORD_WEBHOOK not set"
  exit 1
fi

# Отримати CPU використання (використовує top)
cpu_line=$(top -bn1 | grep "Cpu(s)" || true)
# приклад: "Cpu(s):  5.6%us,  1.2%sy,  0.0%ni, 92.5%id, ..."
cpu_idle=$(echo "$cpu_line" | awk -F'id,' '{ split($1,parts,","); print parts[length(parts)] }' 2>/dev/null || true)
# Простіший роут: використовуємо mpstat якщо є
if command -v mpstat >/dev/null 2>&1; then
  cpu_idle=$(mpstat 1 1 | awk '/all/ {print 100-$12}')
else
  # спробуємо приблизний розрахунок:
  cpu_idle=$(echo "$cpu_line" | awk -F',' '{ for(i=1;i<=NF;i++) if($i ~ /id/) {print $i} }' | awk '{print $1+0}' || echo 0)
  cpu_idle=$(awk "BEGIN{print 100 - $cpu_idle}")
fi
cpu_usage=$(printf "%.0f" "$cpu_idle")

# RAM (в відсотках)
mem_used=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')

# Disk usage root (в відсотках)
disk_used=$(df -h / | awk 'NR==2 {gsub(/%/,"",$5); print $5}')

# Формуємо повідомлення якщо поріг перевищено
message=""
if (( cpu_usage >= CPU_THRESHOLD )); then
  message+="CPU usage high: ${cpu_usage}% (threshold ${CPU_THRESHOLD}%)\n"
fi
if (( mem_used >= MEM_THRESHOLD )); then
  message+="Memory usage high: ${mem_used}% (threshold ${MEM_THRESHOLD}%)\n"
fi
if (( disk_used >= DISK_THRESHOLD )); then
  message+="Disk usage high: ${disk_used}% (threshold ${DISK_THRESHOLD}%)\n"
fi

if [[ -n "$message" ]]; then
  payload=$(jq -nc --arg content "$(printf "%s" "$message")" '{content: $content}')
  curl -s -H "Content-Type: application/json" -X POST -d "$payload" "$WEBHOOK" >/dev/null || echo "Failed to send discord webhook"
  echo "Alert sent: $(date) - $message"
else
  echo "OK: CPU ${cpu_usage}%, MEM ${mem_used}%, DISK ${disk_used}%"
fi
