#!/bin/bash

WEBHOOK_URL="https://discord.com/api/webhooks/XXXXXXXX"
CPU_THRESHOLD=80
RAM_THRESHOLD=80
DISK_THRESHOLD=90

CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
RAM_USAGE=$(free | awk '/Mem/{printf("%.0f"), $3/$2 * 100}')
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')

if (( ${CPU_USAGE%.*} > CPU_THRESHOLD )); then
  curl -H "Content-Type: application/json" -X POST -d "{\"content\":\":warning: High CPU usage: ${CPU_USAGE}%\"}" $WEBHOOK_URL
fi

if (( RAM_USAGE > RAM_THRESHOLD )); then
  curl -H "Content-Type: application/json" -X POST -d "{\"content\":\":warning: High RAM usage: ${RAM_USAGE}%\"}" $WEBHOOK_URL
fi

if (( DISK_USAGE > DISK_THRESHOLD )); then
  curl -H "Content-Type: application/json" -X POST -d "{\"content\":\":warning: Disk usage: ${DISK_USAGE}%\"}" $WEBHOOK_URL
fi
